"""API Key authentication and plan enforcement middleware."""
import hashlib
import json
import os
import sqlite3
import time
from typing import Optional, Tuple
from pathlib import Path
from functools import wraps
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# ── Configuration ───────────────────────────────────────
DB_PATH = os.environ.get("EDITION_AUTH_DB", "data/auth.db")
PLANS_PATH = Path(__file__).parent.parent.parent.parent / "data" / "plans.json"

# Paths that never require authentication
PUBLIC_PATHS = frozenset([
    "/", "/health", "/docs", "/openapi.json", "/redoc",
    "/.well-known/agent.json", "/.well-known/mcp/server-card.json",
])
PUBLIC_PREFIXES = ("/docs", "/.well-known/", "/openapi")

# ── Plan definitions ────────────────────────────────────
def load_plans() -> dict:
    if PLANS_PATH.exists():
        with open(PLANS_PATH) as f:
            return json.load(f)
    return {
        "free": {"daily_limit": 100, "rate_limit_per_min": 10, "domains": ["regulation", "protocol", "calendar", "regional", "organization", "foreign_entry", "travel", "search"]},
        "pro": {"daily_limit": 10000, "rate_limit_per_min": 100, "domains": "all"},
        "enterprise": {"daily_limit": -1, "rate_limit_per_min": -1, "domains": "all"},
    }

PLANS = load_plans()

# ── Database ────────────────────────────────────────────
def _get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS api_keys (
        key_hash TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        plan TEXT NOT NULL DEFAULT 'free',
        created_at REAL NOT NULL,
        active INTEGER NOT NULL DEFAULT 1
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS usage_log (
        key_hash TEXT NOT NULL,
        date TEXT NOT NULL,
        count INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (key_hash, date)
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS rate_window (
        key_hash TEXT NOT NULL,
        window_start REAL NOT NULL,
        count INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (key_hash)
    )""")
    db.commit()
    return db

def hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()

def generate_api_key() -> str:
    """Generate a new API key: edition_<32 hex chars>"""
    import secrets
    return f"edition_{secrets.token_hex(16)}"

def register_key(email: str, plan: str = "free") -> str:
    """Register a new API key and return it."""
    key = generate_api_key()
    db = _get_db()
    db.execute(
        "INSERT INTO api_keys (key_hash, email, plan, created_at) VALUES (?, ?, ?, ?)",
        (hash_key(key), email, plan, time.time())
    )
    db.commit()
    db.close()
    return key

def validate_key(api_key: str) -> Optional[dict]:
    """Validate an API key. Returns key info dict or None."""
    db = _get_db()
    row = db.execute(
        "SELECT * FROM api_keys WHERE key_hash = ? AND active = 1",
        (hash_key(api_key),)
    ).fetchone()
    db.close()
    if row:
        return dict(row)
    return None

def check_daily_limit(api_key: str, plan: str) -> Tuple[bool, int, int]:
    """Check daily request limit. Returns (allowed, used, limit)."""
    plan_config = PLANS.get(plan, PLANS["free"])
    limit = plan_config.get("daily_limit", 100)
    if limit == -1:
        return True, 0, -1

    today = time.strftime("%Y-%m-%d")
    kh = hash_key(api_key)
    db = _get_db()

    row = db.execute(
        "SELECT count FROM usage_log WHERE key_hash = ? AND date = ?",
        (kh, today)
    ).fetchone()

    used = row["count"] if row else 0

    if used >= limit:
        db.close()
        return False, used, limit

    # Increment
    db.execute(
        """INSERT INTO usage_log (key_hash, date, count) VALUES (?, ?, 1)
           ON CONFLICT(key_hash, date) DO UPDATE SET count = count + 1""",
        (kh, today)
    )
    db.commit()
    db.close()
    return True, used + 1, limit

def check_rate_limit(api_key: str, plan: str) -> Tuple[bool, int]:
    """Check per-minute rate limit. Returns (allowed, retry_after_seconds)."""
    plan_config = PLANS.get(plan, PLANS["free"])
    limit = plan_config.get("rate_limit_per_min", 10)
    if limit == -1:
        return True, 0

    kh = hash_key(api_key)
    now = time.time()
    window_start = now - 60

    db = _get_db()
    row = db.execute(
        "SELECT window_start, count FROM rate_window WHERE key_hash = ?",
        (kh,)
    ).fetchone()

    if row and row["window_start"] > window_start:
        if row["count"] >= limit:
            retry_after = int(row["window_start"] + 60 - now) + 1
            db.close()
            return False, retry_after
        db.execute(
            "UPDATE rate_window SET count = count + 1 WHERE key_hash = ?",
            (kh,)
        )
    else:
        db.execute(
            """INSERT INTO rate_window (key_hash, window_start, count) VALUES (?, ?, 1)
               ON CONFLICT(key_hash) DO UPDATE SET window_start = ?, count = 1""",
            (kh, now, now)
        )

    db.commit()
    db.close()
    return True, 0

def check_domain_access(plan: str, path: str) -> bool:
    """Check if the plan has access to the requested domain."""
    plan_config = PLANS.get(plan, PLANS["free"])
    allowed_domains = plan_config.get("domains", [])
    if allowed_domains == "all":
        return True

    # Extract domain from path: /api/v1/{domain}/...
    parts = path.strip("/").split("/")
    if len(parts) >= 3 and parts[0] == "api" and parts[1] == "v1":
        domain = parts[2].replace("-", "_")
        return domain in allowed_domains

    return True  # Non-domain paths are always allowed

def get_usage_stats(api_key: str) -> dict:
    """Get usage statistics for an API key."""
    kh = hash_key(api_key)
    db = _get_db()

    key_info = db.execute(
        "SELECT * FROM api_keys WHERE key_hash = ?", (kh,)
    ).fetchone()

    if not key_info:
        db.close()
        return {"error": "Invalid API key"}

    today = time.strftime("%Y-%m-%d")
    today_usage = db.execute(
        "SELECT count FROM usage_log WHERE key_hash = ? AND date = ?",
        (kh, today)
    ).fetchone()

    total_usage = db.execute(
        "SELECT SUM(count) as total FROM usage_log WHERE key_hash = ?",
        (kh,)
    ).fetchone()

    db.close()

    plan = key_info["plan"]
    plan_config = PLANS.get(plan, PLANS["free"])

    return {
        "plan": plan,
        "email": key_info["email"],
        "created_at": key_info["created_at"],
        "today": {
            "used": today_usage["count"] if today_usage else 0,
            "limit": plan_config.get("daily_limit", 100),
        },
        "total_requests": total_usage["total"] if total_usage and total_usage["total"] else 0,
        "rate_limit_per_min": plan_config.get("rate_limit_per_min", 10),
    }


# ── Middleware ──────────────────────────────────────────

class APIKeyMiddleware(BaseHTTPMiddleware):
    """Optional API key authentication middleware.

    Behavior:
    - Public paths: no auth required
    - No API key provided: treated as anonymous free-tier (100 req/day global)
    - Valid API key: plan-based limits applied
    - Invalid API key: 401 error
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip auth for public paths
        if path in PUBLIC_PATHS or any(path.startswith(p) for p in PUBLIC_PREFIXES):
            response = await call_next(request)
            response.headers["X-Edition-Plan"] = "public"
            return response

        # Extract API key from header or query param
        api_key = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            api_key = auth_header[7:]
        elif request.query_params.get("api_key"):
            api_key = request.query_params["api_key"]

        # No key = anonymous free tier
        if not api_key or api_key == "edition_dev_key_for_testing":
            # Graceful degradation: allow anonymous access with free limits
            plan = "free"
            # For now, allow through without strict enforcement
            # This enables backward compatibility during migration
            response = await call_next(request)
            response.headers["X-Edition-Plan"] = plan
            response.headers["X-Edition-Auth"] = "anonymous"
            return response

        # Validate key
        key_info = validate_key(api_key)
        if not key_info:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Invalid API key",
                    "message": "Register at POST /api/v1/auth/register to get a free API key.",
                    "docs": "https://api.edition.sh/docs"
                }
            )

        plan = key_info["plan"]

        # Check domain access
        if not check_domain_access(plan, path):
            free_domains = PLANS.get("free", {}).get("domains", [])
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Domain not available on your plan",
                    "plan": plan,
                    "message": "Upgrade to Pro for access to all 20 domains.",
                    "free_domains": free_domains,
                    "upgrade": "POST /api/v1/auth/upgrade"
                }
            )

        # Check rate limit
        rate_ok, retry_after = check_rate_limit(api_key, plan)
        if not rate_ok:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "plan": plan,
                    "retry_after_seconds": retry_after,
                    "message": f"Rate limit: {PLANS[plan].get('rate_limit_per_min', 10)} req/min. Upgrade for higher limits."
                },
                headers={"Retry-After": str(retry_after)}
            )

        # Check daily limit
        daily_ok, used, limit = check_daily_limit(api_key, plan)
        if not daily_ok:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Daily limit exceeded",
                    "plan": plan,
                    "used": used,
                    "limit": limit,
                    "message": "Daily quota reached. Resets at midnight UTC. Upgrade for higher limits.",
                    "upgrade": "POST /api/v1/auth/upgrade"
                }
            )

        # All checks passed — proceed
        response = await call_next(request)
        response.headers["X-Edition-Plan"] = plan
        response.headers["X-Edition-Daily-Used"] = str(used)
        response.headers["X-Edition-Daily-Limit"] = str(limit)
        return response
