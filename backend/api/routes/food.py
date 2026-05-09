"""Food Culture API routes — Japanese culinary intelligence."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.services.food_service import search_food, list_food_topics

router = APIRouter(prefix="/api/v1/food", tags=["food"])


class FoodQueryRequest(BaseModel):
    query: str = Field(..., description="食文化に関する質問 (日本語/英語対応)")


@router.post("/search")
def food_search(body: FoodQueryRequest):
    """日本の食文化に関する知識を検索。食事マナー・料理分類・飲食店ガイド・アレルギー対応をカバー。"""
    return search_food(body.query)


@router.get("/topics")
@router.get("/list")
def food_topics():
    """食文化ドメインのトピック一覧"""
    return list_food_topics()
