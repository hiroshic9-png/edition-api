"""Disaster & Safety API routes — Japan emergency intelligence."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.services.disaster_service import search_disaster, list_disaster_topics

router = APIRouter(prefix="/api/v1/disaster", tags=["disaster"])


class DisasterQueryRequest(BaseModel):
    query: str = Field(..., description="災害・安全に関する質問 (日本語/英語対応)")


@router.post("/search")
def disaster_search(body: DisasterQueryRequest):
    """日本の災害・安全に関する知識を検索。地震・台風・緊急連絡先・防災準備をカバー。"""
    return search_disaster(body.query)


@router.get("/topics")
@router.get("/list")
def disaster_topics():
    """災害・安全ドメインのトピック一覧"""
    return list_disaster_topics()
