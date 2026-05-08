"""Calendar API routes — Japanese business calendar and seasonal awareness."""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.api.services.calendar_service import CalendarService

router = APIRouter(prefix="/api/v1/calendar", tags=["calendar"])
calendar_service = CalendarService()


class CalendarCheckRequest(BaseModel):
    query: str = Field(..., description="カレンダーに関する質問 (例: 決算期はいつ？お盆はいつ？)")
    category: Optional[str] = Field(None, description="カテゴリID (fiscal_year, public_holidays, gift_seasons, administrative_deadlines, seasonal_business)")


@router.post("/check")
def check_calendar(body: CalendarCheckRequest):
    """日本のビジネスカレンダー・季節情報を回答。"""
    return calendar_service.check(query=body.query, category=body.category)


@router.get("/list")
def list_categories():
    """対応カレンダーカテゴリ一覧"""
    categories = calendar_service.list_categories()
    return {"categories": categories, "count": len(categories)}


@router.get("/{category_id}")
def get_category_detail(category_id: str):
    """特定カレンダーカテゴリの詳細情報"""
    result = calendar_service.get_category(category_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"カテゴリ '{category_id}' が見つかりません。")
    return result
