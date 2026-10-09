from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

response = client.responses.create(
    model=OPENAI_MODEL,
    input='Return exactly: {"status": "ok"}'
)

print(response.output_text)