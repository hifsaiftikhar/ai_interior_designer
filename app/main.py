from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from app.schemas import DesignRequest, DesignPlan
from app.rag import load_catalog
from app.llm import plan_design


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading furniture catalog and embedding model...")
    load_catalog()
    print("Startup complete.")
    yield
    print("Shutting down.")


app = FastAPI(title="AI Interior Designer API", lifespan=lifespan)


@app.get("/")
def root():
    return {"status": "AI Interior Designer API is running"}


@app.get("/catalog")
def get_catalog():
    from app.rag import _catalog_df
    if _catalog_df is None:
        raise HTTPException(status_code=503, detail="Catalog not loaded yet")
    return _catalog_df[["name", "category", "style", "price_usd"]].to_dict(orient="records")


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
        raise HTTPException(status_code=500, detail=f"Design planning failed: {str(e)}")