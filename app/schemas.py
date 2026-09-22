from pydantic import BaseModel


class RoomAnalysis(BaseModel):
    room_type: str
    furniture: list[str]
    decor: list[str]
    colors: list[str]
    style: str
    lighting: str
    spatial_observations: list[str]


class FurnitureItem(BaseModel):
    item: str
    description: str
    action: str
    price_usd: float


class DesignPlan(BaseModel):
    design_style: str
    color_palette: list[str]
    furniture_changes: list[FurnitureItem]
    layout_changes: list[str]
    generation_prompt: str


class DesignRequest(BaseModel):
    room: RoomAnalysis
    style: str
    budget: str
    budget_num: float
    preferred_colors: list[str]