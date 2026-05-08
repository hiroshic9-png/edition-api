"""Entertainment API routes — Japan pop culture and event intelligence."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.services.entertainment_service import (
    search_entertainment,
    list_entertainment_topics,
)

router = APIRouter(prefix="/api/v1/entertainment", tags=["entertainment"])


class EntertainmentQueryRequest(BaseModel):
    query: str = Field(..., description="エンタメに関する質問 (日本語/英語対応)")


@router.post("/search")
def entertainment_search(body: EntertainmentQueryRequest):
    """日本のエンタメ・推し活・イベントに関する知識を検索。"""
    return search_entertainment(body.query)


@router.get("/topics")
@router.get("/list")
def entertainment_topics():
    """エンタメ知識ドメインのトピック一覧"""
    return list_entertainment_topics()
