"""Real Estate API routes."""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.api.services.real_estate_service import search_real_estate, list_real_estate_topics

router = APIRouter(prefix="/api/v1/real-estate", tags=["real-estate"])

class RealEstateQueryRequest(BaseModel):
    query: str = Field(..., description="不動産・住宅に関する質問")

@router.post("/search")
def real_estate_search(body: RealEstateQueryRequest):
    """日本の不動産・住宅に関する知識を検索。"""
    return search_real_estate(body.query)

@router.get("/topics")
@router.get("/list")
def real_estate_topics():
    """不動産ドメインのトピック一覧"""
    return list_real_estate_topics()
