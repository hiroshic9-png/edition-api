"""EDITION Intelligence Platform — FastAPI Application."""
import time
import logging
import re
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.db.database import init_db, get_db, SessionLocal
from backend.api.models.tenant import Tenant
from backend.api.models.episode import Episode
from backend.api.models.fact import Fact
from backend.api.models.analytics import ApiRequestLog
from backend.api.routes import (
    memory, regulation, protocol, calendar, regional,
    organization, search, foreign_entry, travel, entertainment,
    daily_life, language, food, disaster, analytics,
)

logger = logging.getLogger(__name__)

# ── Agent Detection ─────────────────────────────────────────
AGENT_PATTERNS = [
    (r"claude", "Claude"),
    (r"anthropic", "Claude"),
    (r"openai", "OpenAI/GPT"),
    (r"gpt", "OpenAI/GPT"),
    (r"chatgpt", "OpenAI/GPT"),
    (r"cursor", "Cursor"),
    (r"copilot", "GitHub Copilot"),
    (r"gemini", "Google Gemini"),
    (r"perplexity", "Perplexity"),
    (r"langchain", "LangChain"),
    (r"autogpt", "AutoGPT"),
    (r"agentgpt", "AgentGPT"),
    (r"babyagi", "BabyAGI"),
    (r"crewai", "CrewAI"),
    (r"python-requests", "Python Requests"),
    (r"httpx", "HTTPX"),
    (r"axios", "Axios"),
    (r"node-fetch", "Node Fetch"),
    (r"go-http-client", "Go HTTP"),
]

SKIP_PATHS = {"/docs", "/redoc", "/openapi.json", "/favicon.ico", "/health"}


def detect_agent(user_agent: str) -> Optional[str]:
    """Detect AI agent from User-Agent header."""
    if not user_agent:
        return None
    ua_lower = user_agent.lower()
    for pattern, name in AGENT_PATTERNS:
        if re.search(pattern, ua_lower):
            return name
    return None


def extract_domain(path: str) -> Optional[str]:
    """Extract knowledge domain from request path."""
    match = re.match(r"/api/v1/([^/]+)", path)
    if match:
        return match.group(1).replace("-", "_")
    return None


def extract_query_text(body_bytes: bytes) -> Optional[str]:
    """Try to extract query text from request body."""
    try:
        import json
        body = json.loads(body_bytes)
        return body.get("query") or body.get("action") or body.get("q")
    except Exception:
        return None


# ── Analytics Middleware ────────────────────────────────────
class AnalyticsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip internal/docs paths
        if request.url.path in SKIP_PATHS or request.url.path.startswith("/.well-known"):
            return await call_next(request)

        start = time.time()

        # Read body for POST requests to extract query text
        query_text = None
        if request.method == "POST":
            body_bytes = await request.body()
            query_text = extract_query_text(body_bytes)

        response = await call_next(request)
        latency_ms = (time.time() - start) * 1000

        # Log asynchronously (fire-and-forget)
        try:
            user_agent = request.headers.get("user-agent", "")
            api_key = request.headers.get("authorization", "")
            if api_key.startswith("Bearer "):
                api_key = api_key[7:]

            db = SessionLocal()
            try:
                log_entry = ApiRequestLog(
                    method=request.method,
                    path=str(request.url.path),
                    query_text=query_text,
                    status_code=response.status_code,
                    latency_ms=round(latency_ms, 2),
                    user_agent=user_agent[:500] if user_agent else None,
                    agent_name=detect_agent(user_agent),
                    ip_address=request.client.host if request.client else None,
                    api_key_prefix=api_key[:8] if api_key else None,
                    domain=extract_domain(str(request.url.path)),
                )
                db.add(log_entry)
                db.commit()
            except Exception as e:
                logger.warning(f"Analytics log failed: {e}")
                db.rollback()
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Analytics middleware error: {e}")

        return response


# ── App Setup ───────────────────────────────────────────────
app = FastAPI(
    title="EDITION Intelligence Platform",
    description="Japan Operations OS for autonomous AI agents. Verified, structured knowledge across 14 domains: regulations, procedures, protocols, calendar, regional, organization, foreign entry, travel, entertainment, daily life, Japanese language, food culture, disaster & safety, and persistent memory.",
    version="0.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Analytics Middleware (after CORS so it can see the processed request)
app.add_middleware(AnalyticsMiddleware)

# Routes — Original 10 domains
app.include_router(memory.router)
app.include_router(regulation.router)
app.include_router(protocol.router)
app.include_router(calendar.router)
app.include_router(regional.router)
app.include_router(organization.router)
app.include_router(search.router)
app.include_router(foreign_entry.router)
app.include_router(travel.router)
app.include_router(entertainment.router)

# Routes — New 4 domains (Phase 3)
app.include_router(daily_life.router)
app.include_router(language.router)
app.include_router(food.router)
app.include_router(disaster.router)

# Routes — Analytics
app.include_router(analytics.router)


@app.on_event("startup")
def startup():
    """Initialize database and create default tenant for development."""
    init_db()

    # Create a default dev tenant if none exists
    db = SessionLocal()
    try:
        if db.query(Tenant).count() == 0:
            dev_tenant = Tenant(name="dev", api_key="edition_dev_key_for_testing")
            db.add(dev_tenant)
            db.commit()
            print(f"✅ Dev tenant created. API key: {dev_tenant.api_key}")
        else:
            tenant = db.query(Tenant).first()
            print(f"✅ Existing tenant found: {tenant.name} (key: {tenant.api_key})")
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "service": "EDITION Intelligence Platform",
        "version": "0.4.0",
        "status": "running",
        "docs": "/docs",
        "discovery": {
            "a2a": "/.well-known/agent.json",
            "mcp": "/.well-known/mcp/server-card.json",
        },
        "domains": 14,
        "endpoints": {
            "memory": "/api/v1/memory",
            "regulation": "/api/v1/regulation",
            "protocol": "/api/v1/protocol",
            "calendar": "/api/v1/calendar",
            "regional": "/api/v1/regional",
            "organization": "/api/v1/organization",
            "search": "/api/v1/search",
            "foreign_entry": "/api/v1/foreign-entry",
            "travel": "/api/v1/travel",
            "entertainment": "/api/v1/entertainment",
            "daily_life": "/api/v1/daily-life",
            "language": "/api/v1/language",
            "food": "/api/v1/food",
            "disaster": "/api/v1/disaster",
            "analytics": "/api/v1/analytics",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# ── Agent Discovery Endpoints ───────────────────────────────


@app.get("/.well-known/agent.json")
def agent_card():
    """A2A Agent Card — Enables autonomous agent discovery via RFC 8615."""
    return JSONResponse(content={
        "name": "EDITION Intelligence Platform",
        "description": "Japan Operations OS for autonomous AI agents. Provides verified, structured knowledge across 14 domains essential for operating in the Japanese market: business regulations (10 industries), step-by-step procedures, business protocols (nemawashi, ringi, hourensou, meishi, seating, gift-giving), fiscal calendar & deadlines, regional differences, organizational structures (keiretsu, payment customs), foreign market entry (visa, banking, real estate), travel intelligence, entertainment & pop culture, daily life (postal, garbage, utilities, healthcare), Japanese language (keigo, counters, business Japanese), food culture (etiquette, cuisine, restaurants, dietary restrictions), disaster & safety (earthquakes, typhoons, emergency contacts), and persistent multi-layer memory.",
        "version": "0.4.0",
        "url": "https://api.edition.sh",
        "provider": {
            "organization": "EDITION",
            "url": "https://edition.sh"
        },
        "capabilities": {
            "streaming": False,
            "pushNotifications": False
        },
        "skills": [
            {
                "id": "japan-cross-domain-search",
                "name": "Japan Cross-Domain Intelligence Search",
                "description": "Semantic search across all 14 Japan knowledge domains simultaneously. A single query returns regulation requirements, regional specifics, calendar deadlines, cultural protocols, language guidance, food culture, and disaster safety — all in one response.",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "japan-regulation-check",
                "name": "Japan Regulation & Compliance Check",
                "description": "Check industry-specific regulations, required licenses, governing bodies, penalties, costs, and timelines for operating in Japan. Covers 10 industries plus 6 tourist regulation categories.",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "japan-business-protocol",
                "name": "Japan Business Protocol Guide",
                "description": "Structured guides for Japanese business etiquette: nemawashi, ringi, hourensou, meishi koukan, sekijun, zoutou.",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "japan-foreign-entry",
                "name": "Japan Market Entry Guide",
                "description": "Complete guides for foreign companies entering Japan: incorporation, management visa, bank account, real estate, tax registration.",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "japan-calendar",
                "name": "Japan Business Calendar",
                "description": "Fiscal year cycles, national holidays, gift-giving seasons, administrative deadlines, and seasonal business patterns.",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "japan-travel-entertainment",
                "name": "Japan Travel & Entertainment Intelligence",
                "description": "Travel knowledge (shinkansen, IC cards, ryokan etiquette) and entertainment guides (oshi-katsu, anime pilgrimage, live events, festivals).",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "japan-daily-life",
                "name": "Japan Daily Life Guide",
                "description": "Practical knowledge for living in Japan: postal/address system, garbage sorting, utilities, healthcare system including national insurance.",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "japan-language",
                "name": "Japanese Language Intelligence",
                "description": "Structural understanding of Japanese: keigo honorific system, counter words (josushi), name/address patterns, business Japanese templates.",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "japan-food-culture",
                "name": "Japan Food Culture Guide",
                "description": "Japanese culinary intelligence: dining etiquette, cuisine classification, restaurant navigation (shokkenki, izakaya, sushi), dietary restrictions (halal, vegetarian, allergies).",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "japan-disaster-safety",
                "name": "Japan Disaster & Safety Intelligence",
                "description": "Life-critical knowledge: earthquake shindo scale & EEW alerts, typhoon warning levels, emergency contacts (110/119/118), disaster preparedness, evacuation procedures.",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "persistent-memory",
                "name": "Multi-Layer Persistent Memory",
                "description": "Three-layer memory: Episode (conversation history), Fact (structured triples), Context (session summaries). Japanese language understanding.",
                "inputModes": ["text"],
                "outputModes": ["text"]
            }
        ],
        "authentication": {
            "schemes": ["bearer"],
            "description": "Free Beta: Use API key 'edition_dev_key_for_testing' or any valid key. No registration required during beta."
        },
        "documentationUrl": "https://api.edition.sh/docs",
        "defaultInputModes": ["text"],
        "defaultOutputModes": ["text"]
    })


@app.get("/.well-known/mcp/server-card.json")
def mcp_server_card():
    """MCP Server Card — Enables MCP registry discovery."""
    return JSONResponse(content={
        "name": "edition",
        "displayName": "EDITION Intelligence Platform",
        "description": "Japan Operations OS for autonomous AI agents. 14 knowledge domains, 50+ REST endpoints, 31 MCP tools. Covers regulations, procedures, protocols, calendar, regional, organization, foreign entry, travel, entertainment, daily life, language, food culture, disaster & safety, and persistent memory.",
        "version": "0.4.0",
        "publisher": {
            "name": "EDITION",
            "url": "https://edition.sh"
        },
        "repository": "https://github.com/hiroshic9-png/edition-api",
        "homepage": "https://edition.sh",
        "documentationUrl": "https://api.edition.sh/docs",
        "license": "MIT",
        "runtime": {
            "type": "node",
            "command": "npx",
            "args": ["-y", "edition-mcp-server"]
        },
        "transports": [
            {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "edition-mcp-server"]
            }
        ],
        "tools": [
            {"name": "memory_store", "description": "Store episodes to persistent memory with Japanese language understanding"},
            {"name": "memory_recall", "description": "Semantic search across stored memories"},
            {"name": "memory_facts", "description": "List structured facts (subject-predicate-object triples)"},
            {"name": "memory_context", "description": "Get current session context summary"},
            {"name": "memory_extract", "description": "Auto-extract structured facts from text"},
            {"name": "regulation_check", "description": "Check Japan business regulations for 10 industries"},
            {"name": "regulation_industries", "description": "List all regulated industries in database"},
            {"name": "regulation_tourist", "description": "Tourist/visitor regulation categories"},
            {"name": "protocol_check", "description": "Search Japanese business protocols (nemawashi, ringi, etc)"},
            {"name": "protocol_list", "description": "List all business protocols"},
            {"name": "calendar_check", "description": "Search Japan business calendar (holidays, deadlines)"},
            {"name": "calendar_list", "description": "List all calendar categories"},
            {"name": "regional_check", "description": "Search regional business differences"},
            {"name": "regional_list", "description": "List all regional categories"},
            {"name": "organization_check", "description": "Search organizational structures and customs"},
            {"name": "organization_list", "description": "List all organization categories"},
            {"name": "foreign_entry_check", "description": "Foreign market entry guides (visa, banking, incorporation)"},
            {"name": "foreign_entry_list", "description": "List all foreign entry categories"},
            {"name": "travel_search", "description": "Search Japan travel knowledge (transport, accommodation, dining)"},
            {"name": "travel_list", "description": "List all travel topics"},
            {"name": "entertainment_search", "description": "Search Japan entertainment/pop culture"},
            {"name": "entertainment_list", "description": "List all entertainment topics"},
            {"name": "daily_life_search", "description": "Search daily life knowledge (postal, garbage, utilities, healthcare)"},
            {"name": "daily_life_list", "description": "List all daily life topics"},
            {"name": "language_search", "description": "Search Japanese language knowledge (keigo, counters, business Japanese)"},
            {"name": "language_list", "description": "List all language topics"},
            {"name": "food_search", "description": "Search food culture (etiquette, cuisine, restaurants, dietary restrictions)"},
            {"name": "food_list", "description": "List all food culture topics"},
            {"name": "disaster_search", "description": "Search disaster & safety knowledge (earthquakes, typhoons, emergency contacts)"},
            {"name": "disaster_list", "description": "List all disaster & safety topics"},
            {"name": "search", "description": "Cross-domain search across all 14 knowledge domains simultaneously"}
        ],
        "categories": ["knowledge", "japan", "business", "compliance", "travel", "culture", "memory", "safety", "language"],
        "tags": ["japan", "business", "regulations", "compliance", "protocols", "travel", "entertainment", "memory", "knowledge-base", "agent-os", "daily-life", "language", "food", "disaster", "safety"]
    })
