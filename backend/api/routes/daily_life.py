"""Daily Life API routes — practical living in Japan."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.services.daily_life_service import search_daily_life, list_daily_life_topics

router = APIRouter(prefix="/api/v1/daily-life", tags=["daily-life"])


class DailyLifeQueryRequest(BaseModel):
    query: str = Field(..., description="日常生活に関する質問 (日本語/英語対応)")


@router.post("/search")
def daily_life_search(body: DailyLifeQueryRequest):
    """日本の日常生活に関する知識を検索。住所・郵便、ゴミ分別、公共料金、医療をカバー。"""
    return search_daily_life(body.query)


@router.get("/topics")
@router.get("/list")
def daily_life_topics():
    """日常生活ドメインのトピック一覧"""
    return list_daily_life_topics()
