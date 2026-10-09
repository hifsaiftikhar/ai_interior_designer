# AI Interior Designer — Recommendation & Visualization Bot

An AI-powered interior design application that analyzes a room image, creates a personalized design plan, retrieves relevant furniture options, and generates a redesigned room visualization based on the user's preferences.

## Project Overview

The application combines computer vision, large language models, retrieval-augmented generation (RAG), and diffusion-based image generation in an end-to-end workflow.

Users can upload a room image, select an interior style, set a budget, choose preferred colors, and receive a design plan alongside a generated room visualization.

## Features

* **Room analysis:** Uses Qwen2-VL-2B-Instruct to analyze uploaded room images.
* **Structured design planning:** Uses Gemini to generate a structured design plan from room analysis and user preferences.
* **Furniture retrieval:** Uses a furniture catalog and semantic retrieval to ground recommendations in available items.
* **Image generation:** Uses depth estimation and a diffusion-based generation pipeline to produce a redesigned room.
* **GPU processing:** Runs vision and image-generation workloads in Google Colab.
* **Web interface:** Provides an interactive React frontend connected to a FastAPI backend.
* **Asynchronous job workflow:** Uses Google Drive to pass generation jobs and results between the local application and Colab worker.

## System Architecture

```text
User uploads room image
          |
          v
React Frontend
          |
          v
FastAPI Backend
          |
          v
Qwen2-VL Room Analysis
          |
          v
Structured RoomAnalysis
          |
          +----------------------+
          |                      |
          v                      v
   User Preferences       Furniture Catalog
          |                      |
          +----------+-----------+
                     |
                     v
             Gemini Design Planner
                     |
                     v
               DesignPlan JSON
                     |
                     v
            Generation Job in Drive
                     |
                     v
           Google Colab GPU Worker
                     |
                     v
          Depth + Diffusion Pipeline
                     |
                     v
             Generated Room Image
                     |
                     v
                Google Drive
                     |
                     v
              FastAPI Image Route
                     |
                     v
            React Displays Image
```

## Technology Stack

| Component              | Technology                                                 |
| ---------------------- | ---------------------------------------------------------- |
| Frontend               | React, Vite, JavaScript, CSS                               |
| Backend                | Python, FastAPI                                            |
| Vision-language model  | Qwen2-VL-2B-Instruct                                       |
| Design planning        | Gemini API                                                 |
| Furniture retrieval    | Python, sentence embeddings, catalog filtering             |
| Image generation       | Depth estimation, diffusion, ControlNet-based conditioning |
| GPU environment        | Google Colab                                               |
| Job and image exchange | Google Drive                                               |
| Version control        | Git and GitHub                                             |

## Application Workflow

1. The user uploads a room image and selects design preferences.
2. The vision-language model analyzes the room and returns structured room information.
3. The backend combines the room analysis with the user's style, budget, and color preferences.
4. The design planner uses the furniture catalog and retrieval results to create a structured design plan.
5. The backend creates a generation job in Google Drive.
6. The Colab worker processes the job using depth estimation and image generation.
7. The generated image is saved in Google Drive.
8. The frontend checks the job status and displays the completed visualization.

## Project Structure

```text
ai_interior_design/
├── app/
│   ├── config.py
│   ├── generation.py
│   ├── llm.py
│   ├── main.py
│   ├── rag.py
│   ├── schemas.py
│   └── vlm.py
├── data/
│   └── furniture_catalog.json
├── frontend/
│   └── src/
│       ├── components/
│       ├── styles/
│       ├── App.jsx
│       └── main.jsx
├── notebooks/
│   └── [Colab experiments and notebooks]
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Running the Application

### 1. Backend

Create and activate a Python virtual environment, install the project's dependencies, and configure the required environment variables.

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The FastAPI server runs locally at `http://127.0.0.1:8000`.

### 2. Configure services

Configure the Gemini API key and the URL for the running VLM service in your local environment. Start the VLM service in its configured environment and ensure the backend can reach it.

The Colab generation worker must also be running with Google Drive mounted and the expected job/output directories available.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

### 4. Generate a design

Upload a room image, select your preferences, and click **Generate my room**. The application submits a job, waits for generation to complete, and displays the resulting image.

## API Endpoints

| Method | Endpoint              | Purpose                                                  |
| ------ | --------------------- | -------------------------------------------------------- |
| GET    | `/`                   | API health/status message                                |
| GET    | `/catalog`            | Retrieve furniture catalog entries                       |
| POST   | `/plan`               | Generate a design plan                                   |
| POST   | `/design`             | Run the room-design workflow and create a generation job |
| GET    | `/job/{job_id}`       | Check job status and retrieve completed result data      |
| GET    | `/job/{job_id}/image` | Serve the generated room image                           |

## Current Status

* [x] Room image upload through the web interface
* [x] Vision-language room analysis
* [x] LLM-based design planning
* [x] Furniture catalog retrieval integration
* [x] Generation job creation and Drive-based exchange
* [x] Colab GPU image generation
* [x] Backend job-status tracking
* [x] Display of generated room images in the frontend
* [ ] Systematic evaluation of generated image quality
* [ ] Controlled experiments for improving room-structure preservation
* [ ] Further reliability, error-handling, and deployment improvements

## Limitations and Future Work

The current implementation is a working baseline, not a guarantee of photorealistic or structurally accurate interior redesigns.

Planned improvements include:

* Evaluate whether room structure and furniture placement are preserved.
* Measure how consistently generated images follow the selected style and colors.
* Compare generation settings using fixed input images and prompts.
* Investigate more targeted image editing and selective inpainting if baseline limitations justify it.
* Improve error handling, configuration, and deployment portability.

## Security

Store API keys in a local `.env` file and never commit secrets, private credentials, or generated personal images. Keep local paths and service URLs configurable for other environments.

## Learning Goals

This project explores the integration of vision-language models, structured LLM outputs, retrieval-grounded recommendations, diffusion-based image generation, asynchronous GPU jobs, and a full-stack AI application.
