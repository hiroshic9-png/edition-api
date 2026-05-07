"""Memory API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.api.db.database import get_db
from backend.api.auth.api_key import verify_api_key
from backend.api.models.tenant import Tenant
from backend.api.services.memory_service import MemoryService

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


# ── Request/Response schemas ─────────────────────────

class EpisodeCreate(BaseModel):
    content: str = Field(..., description="保存する内容")
    session_id: Optional[str] = Field(None, description="セッション識別子")
    role: str = Field("user", description="役割 (user/assistant/system)")
    metadata: dict = Field(default_factory=dict, description="追加メタデータ")
    auto_extract: bool = Field(False, description="LLMでファクトを自動抽出するか")


class EpisodeResponse(BaseModel):
    id: str
    session_id: Optional[str]
    content: str
    role: str
    metadata: dict
    event_at: str
    class Config:
        from_attributes = True


class EpisodeSearchRequest(BaseModel):
    query: str = Field(..., description="検索クエリ")
    limit: int = Field(5, ge=1, le=50)


class FactCreate(BaseModel):
    subject: str = Field(..., description="主語 (例: 佐藤部長)")
    predicate: str = Field(..., description="述語 (例: 好む)")
    object: str = Field(..., description="目的語 (例: ワイン)")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="確度")
    source_episode_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class FactResponse(BaseModel):
    id: str
    subject: str
    predicate: str
    object: str
    confidence: float
    valid_from: Optional[str]
    valid_until: Optional[str]
    metadata: dict
    class Config:
        from_attributes = True


class FactUpdate(BaseModel):
    object: Optional[str] = None
    confidence: Optional[float] = None


# ── Episode endpoints ────────────────────────────────

@router.post("/episodes")
def create_episode(
    body: EpisodeCreate,
    tenant: Tenant = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """エピソードを保存（chronicle.mdへの追記に相当）。auto_extract=trueでファクト自動抽出。"""
    svc = MemoryService(db, tenant.id)
    result = svc.store_episode(
        content=body.content,
        session_id=body.session_id,
        role=body.role,
        metadata=body.metadata,
        auto_extract=body.auto_extract,
    )
    ep = result["episode"]
    response = {
        "id": ep.id,
        "session_id": ep.session_id,
        "content": ep.content,
        "role": ep.role,
        "metadata": ep.metadata_ or {},
        "event_at": ep.event_at.isoformat() if ep.event_at else "",
    }
    if result["extracted_facts"]:
        response["extracted_facts"] = [
            {
                "id": f.id,
                "subject": f.subject,
                "predicate": f.predicate,
                "object": f.object_,
                "confidence": f.confidence,
                "metadata": f.metadata_ or {},
            }
            for f in result["extracted_facts"]
        ]
    return response


@router.get("/episodes")
def list_episodes(
    session_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tenant: Tenant = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """エピソード一覧取得"""
    svc = MemoryService(db, tenant.id)
    episodes = svc.list_episodes(session_id=session_id, limit=limit, offset=offset)
    return {
        "episodes": [
            {
                "id": ep.id,
                "session_id": ep.session_id,
                "content": ep.content,
                "role": ep.role,
                "event_at": ep.event_at.isoformat() if ep.event_at else "",
            }
            for ep in episodes
        ],
        "count": len(episodes),
    }


@router.post("/episodes/search")
def search_episodes(
    body: EpisodeSearchRequest,
    tenant: Tenant = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """エピソードをセマンティック検索"""
    svc = MemoryService(db, tenant.id)
    results = svc.search_episodes(query=body.query, limit=body.limit)
    return {"results": results, "count": len(results)}


# ── Fact endpoints ───────────────────────────────────

@router.post("/facts", response_model=FactResponse)
def create_fact(
    body: FactCreate,
    tenant: Tenant = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """ファクトを追加"""
    svc = MemoryService(db, tenant.id)
    fact = svc.add_fact(
        subject=body.subject,
        predicate=body.predicate,
        object_=body.object,
        confidence=body.confidence,
        source_episode_id=body.source_episode_id,
        metadata=body.metadata,
    )
    return FactResponse(
        id=fact.id,
        subject=fact.subject,
        predicate=fact.predicate,
        object=fact.object_,
        confidence=fact.confidence,
        valid_from=fact.valid_from.isoformat() if fact.valid_from else None,
        valid_until=fact.valid_until.isoformat() if fact.valid_until else None,
        metadata=fact.metadata_ or {},
    )


@router.get("/facts")
def list_facts(
    valid_only: bool = Query(True),
    tenant: Tenant = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """現在有効なファクト一覧"""
    svc = MemoryService(db, tenant.id)
    facts = svc.list_facts(valid_only=valid_only)
    return {
        "facts": [
            {
                "id": f.id,
                "subject": f.subject,
                "predicate": f.predicate,
                "object": f.object_,
                "confidence": f.confidence,
                "valid_from": f.valid_from.isoformat() if f.valid_from else None,
                "valid_until": f.valid_until.isoformat() if f.valid_until else None,
            }
            for f in facts
        ],
        "count": len(facts),
    }


@router.put("/facts/{fact_id}", response_model=FactResponse)
def update_fact(
    fact_id: str,
    body: FactUpdate,
    tenant: Tenant = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """ファクトを更新（旧版は自動的にinvalidateされる）"""
    svc = MemoryService(db, tenant.id)
    fact = svc.update_fact(fact_id, new_object=body.object, new_confidence=body.confidence)
    if not fact:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Fact not found")
    return FactResponse(
        id=fact.id,
        subject=fact.subject,
        predicate=fact.predicate,
        object=fact.object_,
        confidence=fact.confidence,
        valid_from=fact.valid_from.isoformat() if fact.valid_from else None,
        valid_until=fact.valid_until.isoformat() if fact.valid_until else None,
        metadata=fact.metadata_ or {},
    )


@router.delete("/facts/{fact_id}")
def delete_fact(
    fact_id: str,
    tenant: Tenant = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """ファクトを無効化"""
    svc = MemoryService(db, tenant.id)
    fact = svc.invalidate_fact(fact_id)
    if not fact:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Fact not found")
    return {"status": "invalidated", "fact_id": fact_id}


# ── Context endpoint ─────────────────────────────────

@router.get("/context")
def get_context(
    session_id: Optional[str] = Query(None),
    use_llm: bool = Query(False, description="LLMでリッチなサマリーを生成するか"),
    tenant: Tenant = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """現在のコンテキストサマリーを取得（session_state.md相当）"""
    svc = MemoryService(db, tenant.id)
    return svc.get_context(session_id=session_id, use_llm=use_llm)


# ── Extract endpoint ─────────────────────────────────

class ExtractRequest(BaseModel):
    text: str = Field(..., description="ファクトを抽出するテキスト")
    context_hint: str = Field("", description="コンテキストヒント")
    store: bool = Field(False, description="抽出したファクトを保存するか")


@router.post("/extract")
def extract_facts(
    body: ExtractRequest,
    tenant: Tenant = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """テキストからファクトを自動抽出（LLM使用）。

    日本語の文脈（敬語・主語省略・社会的階層）を分析して構造化。
    store=trueで抽出結果をファクトとして永続保存。
    """
    svc = MemoryService(db, tenant.id)

    if body.store:
        # Store as episode first, then extract
        result = svc.store_episode(
            content=body.text,
            role="system",
            metadata={"source": "manual_extraction"},
            auto_extract=True,
        )
        return {
            "extracted_facts": [
                {
                    "id": f.id,
                    "subject": f.subject,
                    "predicate": f.predicate,
                    "object": f.object_,
                    "confidence": f.confidence,
                    "metadata": f.metadata_ or {},
                }
                for f in result["extracted_facts"]
            ],
            "stored": True,
            "episode_id": result["episode"].id,
        }
    else:
        # Extract without storing
        raw_facts = svc.extract_from_text(
            text=body.text,
            context_hint=body.context_hint,
        )
        return {
            "extracted_facts": raw_facts,
            "stored": False,
        }
