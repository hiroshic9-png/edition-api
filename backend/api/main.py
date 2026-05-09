"""EDITION Intelligence Platform — FastAPI Application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.db.database import init_db, get_db, SessionLocal
from backend.api.models.tenant import Tenant
from backend.api.models.episode import Episode
from backend.api.models.fact import Fact
from backend.api.routes import memory, regulation, protocol, calendar, regional, organization, search, foreign_entry, travel, entertainment

app = FastAPI(
    title="EDITION Intelligence Platform",
    description="Japan Operations OS for autonomous AI agents. Verified, structured knowledge across 10 domains: regulations, procedures, protocols, calendar, regional, organization, foreign entry, travel, entertainment, and persistent memory.",
    version="0.3.0",
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

# Routes
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
        "version": "0.3.0",
        "status": "running",
        "docs": "/docs",
        "discovery": {
            "a2a": "/.well-known/agent.json",
            "mcp": "/.well-known/mcp/server-card.json",
        },
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
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# ── Agent Discovery Endpoints ───────────────────────────────


@app.get("/.well-known/agent.json")
def agent_card():
    """A2A Agent Card — Enables autonomous agent discovery via RFC 8615.

    Any A2A-compatible agent can discover EDITION's capabilities by sending
    GET https://api.edition.sh/.well-known/agent.json
    """
    return JSONResponse(content={
        "name": "EDITION Intelligence Platform",
        "description": "Japan Operations OS for autonomous AI agents. Provides verified, structured knowledge across 10 domains essential for operating in the Japanese market: business regulations (10 industries), step-by-step procedures, business protocols (nemawashi, ringi, hourensou, meishi, seating, gift-giving), fiscal calendar & deadlines, regional differences, organizational structures (keiretsu, payment customs), foreign market entry (visa, banking, real estate), travel intelligence, entertainment & pop culture, and persistent multi-layer memory.",
        "version": "0.3.0",
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
                "description": "Semantic search across all 10 Japan knowledge domains simultaneously. A single query like 'opening a restaurant in Osaka' returns regulation requirements, regional specifics, calendar deadlines, and cultural protocols — all in one response.",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "japan-regulation-check",
                "name": "Japan Regulation & Compliance Check",
                "description": "Check industry-specific regulations, required licenses, governing bodies, penalties, costs, and timelines for operating in Japan. Covers 10 industries (food service, real estate, finance, healthcare, IT, education, construction, logistics, retail, manufacturing) plus 6 tourist regulation categories.",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "japan-business-protocol",
                "name": "Japan Business Protocol Guide",
                "description": "Structured guides for Japanese business etiquette with step-by-step instructions and expert experience tips. Protocols: nemawashi (consensus building), ringi (approval process), hourensou (reporting), meishi koukan (business card exchange), sekijun (seating hierarchy), zoutou (gift-giving).",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "japan-foreign-entry",
                "name": "Japan Market Entry Guide",
                "description": "Complete guides for foreign companies and individuals entering the Japanese market: company incorporation (KK/GK), management visa, bank account opening, real estate, tax registration. Each with step-by-step procedures and insider tips.",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "japan-calendar",
                "name": "Japan Business Calendar",
                "description": "Fiscal year cycles, national holidays, gift-giving seasons (ochugen/oseibo), administrative deadlines, and seasonal business patterns.",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "japan-travel-entertainment",
                "name": "Japan Travel & Entertainment Intelligence",
                "description": "Practical travel knowledge (shinkansen, IC cards, ryokan etiquette, tipping culture) and entertainment/pop culture guides (oshi-katsu fan culture, anime pilgrimage, live event etiquette, seasonal festivals).",
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "persistent-memory",
                "name": "Multi-Layer Persistent Memory",
                "description": "Three-layer memory architecture: Episode (conversation history with semantic search), Fact (structured subject-predicate-object triples with confidence scores), and Context (session state summaries). Supports Japanese language understanding including keigo levels and implicit subject resolution.",
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
    """MCP Server Card — Enables MCP registry discovery (Smithery, etc).

    Registries like Smithery scan this endpoint to automatically populate
    server metadata, tool listings, and capability descriptions.
    """
    return JSONResponse(content={
        "name": "edition",
        "displayName": "EDITION Intelligence Platform",
        "description": "Japan Operations OS for autonomous AI agents. 10 knowledge domains, 36 REST endpoints, 23 MCP tools. Covers regulations, procedures, protocols, calendar, regional, organization, foreign entry, travel, entertainment, and persistent memory.",
        "version": "0.3.0",
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
            {"name": "entertainment_search", "description": "Search Japan entertainment/pop culture (oshi-katsu, anime, festivals)"},
            {"name": "entertainment_list", "description": "List all entertainment topics"},
            {"name": "search", "description": "Cross-domain search across all 10 knowledge domains simultaneously"}
        ],
        "categories": ["knowledge", "japan", "business", "compliance", "travel", "culture", "memory"],
        "tags": ["japan", "business", "regulations", "compliance", "protocols", "travel", "entertainment", "memory", "knowledge-base", "agent-os"]
    })
