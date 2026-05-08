"""Protocol API routes — Japanese business customs and practices."""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.api.services.protocol_service import ProtocolService

router = APIRouter(prefix="/api/v1/protocol", tags=["protocol"])
protocol_service = ProtocolService()


class ProtocolCheckRequest(BaseModel):
    query: str = Field(..., description="ビジネスプロトコルに関する質問 (日本語/英語対応)")
    category: Optional[str] = Field(None, description="プロトコルID (nemawashi, ringi, horenso, meishi, sekiji, zoto)")


@router.post("/check")
def check_protocol(body: ProtocolCheckRequest):
    """日本のビジネスプロトコル・慣習に関する情報を回答。

    根回し、稟議、報連相、名刺交換、席順、贈答の6カテゴリをカバー。
    """
    return protocol_service.check(query=body.query, category=body.category)


@router.get("/list")
def list_protocols():
    """対応ビジネスプロトコル一覧"""
    protocols = protocol_service.list_protocols()
    return {"protocols": protocols, "count": len(protocols)}


@router.get("/{protocol_id}")
def get_protocol_detail(protocol_id: str):
    """特定ビジネスプロトコルの詳細情報"""
    result = protocol_service.get_protocol(protocol_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"プロトコル '{protocol_id}' が見つかりません。/list で一覧を確認してください。",
        )
    return result
