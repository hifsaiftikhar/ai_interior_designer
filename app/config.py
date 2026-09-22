import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found. Create a .env file in the project root with: "
        "GEMINI_API_KEY=your_key_here"
    )

GEMINI_MODEL = "gemini-3.5-flash"
GEMINI_FALLBACK_MODEL = "gemini-3.5-flash-lite"

SAR_TO_USD = 0.27

FURNITURE_CATALOG_PATH = "data/furniture_catalog.json"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"