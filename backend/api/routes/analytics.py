"""Analytics API routes — usage monitoring and traffic insights."""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from backend.api.db.database import get_db
from backend.api.models.analytics import ApiRequestLog

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/summary")
def analytics_summary(
    period: str = Query("24h", description="Period: 1h, 24h, 7d, 30d"),
    db: Session = Depends(get_db),
):
    """Usage summary — request counts, domain breakdown, popular queries, agents."""
    now = datetime.now(timezone.utc)
    period_map = {"1h": 1/24, "24h": 1, "7d": 7, "30d": 30}
    days = period_map.get(period, 1)
    since = now - timedelta(days=days)

    logs = db.query(ApiRequestLog).filter(ApiRequestLog.timestamp >= since)

    total = logs.count()

    # Domain breakdown
    domain_stats = (
        logs.with_entities(ApiRequestLog.domain, func.count())
        .filter(ApiRequestLog.domain.isnot(None))
        .group_by(ApiRequestLog.domain)
        .order_by(desc(func.count()))
        .all()
    )

    # Top paths
    path_stats = (
        logs.with_entities(ApiRequestLog.path, func.count())
        .group_by(ApiRequestLog.path)
        .order_by(desc(func.count()))
        .limit(10)
        .all()
    )

    # Popular queries
    query_stats = (
        logs.with_entities(ApiRequestLog.query_text, func.count())
        .filter(ApiRequestLog.query_text.isnot(None))
        .group_by(ApiRequestLog.query_text)
        .order_by(desc(func.count()))
        .limit(10)
        .all()
    )

    # Agent breakdown
    agent_stats = (
        logs.with_entities(ApiRequestLog.agent_name, func.count())
        .filter(ApiRequestLog.agent_name.isnot(None))
        .group_by(ApiRequestLog.agent_name)
        .order_by(desc(func.count()))
        .all()
    )

    # Unique user agents
    unique_agents = (
        logs.with_entities(ApiRequestLog.user_agent)
        .filter(ApiRequestLog.user_agent.isnot(None))
        .distinct()
        .count()
    )

    # Avg latency
    avg_latency = (
        logs.with_entities(func.avg(ApiRequestLog.latency_ms))
        .scalar()
    ) or 0

    return {
        "period": period,
        "since": since.isoformat(),
        "total_requests": total,
        "unique_user_agents": unique_agents,
        "avg_latency_ms": round(avg_latency, 2),
        "domains": {d: c for d, c in domain_stats},
        "top_paths": {p: c for p, c in path_stats},
        "top_queries": {q: c for q, c in query_stats},
        "agents": {a or "unknown": c for a, c in agent_stats},
    }


@router.get("/timeline")
def analytics_timeline(
    period: str = Query("24h", description="Period: 24h, 7d, 30d"),
    db: Session = Depends(get_db),
):
    """Hourly request counts for timeline visualization."""
    now = datetime.now(timezone.utc)
    period_map = {"24h": 1, "7d": 7, "30d": 30}
    days = period_map.get(period, 1)
    since = now - timedelta(days=days)

    logs = (
        db.query(ApiRequestLog)
        .filter(ApiRequestLog.timestamp >= since)
        .all()
    )

    # Bucket by hour
    buckets = {}
    for log in logs:
        hour_key = log.timestamp.strftime("%Y-%m-%d %H:00")
        buckets[hour_key] = buckets.get(hour_key, 0) + 1

    return {
        "period": period,
        "since": since.isoformat(),
        "timeline": [{"hour": k, "count": v} for k, v in sorted(buckets.items())],
    }


@router.get("/agents")
def analytics_agents(db: Session = Depends(get_db)):
    """Agent-level usage statistics."""
    agent_stats = (
        db.query(
            ApiRequestLog.agent_name,
            func.count().label("total"),
            func.avg(ApiRequestLog.latency_ms).label("avg_latency"),
            func.min(ApiRequestLog.timestamp).label("first_seen"),
            func.max(ApiRequestLog.timestamp).label("last_seen"),
        )
        .group_by(ApiRequestLog.agent_name)
        .order_by(desc(func.count()))
        .all()
    )

    return {
        "agents": [
            {
                "name": a.agent_name or "unknown",
                "total_requests": a.total,
                "avg_latency_ms": round(a.avg_latency or 0, 2),
                "first_seen": a.first_seen.isoformat() if a.first_seen else None,
                "last_seen": a.last_seen.isoformat() if a.last_seen else None,
            }
            for a in agent_stats
        ]
    }


# ── Phase 5A: MCP Telemetry ──────────────────────────────────

@router.get("/mcp")
def analytics_mcp(
    period: str = Query("30d", description="Period: 1h, 24h, 7d, 30d"),
    db: Session = Depends(get_db),
):
    """MCP-specific telemetry — tool usage breakdown by domain."""
    now = datetime.now(timezone.utc)
    period_map = {"1h": 1/24, "24h": 1, "7d": 7, "30d": 30}
    days = period_map.get(period, 30)
    since = now - timedelta(days=days)

    # MCP tool calls (identified by path = /mcp)
    mcp_logs = (
        db.query(ApiRequestLog)
        .filter(ApiRequestLog.timestamp >= since)
        .filter(ApiRequestLog.path == "/mcp")
        .all()
    )

    # Tool usage breakdown
    tool_counts = {}
    domain_via_mcp = {}
    sessions = set()
    for log in mcp_logs:
        if log.mcp_tool_name:
            tool_counts[log.mcp_tool_name] = tool_counts.get(log.mcp_tool_name, 0) + 1
        if log.response_domains:
            for d in log.response_domains.split(","):
                d = d.strip()
                if d:
                    domain_via_mcp[d] = domain_via_mcp.get(d, 0) + 1
        if log.mcp_session_id:
            sessions.add(log.mcp_session_id)

    # REST API calls for comparison
    rest_total = (
        db.query(ApiRequestLog)
        .filter(ApiRequestLog.timestamp >= since)
        .filter(ApiRequestLog.path != "/mcp")
        .filter(ApiRequestLog.path.like("/api/v1/%"))
        .count()
    )

    return {
        "period": period,
        "since": since.isoformat(),
        "mcp": {
            "total_calls": len(mcp_logs),
            "unique_sessions": len(sessions),
            "tool_usage": dict(sorted(tool_counts.items(), key=lambda x: -x[1])),
            "domains_accessed": dict(sorted(domain_via_mcp.items(), key=lambda x: -x[1])),
        },
        "rest": {
            "total_calls": rest_total,
        },
        "mcp_ratio": round(len(mcp_logs) / max(len(mcp_logs) + rest_total, 1) * 100, 1),
    }


# ── Phase 5B: Quality Scoring (Trust Anchor) ─────────────────

DOMAIN_QUALITY = {
    "memory": {"rules": True, "context": True, "experience": False, "entries": 5, "verified": True, "source": "system"},
    "regulation": {"rules": True, "context": True, "experience": True, "entries": 10, "verified": True, "source": "official_law"},
    "procedure": {"rules": True, "context": True, "experience": True, "entries": 65, "verified": True, "source": "official_gov"},
    "protocol": {"rules": True, "context": True, "experience": True, "entries": 6, "verified": True, "source": "domain_expert"},
    "calendar": {"rules": True, "context": True, "experience": True, "entries": 5, "verified": True, "source": "official_gov"},
    "regional": {"rules": True, "context": True, "experience": True, "entries": 4, "verified": True, "source": "official_gov"},
    "organization": {"rules": True, "context": True, "experience": True, "entries": 5, "verified": True, "source": "domain_expert"},
    "foreign_entry": {"rules": True, "context": True, "experience": True, "entries": 5, "verified": True, "source": "official_gov"},
    "travel": {"rules": True, "context": True, "experience": True, "entries": 4, "verified": True, "source": "domain_expert"},
    "entertainment": {"rules": True, "context": True, "experience": True, "entries": 4, "verified": True, "source": "domain_expert"},
    "daily_life": {"rules": True, "context": True, "experience": True, "entries": 4, "verified": True, "source": "official_gov"},
    "language": {"rules": True, "context": True, "experience": True, "entries": 4, "verified": True, "source": "domain_expert"},
    "food": {"rules": True, "context": True, "experience": True, "entries": 4, "verified": True, "source": "domain_expert"},
    "disaster": {"rules": True, "context": True, "experience": True, "entries": 4, "verified": True, "source": "official_gov"},
}


@router.get("/quality")
def analytics_quality():
    """Knowledge quality dashboard — Trust Anchor scoring for each domain."""
    domains = []
    total_score = 0
    for domain_id, meta in DOMAIN_QUALITY.items():
        layers = sum([meta["rules"], meta["context"], meta["experience"]])
        layer_score = layers / 3.0
        verified_score = 1.0 if meta["verified"] else 0.5
        source_weights = {"official_law": 1.0, "official_gov": 0.95, "domain_expert": 0.85, "community": 0.7, "llm_generated": 0.3}
        source_score = source_weights.get(meta["source"], 0.5)
        quality = round((layer_score * 0.4 + verified_score * 0.35 + source_score * 0.25) * 100, 1)
        total_score += quality
        domains.append({
            "domain": domain_id,
            "quality_score": quality,
            "layers": {
                "rules": meta["rules"],
                "context": meta["context"],
                "experience": meta["experience"],
            },
            "entries": meta["entries"],
            "verified": meta["verified"],
            "source": meta["source"],
        })

    avg_score = round(total_score / len(DOMAIN_QUALITY), 1)
    full_coverage = sum(1 for d in DOMAIN_QUALITY.values() if all([d["rules"], d["context"], d["experience"]]))

    return {
        "platform_quality_score": avg_score,
        "total_domains": len(DOMAIN_QUALITY),
        "full_3layer_coverage": full_coverage,
        "total_entries": sum(d["entries"] for d in DOMAIN_QUALITY.values()),
        "all_verified": all(d["verified"] for d in DOMAIN_QUALITY.values()),
        "domains": sorted(domains, key=lambda x: -x["quality_score"]),
    }


# ── Phase 5C: Agent Reputation Protocol ──────────────────────

@router.get("/reputation")
def analytics_reputation(
    period: str = Query("30d", description="Period: 7d, 30d"),
    db: Session = Depends(get_db),
):
    """Agent reputation — usage patterns, depth of engagement, domain diversity."""
    now = datetime.now(timezone.utc)
    period_map = {"7d": 7, "30d": 30}
    days = period_map.get(period, 30)
    since = now - timedelta(days=days)

    # Get all agent stats grouped by name
    agent_data = (
        db.query(
            ApiRequestLog.agent_name,
            func.count().label("total"),
            func.avg(ApiRequestLog.latency_ms).label("avg_latency"),
            func.min(ApiRequestLog.timestamp).label("first_seen"),
            func.max(ApiRequestLog.timestamp).label("last_seen"),
        )
        .filter(ApiRequestLog.timestamp >= since)
        .group_by(ApiRequestLog.agent_name)
        .order_by(desc(func.count()))
        .all()
    )

    agents = []
    for a in agent_data:
        name = a.agent_name or "unknown"

        # Domain diversity for this agent
        domain_result = (
            db.query(ApiRequestLog.domain, func.count())
            .filter(ApiRequestLog.timestamp >= since)
            .filter(ApiRequestLog.agent_name == a.agent_name)
            .filter(ApiRequestLog.domain.isnot(None))
            .group_by(ApiRequestLog.domain)
            .all()
        )
        domains_used = {d: c for d, c in domain_result}

        # Calculate reputation score
        diversity = min(len(domains_used) / 14.0, 1.0)  # breadth across 14 domains
        volume = min(a.total / 100.0, 1.0)  # usage volume (cap at 100)
        recency_days = (now - a.last_seen.replace(tzinfo=timezone.utc)).days if a.last_seen else 30
        recency = max(1.0 - recency_days / 30.0, 0.0)
        rep_score = round((diversity * 0.4 + volume * 0.3 + recency * 0.3) * 100, 1)

        agents.append({
            "agent": name,
            "reputation_score": rep_score,
            "total_requests": a.total,
            "domains_used": len(domains_used),
            "domain_breakdown": domains_used,
            "avg_latency_ms": round(a.avg_latency or 0, 2),
            "first_seen": a.first_seen.isoformat() if a.first_seen else None,
            "last_seen": a.last_seen.isoformat() if a.last_seen else None,
        })

    return {
        "period": period,
        "since": since.isoformat(),
        "total_agents": len(agents),
        "agents": sorted(agents, key=lambda x: -x["reputation_score"]),
    }


@router.get("/weekly")
def weekly_summary(db: Session = Depends(get_db)):
    """Weekly intelligence summary — demand detection + platform health.

    Designed to be checked every Monday to detect usage patterns,
    new agent arrivals, and knowledge freshness degradation.
    """
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    prev_week_start = week_ago - timedelta(days=7)

    # Current week stats
    current_logs = db.query(ApiRequestLog).filter(ApiRequestLog.timestamp >= week_ago)
    current_total = current_logs.count()

    # Previous week stats (for comparison)
    prev_logs = db.query(ApiRequestLog).filter(
        ApiRequestLog.timestamp >= prev_week_start,
        ApiRequestLog.timestamp < week_ago,
    )
    prev_total = prev_logs.count()

    # Growth rate
    growth = round(((current_total - prev_total) / max(prev_total, 1)) * 100, 1)

    # Domain heat map (which domains are getting attention)
    domain_heat = dict(
        current_logs.with_entities(ApiRequestLog.domain, func.count())
        .filter(ApiRequestLog.domain.isnot(None))
        .group_by(ApiRequestLog.domain)
        .order_by(desc(func.count()))
        .all()
    )

    # New agents detected this week
    all_agents_before = set(
        a[0] for a in db.query(ApiRequestLog.agent_name)
        .filter(ApiRequestLog.timestamp < week_ago)
        .filter(ApiRequestLog.agent_name.isnot(None))
        .distinct()
        .all()
    )
    current_agents = set(
        a[0] for a in current_logs
        .with_entities(ApiRequestLog.agent_name)
        .filter(ApiRequestLog.agent_name.isnot(None))
        .distinct()
        .all()
    )
    new_agents = list(current_agents - all_agents_before)

    # Peak hours (UTC)
    hour_dist = dict(
        current_logs.with_entities(
            func.extract("hour", ApiRequestLog.timestamp).label("hour"),
            func.count(),
        )
        .group_by("hour")
        .order_by(desc(func.count()))
        .limit(5)
        .all()
    )

    # Top queries this week
    top_queries = [
        {"query": q, "count": c}
        for q, c in current_logs
        .with_entities(ApiRequestLog.query_text, func.count())
        .filter(ApiRequestLog.query_text.isnot(None))
        .group_by(ApiRequestLog.query_text)
        .order_by(desc(func.count()))
        .limit(10)
        .all()
    ]

    # MCP tool usage
    mcp_usage = dict(
        current_logs.with_entities(ApiRequestLog.mcp_tool_name, func.count())
        .filter(ApiRequestLog.mcp_tool_name.isnot(None))
        .group_by(ApiRequestLog.mcp_tool_name)
        .order_by(desc(func.count()))
        .all()
    )

    # Knowledge freshness summary
    try:
        from backend.api.services.freshness import freshness_report
        fr = freshness_report.generate_report()
        freshness = {
            "health_score": fr["platform"]["health_score"],
            "total_entries": fr["platform"]["total_entries"],
            "stale_count": fr["action_required"]["total_action_needed"],
            "next_review": fr["next_review"]["recommended_date"],
        }
    except Exception:
        freshness = {"health_score": 0, "note": "Could not generate freshness report"}

    return {
        "report_type": "weekly_intelligence_summary",
        "period": {
            "start": week_ago.isoformat(),
            "end": now.isoformat(),
        },
        "traffic": {
            "total_requests": current_total,
            "previous_week": prev_total,
            "growth_percent": growth,
            "trend": "up" if growth > 0 else ("down" if growth < 0 else "flat"),
        },
        "domain_heat": domain_heat,
        "agents": {
            "total_active": len(current_agents),
            "new_this_week": new_agents,
            "new_count": len(new_agents),
        },
        "peak_hours_utc": hour_dist,
        "top_queries": top_queries,
        "mcp_tool_usage": mcp_usage,
        "knowledge_freshness": freshness,
        "demand_signals": {
            "has_real_traffic": current_total > 10,
            "has_agent_traffic": len(current_agents) > 0,
            "dominant_domain": max(domain_heat, key=domain_heat.get) if domain_heat else None,
            "recommendation": (
                "Real demand detected. Analyze top queries for feature prioritization."
                if current_total > 10
                else "No significant traffic yet. Continue marketing efforts."
            ),
        },
    }

