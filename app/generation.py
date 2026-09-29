from pathlib import Path
import json
import shutil
import uuid


GENERATION_JOBS_DIR = Path(
    r"G:\My Drive\ai_interior_design\generation_jobs"
)


def create_generation_job(
    image_path: str,
    generation_prompt: str,
    style: str,
    budget: str,
    preferred_colors: list[str],
) -> str:

    job_id = f"job_{uuid.uuid4().hex[:8]}"

    job_dir = GENERATION_JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # Copy room image into generation job
    # --------------------------------------------------

    source_image = Path(image_path)

    if not source_image.exists():
        raise FileNotFoundError(
            f"Source image not found: {source_image}"
        )

    destination_image = job_dir / "room.png"

    shutil.copy2(
        source_image,
        destination_image
    )

    # --------------------------------------------------
    # Create job metadata
    # --------------------------------------------------

    job = {
        "job_id": job_id,
        "generation_prompt": generation_prompt,
        "style": style,
        "budget": budget,
        "preferred_colors": preferred_colors,
        "status": "queued"
    }

    with open(
        job_dir / "job.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            job,
            f,
            indent=2
        )

    print(f"Generation job created: {job_id}")
    print(f"Room image copied to: {destination_image}")

    return job_id