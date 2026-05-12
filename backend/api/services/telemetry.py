"""Telemetry v1 — Comprehensive tool invocation tracking and metadata.

Phase 1 of Roadmap v2.0.
Records every tool call with rich metadata and provides aggregated analytics.

Key capabilities:
  1. Per-tool invocation counts with latency tracking
  2. Domain-level heat maps (which knowledge areas are most demanded)
  3. Agent-level usage fingerprinting
  4. Time-series data for trend detection
  5. MCP vs REST traffic ratio
  6. Quality metadata injection into responses
"""
import logging
from datetime import datetime, timezone, timedelta, date
from typing import Optional
from sqlalchemy import func, desc, case, cast, Date
from sqlalchemy.orm import Session

from backend.api.models.analytics import ApiRequestLog

logger = logging.getLogger(__name__)


class TelemetryService:
    """Centralized telemetry aggregation engine."""

    # ── Tool Invocation Summary ────────────────────────────────

    def tool_invocations(
        self,
        db: Session,
        period_days: int = 30,
        tool_name: Optional[str] = None,
    ) -> dict:
        """Get tool invocation counts with metadata.

        Returns per-tool breakdown with call counts, avg latency,
        unique agents, and last-called timestamps.
        """
        since = datetime.now(timezone.utc) - timedelta(days=period_days)

        base_q = (
            db.query(ApiRequestLog)
            .filter(ApiRequestLog.timestamp >= since)
        )

        # For MCP tools: path = /mcp AND mcp_tool_name is not null
        # For REST tools: path starts with /api/v1/ (domain extracted)
        mcp_q = base_q.filter(
            ApiRequestLog.path == "/mcp",
            ApiRequestLog.mcp_tool_name.isnot(None),
        )

        if tool_name:
            mcp_q = mcp_q.filter(ApiRequestLog.mcp_tool_name == tool_name)

        # MCP tool stats
        mcp_stats = (
            mcp_q.with_entities(
                ApiRequestLog.mcp_tool_name,
                func.count().label("calls"),
                func.avg(ApiRequestLog.latency_ms).label("avg_latency"),
                func.max(ApiRequestLog.timestamp).label("last_called"),
            )
            .group_by(ApiRequestLog.mcp_tool_name)
            .order_by(desc(func.count()))
            .all()
        )

        # REST endpoint stats
        rest_q = base_q.filter(
            ApiRequestLog.path.like("/api/v1/%"),
            ApiRequestLog.domain.isnot(None),
        )
        rest_stats = (
            rest_q.with_entities(
                ApiRequestLog.path,
                func.count().label("calls"),
                func.avg(ApiRequestLog.latency_ms).label("avg_latency"),
                func.max(ApiRequestLog.timestamp).label("last_called"),
            )
            .group_by(ApiRequestLog.path)
            .order_by(desc(func.count()))
            .all()
        )

        # Unique agents per tool (MCP)
        tool_agents = {}
        for stat in mcp_stats:
            agents = (
                mcp_q.filter(ApiRequestLog.mcp_tool_name == stat.mcp_tool_name)
                .with_entities(ApiRequestLog.agent_name)
                .filter(ApiRequestLog.agent_name.isnot(None))
                .distinct()
                .all()
            )
            tool_agents[stat.mcp_tool_name] = [a[0] for a in agents]

        tools = []
        for s in mcp_stats:
            tools.append({
                "name": s.mcp_tool_name,
                "transport": "mcp",
                "calls": s.calls,
                "avg_latency_ms": round(s.avg_latency or 0, 2),
                "last_called": s.last_called.isoformat() if s.last_called else None,
                "agents": tool_agents.get(s.mcp_tool_name, []),
            })

        for s in rest_stats:
            tools.append({
                "name": s.path,
                "transport": "rest",
                "calls": s.calls,
                "avg_latency_ms": round(s.avg_latency or 0, 2),
                "last_called": s.last_called.isoformat() if s.last_called else None,
            })

        # Totals
        total_mcp = sum(t["calls"] for t in tools if t["transport"] == "mcp")
        total_rest = sum(t["calls"] for t in tools if t["transport"] == "rest")

        return {
            "period_days": period_days,
            "since": (datetime.now(timezone.utc) - timedelta(days=period_days)).isoformat(),
            "total_invocations": total_mcp + total_rest,
            "mcp_calls": total_mcp,
            "rest_calls": total_rest,
            "mcp_ratio_percent": round(total_mcp / max(total_mcp + total_rest, 1) * 100, 1),
            "tools": sorted(tools, key=lambda x: -x["calls"]),
        }

    # ── Domain Heat Map ────────────────────────────────────────

    def domain_heatmap(self, db: Session, period_days: int = 30) -> dict:
        """Domain-level demand heatmap.

        Shows which knowledge domains are most accessed,
        enabling data-driven domain expansion decisions.
        """
        since = datetime.now(timezone.utc) - timedelta(days=period_days)

        stats = (
            db.query(
                ApiRequestLog.domain,
                func.count().label("total"),
                func.avg(ApiRequestLog.latency_ms).label("avg_latency"),
                func.count(func.distinct(ApiRequestLog.agent_name)).label("unique_agents"),
            )
            .filter(
                ApiRequestLog.timestamp >= since,
                ApiRequestLog.domain.isnot(None),
            )
            .group_by(ApiRequestLog.domain)
            .order_by(desc(func.count()))
            .all()
        )

        total = sum(s.total for s in stats) or 1
        domains = []
        for s in stats:
            domains.append({
                "domain": s.domain,
                "calls": s.total,
                "share_percent": round(s.total / total * 100, 1),
                "avg_latency_ms": round(s.avg_latency or 0, 2),
                "unique_agents": s.unique_agents,
            })

        return {
            "period_days": period_days,
            "total_calls": total,
            "domains": domains,
        }

    # ── Daily Time Series ──────────────────────────────────────

    def daily_timeseries(self, db: Session, period_days: int = 30) -> dict:
        """Daily call counts for trend visualization."""
        since = datetime.now(timezone.utc) - timedelta(days=period_days)

        logs = (
            db.query(ApiRequestLog)
            .filter(ApiRequestLog.timestamp >= since)
            .all()
        )

        daily = {}
        for log in logs:
            day_key = log.timestamp.strftime("%Y-%m-%d")
            daily[day_key] = daily.get(day_key, 0) + 1

        # Fill gaps with zeros
        series = []
        current = date.today() - timedelta(days=period_days)
        end = date.today()
        while current <= end:
            key = current.isoformat()
            series.append({"date": key, "calls": daily.get(key, 0)})
            current += timedelta(days=1)

        return {
            "period_days": period_days,
            "series": series,
        }

    # ── Top Queries ────────────────────────────────────────────

    def top_queries(self, db: Session, period_days: int = 30, limit: int = 20) -> dict:
        """Most popular search queries — reveals what agents actually need."""
        since = datetime.now(timezone.utc) - timedelta(days=period_days)

        stats = (
            db.query(
                ApiRequestLog.query_text,
                ApiRequestLog.domain,
                func.count().label("count"),
            )
            .filter(
                ApiRequestLog.timestamp >= since,
                ApiRequestLog.query_text.isnot(None),
            )
            .group_by(ApiRequestLog.query_text, ApiRequestLog.domain)
            .order_by(desc(func.count()))
            .limit(limit)
            .all()
        )

        return {
            "period_days": period_days,
            "queries": [
                {"query": s.query_text, "domain": s.domain, "count": s.count}
                for s in stats
            ],
        }


# ── Module singleton ──
telemetry_service = TelemetryService()
