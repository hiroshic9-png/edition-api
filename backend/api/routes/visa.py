"""Visa & Immigration API routes — Japanese visa and immigration intelligence."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.services.visa_service import search_visa, list_visa_topics

router = APIRouter(prefix="/api/v1/visa", tags=["visa-immigration"])


class VisaQueryRequest(BaseModel):
    query: str = Field(..., description="ビザ・在留資格に関する質問 (日本語/英語対応)")


@router.post("/search")
def visa_search(body: VisaQueryRequest):
    """日本のビザ・在留資格に関する知識を検索。在留資格一覧、永住権、高度人材ポイント制、経営管理ビザ、帰化等をカバー。"""
    return search_visa(body.query)


@router.get("/topics")
@router.get("/list")
def visa_topics():
    """ビザ・在留資格ドメインのトピック一覧"""
    return list_visa_topics()
