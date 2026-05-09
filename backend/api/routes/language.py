"""Japanese Language API routes — linguistic intelligence."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.services.language_service import search_language, list_language_topics

router = APIRouter(prefix="/api/v1/language", tags=["language"])


class LanguageQueryRequest(BaseModel):
    query: str = Field(..., description="日本語に関する質問 (日本語/英語対応)")


@router.post("/search")
def language_search(body: LanguageQueryRequest):
    """日本語の構造的知識を検索。敬語・助数詞・名前構造・ビジネス日本語をカバー。"""
    return search_language(body.query)


@router.get("/topics")
@router.get("/list")
def language_topics():
    """日本語ドメインのトピック一覧"""
    return list_language_topics()
