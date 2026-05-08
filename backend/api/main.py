"""EDITION Intelligence Platform — FastAPI Application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.db.database import init_db, get_db, SessionLocal
from backend.api.models.tenant import Tenant
from backend.api.models.episode import Episode
from backend.api.models.fact import Fact
from backend.api.routes import memory, regulation, protocol, calendar, regional, organization, search, foreign_entry, travel, entertainment

app = FastAPI(
    title="EDITION Intelligence Platform",
    description="AIエージェントが日本で業務を遂行するためのインテリジェンスプラットフォーム。記憶インフラ + 規制チェック。",
    version="0.1.0",
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
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
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
