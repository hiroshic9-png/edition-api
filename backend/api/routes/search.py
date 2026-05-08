"""Cross-domain search API route."""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.api.services.search_service import SearchService

router = APIRouter(prefix="/api/v1/search", tags=["search"])
svc = SearchService()


class SearchRequest(BaseModel):
    query: str = Field(..., description="検索クエリ (例: '大阪で飲食店を開業')")


@router.post("")
@router.post("/")
def search(body: SearchRequest):
    """全ドメインを横断検索。1回のリクエストで規制・プロトコル・カレンダー・地域・組織の全情報を返す。"""
    return svc.search(query=body.query)


@router.get("")
@router.get("/")
def search_get(q: str = ""):
    """GET版の横断検索。ブラウザからの簡易テスト用。"""
    if not q:
        return {"message": "クエリパラメータ 'q' を指定してください。例: /api/v1/search?q=飲食店+東京"}
    return svc.search(query=q)
