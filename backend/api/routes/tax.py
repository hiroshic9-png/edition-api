"""Tax API routes — Japanese tax system intelligence."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.services.tax_service import search_tax, list_tax_topics

router = APIRouter(prefix="/api/v1/tax", tags=["tax"])


class TaxQueryRequest(BaseModel):
    query: str = Field(..., description="税金・確定申告に関する質問 (日本語/英語対応)")


@router.post("/search")
def tax_search(body: TaxQueryRequest):
    """日本の税制に関する知識を検索。所得税、消費税、法人税、源泉徴収、ふるさと納税、暗号資産税制等をカバー。"""
    return search_tax(body.query)


@router.get("/topics")
@router.get("/list")
def tax_topics():
    """税務ドメインのトピック一覧"""
    return list_tax_topics()
