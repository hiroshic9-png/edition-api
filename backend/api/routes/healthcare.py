"""Healthcare API routes."""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.api.services.healthcare_service import search_healthcare, list_healthcare_topics

router = APIRouter(prefix="/api/v1/healthcare", tags=["healthcare"])

class HealthcareQueryRequest(BaseModel):
    query: str = Field(..., description="医療・健康保険に関する質問")

@router.post("/search")
def healthcare_search(body: HealthcareQueryRequest):
    """日本の医療・健康保険に関する知識を検索。"""
    return search_healthcare(body.query)

@router.get("/topics")
@router.get("/list")
def healthcare_topics():
    """医療ドメインのトピック一覧"""
    return list_healthcare_topics()
