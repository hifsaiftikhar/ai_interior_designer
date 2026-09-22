import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import FURNITURE_CATALOG_PATH, EMBEDDING_MODEL_NAME

CATEGORY_MAP = {
    "bed": "Beds",
    "table": "Tables & desks",
    "nightstand": "Chests of drawers & drawer units",
    "wardrobe": "Wardrobes",
    "chair": "Chairs",
    "sofa": "Sofas & armchairs",
    "bookcase": "Bookcases & shelving units",
}

_catalog_df = None
_catalog_embeddings = None
_embed_model = None


def load_catalog():
    global _catalog_df, _catalog_embeddings, _embed_model

    _catalog_df = pd.read_json(FURNITURE_CATALOG_PATH)
    _embed_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    _catalog_df["search_text"] = (
        _catalog_df["name"] + " " + _catalog_df["category"] + " " + _catalog_df["style"] + " style furniture"
    )
    _catalog_embeddings = _embed_model.encode(_catalog_df["search_text"].tolist())

    print(f"Loaded and embedded {len(_catalog_df)} furniture items")


def get_relevant_categories(furniture_list: list) -> list:
    categories = []
    for item in furniture_list:
        item_lower = item.lower()
        for key, cat in CATEGORY_MAP.items():
            if key in item_lower and cat not in categories:
                categories.append(cat)
    return categories


def retrieve_furniture_by_categories(style: str, categories: list, budget_num: float, top_k_per_category: int = 3) -> pd.DataFrame:
    if _catalog_df is None:
        raise RuntimeError("Catalog not loaded. Call load_catalog() first.")

    all_retrieved = []
    for category in categories:
        subset = _catalog_df[_catalog_df["category"] == category]
        if subset.empty:
            continue
        query_embedding = _embed_model.encode([f"{style} {category}"])
        subset_embeddings = _catalog_embeddings[subset.index]
        similarities = np.dot(subset_embeddings, query_embedding.T).flatten()
        subset = subset.copy()
        subset["similarity"] = similarities
        subset = subset[subset["price_usd"] <= budget_num].sort_values("similarity", ascending=False).head(top_k_per_category)
        all_retrieved.append(subset)

    if all_retrieved:
        return pd.concat(all_retrieved).drop_duplicates(subset=["name", "category", "price_usd"])
    return pd.DataFrame()