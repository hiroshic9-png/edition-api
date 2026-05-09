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
