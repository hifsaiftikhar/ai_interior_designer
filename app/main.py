from pathlib import Path
import json
import base64
import os
import tempfile
from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import RoomAnalysis, DesignRequest, DesignPlan
from app.rag import load_catalog
from app.llm import plan_design
from app.generation import create_generation_job
from app.config import VLM_SERVICE_URL


# ============================================================
# Application startup / shutdown
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading furniture catalog and embedding model...")

    load_catalog()

    print("Startup complete.")

    yield

    print("Shutting down.")


app = FastAPI(
    title="AI Interior Designer API",
    lifespan=lifespan
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Root
# ============================================================

@app.get("/")
def root():
    return {
        "status": "AI Interior Designer API is running"
    }


# ============================================================
# Furniture catalog
# ============================================================

@app.get("/catalog")
def get_catalog():

    from app.rag import _catalog_df

    if _catalog_df is None:
        raise HTTPException(
            status_code=503,
            detail="Catalog not loaded yet"
        )

    return _catalog_df[
        ["name", "category", "style", "price_usd"]
    ].to_dict(orient="records")


# ============================================================
# Design planning only
# ============================================================

@app.post("/plan", response_model=DesignPlan)
def create_design_plan(request: DesignRequest):

    try:

        design = plan_design(
            room=request.room,
            style=request.style,
            budget=request.budget,
            preferred_colors=request.preferred_colors,
            budget_num=request.budget_num,
        )

        return design

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Design planning failed: {str(e)}"
        )


# ============================================================
# Full pipeline
#
# Room image
#     ↓
# VLM
#     ↓
# RoomAnalysis
#     ↓
# LLM + RAG
#     ↓
# DesignPlan
#     ↓
# Google Drive generation job
# ============================================================

@app.post("/design")
async def full_design_pipeline(
    file: UploadFile = File(...),
    style: str = Form(...),
    budget: str = Form(...),
    budget_num: float = Form(...),
    preferred_colors: str = Form(...)
):

    temp_path = None

    try:

        # ------------------------------------------------------
        # Read uploaded image
        # ------------------------------------------------------

        print("Reading uploaded image...")

        image_bytes = await file.read()

        if not image_bytes:

            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty."
            )


        # ------------------------------------------------------
        # Parse preferred colors
        # ------------------------------------------------------

        colors_list = [
            color.strip()
            for color in preferred_colors.split(",")
            if color.strip()
        ]

        print(
            "Preferred colors:",
            colors_list
        )


        # ------------------------------------------------------
        # STEP 1 — VLM
        # ------------------------------------------------------

        print("Calling VLM service...")

        analyze_response = requests.post(
            f"{VLM_SERVICE_URL}/analyze",
            files={
                "file": (
                    file.filename,
                    image_bytes,
                    file.content_type
                )
            },
            timeout=120
        )

        analyze_response.raise_for_status()

        room = RoomAnalysis(
            **analyze_response.json()
        )

        print("VLM analysis completed.")


        # ------------------------------------------------------
        # STEP 2 — LLM + RAG
        # ------------------------------------------------------

        print("Creating design plan...")

        design = plan_design(
            room=room,
            style=style,
            budget=budget,
            preferred_colors=colors_list,
            budget_num=budget_num,
        )

        print("Design plan created.")


        # ------------------------------------------------------
        # STEP 3 — Create temporary image file
        # ------------------------------------------------------

        with tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False
        ) as temp_file:

            temp_file.write(image_bytes)

            temp_path = temp_file.name

        print(
            "Temporary image created:",
            temp_path
        )


        # ------------------------------------------------------
        # STEP 4 — Create Google Drive generation job
        # ------------------------------------------------------

        print("Creating generation job...")

        job_id = create_generation_job(
            image_path=temp_path,
            generation_prompt=design.generation_prompt,
            style=style,
            budget=budget,
            preferred_colors=colors_list,
        )

        print(
            f"Generation job created successfully: {job_id}"
        )


        # ------------------------------------------------------
        # STEP 5 — Return pipeline result
        # ------------------------------------------------------

        return {
            "job_id": job_id,
            "generation_status": "queued",
            "room_analysis": room.model_dump(),
            "design_plan": design.model_dump()
        }


    # ----------------------------------------------------------
    # VLM / network error
    # ----------------------------------------------------------

    except requests.exceptions.RequestException as e:

        raise HTTPException(
            status_code=502,
            detail=f"VLM service call failed: {str(e)}"
        )


    # ----------------------------------------------------------
    # HTTPException — preserve original status/detail
    # ----------------------------------------------------------

    except HTTPException:

        raise


    # ----------------------------------------------------------
    # Other errors
    # ----------------------------------------------------------

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed: {str(e)}"
        )


    # ----------------------------------------------------------
    # Always remove temporary local image
    # ----------------------------------------------------------

    finally:

        if temp_path and os.path.exists(temp_path):

            try:

                os.remove(temp_path)

                print(
                    "Temporary image deleted."
                )

            except Exception as cleanup_error:

                print(
                    f"Could not delete temporary file: "
                    f"{cleanup_error}"
                )


# ============================================================
# Generation job status
# ============================================================

@app.get("/job/{job_id}")
def get_generation_job(job_id: str):

    jobs_dir = Path(
        r"G:\My Drive\ai_interior_design\generation_jobs"
    )

    output_dir = Path(
        r"G:\My Drive\ai_interior_design\generated"
    )

    job_dir = jobs_dir / job_id

    job_file = job_dir / "job.json"

    result_file = (
        output_dir /
        job_id /
        "result.png"
    )


    # --------------------------------------------------
    # Check job exists
    # --------------------------------------------------

    if not job_file.exists():

        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )


    # --------------------------------------------------
    # Read job information
    # --------------------------------------------------

    with open(
        job_file,
        "r",
        encoding="utf-8"
    ) as f:

        job = json.load(f)


    status = job.get(
        "status",
        "unknown"
    )


    # --------------------------------------------------
    # If generation is not completed
    # --------------------------------------------------

    if (
        status != "completed"
        or not result_file.exists()
    ):

        return {
            "job_id": job_id,
            "status": status,
            "result_available": False
        }


    # --------------------------------------------------
    # Read generated image
    # --------------------------------------------------

    with open(
        result_file,
        "rb"
    ) as f:

        image_base64 = base64.b64encode(
            f.read()
        ).decode("utf-8")


    # --------------------------------------------------
    # Return completed result
    # --------------------------------------------------

    return {
        "job_id": job_id,
        "status": "completed",
        "result_available": True,
        "image_base64": image_base64
    }


# ============================================================
# Serve generated image directly
# ============================================================

@app.get("/job/{job_id}/image")
def get_generation_image(job_id: str):

    output_dir = Path(
        r"G:\My Drive\ai_interior_design\generated"
    )

    result_file = (
        output_dir /
        job_id /
        "result.png"
    )


    if not result_file.exists():

        raise HTTPException(
            status_code=404,
            detail="Generated image is not available yet."
        )


    return FileResponse(
        result_file,
        media_type="image/png"
    )