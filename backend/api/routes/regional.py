"""Regional API routes."""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.api.services.regional_service import RegionalService

router = APIRouter(prefix="/api/v1/regional", tags=["regional"])
svc = RegionalService()

class RegionalCheckRequest(BaseModel):
    query: str = Field(..., description="地域に関する質問")
    category: Optional[str] = Field(None)

@router.post("/check")
def check(body: RegionalCheckRequest):
    """日本の地域差に関する情報を回答。"""
    return svc.check(query=body.query, category=body.category)

@router.get("/list")
def list_categories():
    cats = svc.list_categories()
    return {"categories": cats, "count": len(cats)}

@router.get("/{category_id}")
def get_detail(category_id: str):
    r = svc.get_category(category_id)
    if not r:
        raise HTTPException(status_code=404, detail=f"'{category_id}' が見つかりません。")
    return r
