"""Foreign entry API routes — Japan market entry for foreign companies."""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.api.services.foreign_entry_service import ForeignEntryService

router = APIRouter(prefix="/api/v1/foreign-entry", tags=["foreign-entry"])
svc = ForeignEntryService()

class EntryCheckRequest(BaseModel):
    query: str = Field(..., description="日本進出に関する質問 (例: 'ビザ取得', '法人設立')")
    category: Optional[str] = Field(None)

@router.post("/check")
def check(body: EntryCheckRequest):
    """外国企業・外国人の日本進出に関する情報を回答。"""
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
