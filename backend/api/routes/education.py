"""Education API routes."""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.api.services.education_service import search_education, list_education_topics

router = APIRouter(prefix="/api/v1/education", tags=["education"])

class EducationQueryRequest(BaseModel):
    query: str = Field(..., description="教育・留学に関する質問")

@router.post("/search")
def education_search(body: EducationQueryRequest):
    """日本の教育制度・留学に関する知識を検索。"""
    return search_education(body.query)

@router.get("/topics")
@router.get("/list")
def education_topics():
    """教育ドメインのトピック一覧"""
    return list_education_topics()
