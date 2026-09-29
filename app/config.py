import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3.5-flash"

VLM_SERVICE_URL = os.getenv("VLM_SERVICE_URL")
GENERATE_SERVICE_URL = os.getenv("GENERATE_SERVICE_URL")

SAR_TO_USD = 0.27
FURNITURE_CATALOG_PATH = "data/furniture_catalog.json"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"