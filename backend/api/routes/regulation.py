"""Regulation API routes — business and tourist regulation checks."""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.api.services.regulation_service import RegulationService

router = APIRouter(prefix="/api/v1/regulation", tags=["regulation"])
regulation_service = RegulationService()


# ── Request schemas ──────────────────────────────────

class RegulationCheckRequest(BaseModel):
    action: str = Field(..., description="実行しようとしているアクション (日本語/英語対応)")
    industry: Optional[str] = Field(None, description="業種")
    entity_type: str = Field(
        "foreign_company",
        description="主体の種別 (foreign_company / domestic_company / individual / tourist)",
    )


# ── Endpoints ────────────────────────────────────────

@router.post("/check")
def check_regulation(body: RegulationCheckRequest):
    """特定のアクションに必要な日本の規制・許認可情報を回答。

    - 10業種の構造化された規制データベースから即座に回答
    - 訪日旅行者向けの規制情報にも対応
    - DBにない質問にはLLM RAGでフォールバック回答（確度は低め）
    """
    return regulation_service.check(
        action=body.action,
        industry=body.industry,
        entity_type=body.entity_type,
    )


@router.get("/industries")
def list_industries():
    """対応業種一覧（10業種）"""
    return {
        "industries": regulation_service.list_industries(),
        "count": len(regulation_service.list_industries()),
    }


@router.get("/industries/{industry}")
def get_industry_detail(industry: str):
    """特定業種の規制詳細情報"""
    result = regulation_service.get_industry_detail(industry)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"業種 '{industry}' が見つかりません。/industries で対応業種一覧を確認してください。",
        )
    return result


@router.get("/tourist")
def list_tourist_categories():
    """訪日旅行者向け規制カテゴリ一覧"""
    return {
        "categories": regulation_service.list_tourist_categories(),
        "count": len(regulation_service.list_tourist_categories()),
    }


@router.get("/tourist/{category}")
def get_tourist_detail(category: str):
    """訪日旅行者向け特定カテゴリの規制詳細"""
    result = regulation_service.get_tourist_detail(category)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"カテゴリ '{category}' が見つかりません。/tourist で一覧を確認してください。",
        )
    return result
