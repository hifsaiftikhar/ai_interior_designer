import json
import re
import time

from google import genai

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.schemas import RoomAnalysis, DesignPlan
from app.rag import (
    get_relevant_categories,
    retrieve_furniture_by_categories,
)

client = genai.Client(api_key=GEMINI_API_KEY)


def parse_design_plan(raw_text: str) -> DesignPlan:
    cleaned = re.sub(
        r"^```(json)?\s*|\s*```$",
        "",
        raw_text.strip(),
    )

    data = json.loads(cleaned)

    return DesignPlan(**data)


def build_design_prompt(
    room: RoomAnalysis,
    style: str,
    budget: str,
    preferred_colors: list[str],
    budget_num: float,
) -> str:

    relevant_categories = get_relevant_categories(
        room.furniture + ["wardrobe"]
    )

    retrieved = retrieve_furniture_by_categories(
        style,
        relevant_categories,
        budget_num,
    )

    lines = []

    for _, row in retrieved.iterrows():
        lines.append(
            f"- {row['name']} "
            f"({row['category']}, {row['style']}): "
            f"${row['price_usd']}"
        )

    furniture_options = "\n".join(lines)

    schema = """{
  "design_style": "string",
  "color_palette": ["color1", "color2"],
  "furniture_changes": [
    {
      "item": "exact name from available list, or not available in catalog",
      "description": "string",
      "action": "replace/add/keep",
      "price_usd": 0
    }
  ],
  "layout_changes": ["string"],
  "generation_prompt": "string describing the redesigned room for an image generation model"
}"""

    prompt = (
        "You are an interior design planner.\n\n"
        "Given a room analysis, user preferences, and a list of "
        "ACTUAL AVAILABLE furniture items, create a design plan "
        "using ONLY items from the provided list.\n\n"

        "If something is needed but not in the list, "
        "note it as 'not available in catalog' rather than "
        "inventing an item.\n\n"

        "Room analysis:\n"
        + room.model_dump_json(indent=2)
        + "\n\n"

        "User preferences:\n"
        + f"- Style: {style}\n"
        + f"- Budget: {budget}\n"
        + f"- Preferred colors: {', '.join(preferred_colors)}\n\n"

        "Available furniture:\n"
        + furniture_options
        + "\n\n"

        "Respond with ONLY a valid JSON object in exactly this format:\n\n"
        + schema
        + "\n\n"

        "Do not include markdown formatting or text outside the JSON object."
    )

    return prompt


def plan_design(room, style, budget, preferred_colors, budget_num):
    prompt = build_design_prompt(
        room, style, budget, preferred_colors, budget_num
    )

    models = [
        GEMINI_MODEL,
        "gemini-3.5-flash-lite",
    ]

    last_error = None

    for model in models:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                return parse_design_plan(response.text)

            except Exception as e:
                last_error = e
                print(
                    f"Gemini failed: model={model}, "
                    f"attempt={attempt + 1}, error={e}"
                )
                time.sleep(2 * (attempt + 1))

    raise RuntimeError(
        f"Gemini failed after retries and fallback. Last error: {last_error}"
    )