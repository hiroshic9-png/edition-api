"""Telemetry & Quality Gate API routes.

Phase 1 of Roadmap v2.0.
Exposes telemetry dashboards and quality gate audit endpoints.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.api.db.database import get_db
from backend.api.services.telemetry import telemetry_service
from backend.api.services.quality_gate import quality_gate

router = APIRouter(prefix="/api/v1/telemetry", tags=["telemetry"])


# ── Telemetry v1 Endpoints ─────────────────────────────────────

@router.get("/tools")
def telemetry_tools(
    period: int = Query(30, description="Period in days"),
    tool: str = Query(None, description="Filter by specific tool name"),
    db: Session = Depends(get_db),
):
    """Tool invocation dashboard — per-tool counts, latency, agents."""
    return telemetry_service.tool_invocations(db, period_days=period, tool_name=tool)


@router.get("/heatmap")
def telemetry_heatmap(
    period: int = Query(30, description="Period in days"),
    db: Session = Depends(get_db),
):
    """Domain demand heatmap — which knowledge areas are most used."""
    return telemetry_service.domain_heatmap(db, period_days=period)


@router.get("/timeseries")
def telemetry_timeseries(
    period: int = Query(30, description="Period in days"),
    db: Session = Depends(get_db),
):
    """Daily call volume time series for trend detection."""
    return telemetry_service.daily_timeseries(db, period_days=period)


@router.get("/queries")
def telemetry_queries(
    period: int = Query(30, description="Period in days"),
    limit: int = Query(20, description="Max results"),
    db: Session = Depends(get_db),
):
    """Top queries — reveals what agents actually need."""
    return telemetry_service.top_queries(db, period_days=period, limit=limit)


# ── Quality Gate Endpoints ─────────────────────────────────────

@router.get("/quality-gate")
def quality_gate_audit():
    """Full platform quality gate audit.

    Scores every KB entry and determines publish/draft/flagged/unpublished status.
    Entries below score 80 are demoted. This is the data-driven quality moat.
    """
    return quality_gate.run_full_audit()


@router.get("/quality-gate/{domain}")
def quality_gate_domain(domain: str):
    """Quality gate for a specific domain."""
    from backend.api.services.kb_loader import load_all_domains
    domains = load_all_domains()
    if domain not in domains:
        return {"error": f"Domain '{domain}' not found", "available": list(domains.keys())}
    return quality_gate.evaluate_domain(domain, domains[domain])
