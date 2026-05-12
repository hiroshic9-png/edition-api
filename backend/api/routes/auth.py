"""Auth API routes — API key registration and usage tracking."""
import re
from typing import List
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from backend.api.middleware.api_key import register_key, validate_key, get_usage_stats, PLANS

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: str = Field(..., description="メールアドレス（APIキー発行に必要）")


class RegisterResponse(BaseModel):
    api_key: str
    plan: str
    message: str
    daily_limit: int
    rate_limit_per_min: int
    free_domains: List[str]
    upgrade_info: str


@router.post("/register", response_model=RegisterResponse)
def auth_register(body: RegisterRequest):
    """無料APIキーを発行します。メールアドレスが必要です。"""
    email = body.email.strip().lower()

    # Basic email validation
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        raise HTTPException(status_code=400, detail="Invalid email address")

    key = register_key(email, plan="free")
    free_config = PLANS.get("free", {})

    return RegisterResponse(
        api_key=key,
        plan="free",
        message="API key created successfully. Store this key securely — it cannot be recovered.",
        daily_limit=free_config.get("daily_limit", 100),
        rate_limit_per_min=free_config.get("rate_limit_per_min", 10),
        free_domains=free_config.get("domains", []),
        upgrade_info="Contact h.sato@c-9.co.jp for Pro/Enterprise plans."
    )


@router.get("/usage")
def auth_usage(request: Request):
    """現在のAPIキーの利用状況を確認します。"""
    api_key = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        api_key = auth_header[7:]

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Pass via Authorization: Bearer <key>"
        )

    stats = get_usage_stats(api_key)
    if "error" in stats:
        raise HTTPException(status_code=401, detail=stats["error"])

    return stats


@router.get("/plans")
def auth_plans():
    """利用可能なプラン一覧を取得します。"""
    result = []
    for plan_id, config in PLANS.items():
        result.append({
            "plan": plan_id,
            "name": config.get("name", plan_id),
            "daily_limit": config.get("daily_limit", 100),
            "rate_limit_per_min": config.get("rate_limit_per_min", 10),
            "domains": config.get("domains", []),
            "price": config.get("price", config.get("price_monthly_jpy", "contact")),
        })
    return {"plans": result}
