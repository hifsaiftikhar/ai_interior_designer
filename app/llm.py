import json
import re
import time

from google import genai

from app.config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_FALLBACK_MODEL
from app.schemas import RoomAnalysis, DesignPlan
from app.rag import get_relevant_categories, retrieve_furniture_by_categories

client = genai.Client(api_key=GEMINI_API_KEY)


def parse_design_plan(raw_text: str) -> DesignPlan:
    cleaned = re.sub(r"^```(json)?\s*|\s*```$", "", raw_text.strip())
    data = json.loads(cleaned)
    return DesignPlan(**data)


def call_gemini_with_retry(prompt: str, max_retries: int = 5):
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        except Exception as e:
            print(f"[Gemini attempt {attempt + 1}/{max_retries}] {GEMINI_MODEL} failed: {e}")
            time.sleep(5 * (attempt + 1))

    print(f"[Gemini] Primary model exhausted retries, trying fallback: {GEMINI_FALLBACK_MODEL}")
    return client.models.generate_content(model=GEMINI_FALLBACK_MODEL, contents=prompt)


def build_design_prompt(room: RoomAnalysis, style: str, budget: str, preferred_colors: list[str], budget_num: float) -> str:
    relevant_categories = get_relevant_categories(room.furniture + ["wardrobe"])
    retrieved = retrieve_furniture_by_categories(style, relevant_categories, budget_num)

    lines = []
    for _, row in retrieved.iterrows():
        lines.append(f"- {row['name']} ({row['category']}, {row['style']}): ${row['price_usd']}")
    furniture_options = "\n".join(lines)

    header = (
        "You are an interior design planner. Given a room analysis, user preferences, and a list of "
        "ACTUAL AVAILABLE furniture items, create a design plan using ONLY items from the provided list. "
        "If something is needed but not in the list, note it as 'not available in catalog' rather than inventing an item."
    )

    schema = """{
  "design_style": "string",
  "color_palette": ["color1", "color2"],
  "furniture_changes": [
    {"item": "exact name from available list, or not available in catalog", "description": "string", "action": "replace/add/keep", "price_usd": 0}
  ],
  "layout_changes": ["string"],
  "generation_prompt": "string describing the redesigned room for an image generation model"
}"""

    prompt = (
        header
        + "\n\nRoom analysis:\n" + room.model_dump_json(indent=2)
        + "\n\nUser preferences:\n- Style: " + style
        + "\n- Budget: " + budget
        + "\n- Preferred colors: " + ", ".join(preferred_colors)
        + "\n\nAvailable furniture (choose only from this list):\n" + furniture_options
        + "\n\nRespond with ONLY a valid JSON object, no other text, in exactly this format:\n\n" + schema
        + "\n\nDo not include any explanation, markdown formatting, or text outside the JSON object."
    )

    return prompt


def plan_design(room: RoomAnalysis, style: str, budget: str, preferred_colors: list[str], budget_num: float) -> DesignPlan:
    prompt = build_design_prompt(room, style, budget, preferred_colors, budget_num)
    response = call_gemini_with_retry(prompt)
    return parse_design_plan(response.text)