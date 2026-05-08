"""Travel API routes — Japan inbound tourism intelligence."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.services.travel_service import search_travel, list_travel_topics

router = APIRouter(prefix="/api/v1/travel", tags=["travel"])


class TravelQueryRequest(BaseModel):
    query: str = Field(..., description="旅行に関する質問 (日本語/英語対応)")


@router.post("/search")
def travel_search(body: TravelQueryRequest):
    """訪日旅行に関する知識を検索。交通・宿泊・飲食・実用情報をカバー。"""
    return search_travel(body.query)


@router.get("/topics")
@router.get("/list")
def travel_topics():
    """旅行知識ドメインのトピック一覧"""
    return list_travel_topics()
