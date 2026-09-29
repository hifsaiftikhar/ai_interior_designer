import os
import requests
from dotenv import load_dotenv

from app.schemas import RoomAnalysis

load_dotenv()

VLM_API_URL = os.getenv("VLM_API_URL")


def analyze_room(image_path: str) -> RoomAnalysis:
    with open(image_path, "rb") as image_file:
        response = requests.post(
            VLM_API_URL,
            files={
                "file": (
                    os.path.basename(image_path),
                    image_file,
                    "image/jpeg",
                )
            },
            timeout=120,
        )

    response.raise_for_status()

    return RoomAnalysis(**response.json())