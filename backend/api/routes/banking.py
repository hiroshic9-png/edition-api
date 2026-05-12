"""Banking & Finance API routes — Japanese banking and financial services."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.services.banking_service import search_banking, list_banking_topics

router = APIRouter(prefix="/api/v1/banking", tags=["banking-finance"])


class BankingQueryRequest(BaseModel):
    query: str = Field(..., description="銀行・金融に関する質問 (日本語/英語対応)")


@router.post("/search")
def banking_search(body: BankingQueryRequest):
    """日本の銀行・金融サービスに関する知識を検索。口座開設、海外送金、モバイル決済、クレジットカード等をカバー。"""
    return search_banking(body.query)


@router.get("/topics")
@router.get("/list")
def banking_topics():
    """銀行・金融ドメインのトピック一覧"""
    return list_banking_topics()
