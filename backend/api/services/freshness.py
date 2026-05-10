"""Knowledge freshness management system.

Tracks, evaluates, and reports on the currency and reliability
of all EDITION knowledge entries. Supports automated degradation
detection and semi-automated update workflows.

Architecture:
  1. FreshnessMetadata — per-entry metadata (source, date, confidence)
  2. FreshnessChecker — scans all domains and computes staleness
  3. FreshnessReport — generates platform-wide freshness analytics
  4. Integration with all API responses via _freshness field
"""
import logging
from datetime import datetime, date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# ── Freshness confidence levels ────────────────────────────────
CONFIDENCE_LEVELS = {
    "verified": {
        "label": "Verified",
        "description": "Confirmed accurate against official sources within the last 6 months",
        "color": "#22c55e",
        "trust_score": 1.0,
    },
    "likely_current": {
        "label": "Likely Current",
        "description": "No known changes since last verification, but not recently re-checked",
        "color": "#84cc16",
        "trust_score": 0.8,
    },
    "needs_review": {
        "label": "Needs Review",
        "description": "More than 6 months since last verification. May contain outdated information",
        "color": "#f59e0b",
        "trust_score": 0.5,
    },
    "stale": {
        "label": "Stale",
        "description": "More than 12 months since last verification. Treat with caution",
        "color": "#ef4444",
        "trust_score": 0.3,
    },
    "deprecated": {
        "label": "Deprecated",
        "description": "Known to be outdated due to law changes or policy updates",
        "color": "#991b1b",
        "trust_score": 0.1,
    },
}

# ── Default metadata for entries without explicit _meta ────────
DEFAULT_META = {
    "last_verified": "2026-05-10",
    "source": "EDITION knowledge base",
    "source_url": None,
    "confidence": "verified",
    "valid_until": None,
    "version": "1.0.0",
    "changelog": ["2026-05-10: Initial verified entry"],
}


# ── FreshnessChecker ───────────────────────────────────────────

class FreshnessChecker:
    """Scans all knowledge entries and computes freshness status."""

    # Thresholds in days
    VERIFIED_WINDOW = 180     # 6 months
    REVIEW_WINDOW = 365       # 12 months

    def compute_confidence(self, meta: dict) -> str:
        """Compute confidence level from metadata.

        Logic:
          1. If valid_until has passed → deprecated
          2. If last_verified is > 12 months → stale
          3. If last_verified is > 6 months → needs_review
          4. If last_verified is > 3 months → likely_current
          5. Otherwise → verified (or use explicit confidence)
        """
        today = date.today()

        # Check expiration
        valid_until = meta.get("valid_until")
        if valid_until:
            try:
                expiry = date.fromisoformat(valid_until)
                if today > expiry:
                    return "deprecated"
            except (ValueError, TypeError):
                pass

        # Check last verification date
        last_verified = meta.get("last_verified")
        if last_verified:
            try:
                verified_date = date.fromisoformat(last_verified)
                days_since = (today - verified_date).days

                if days_since > self.REVIEW_WINDOW:
                    return "stale"
                elif days_since > self.VERIFIED_WINDOW:
                    return "needs_review"
                elif days_since > 90:
                    return "likely_current"
                else:
                    return meta.get("confidence", "verified")
            except (ValueError, TypeError):
                pass

        # No date info → needs_review
        return "needs_review"

    def build_freshness_response(self, meta: dict) -> dict:
        """Build the _freshness block for API responses."""
        computed = self.compute_confidence(meta)
        level_info = CONFIDENCE_LEVELS.get(computed, CONFIDENCE_LEVELS["needs_review"])

        warning = None
        if computed == "stale":
            warning = f"This information was last verified on {meta.get('last_verified', 'unknown')}. It may be outdated."
        elif computed == "needs_review":
            warning = f"This information was last verified on {meta.get('last_verified', 'unknown')}. Review recommended."
        elif computed == "deprecated":
            warning = "This information is known to be outdated. Do not rely on it for decisions."

        return {
            "confidence": computed,
            "trust_score": level_info["trust_score"],
            "last_verified": meta.get("last_verified"),
            "source": meta.get("source", "EDITION knowledge base"),
            "source_url": meta.get("source_url"),
            "version": meta.get("version", "1.0.0"),
            "warning": warning,
        }


# ── FreshnessReport ────────────────────────────────────────────

class FreshnessReport:
    """Generates platform-wide freshness analytics."""

    def __init__(self):
        self.checker = FreshnessChecker()

    def _load_all_domains(self) -> dict:
        """Load all KB modules and extract their entries with metadata."""
        domains = {}

        # Import all KBs
        domain_configs = [
            ("regulation", "backend.api.services.regulation_kb", "REGULATION_DB"),
            ("protocol", "backend.api.services.protocol_kb", "PROTOCOL_DB"),
            ("calendar", "backend.api.services.calendar_kb", "CALENDAR_DB"),
            ("regional", "backend.api.services.regional_kb", "REGIONAL_DB"),
            ("organization", "backend.api.services.organization_kb", "ORGANIZATION_DB"),
            ("foreign_entry", "backend.api.services.foreign_entry_kb", "FOREIGN_ENTRY_DB"),
            ("travel", "backend.api.services.travel_kb", "TRAVEL_DB"),
            ("entertainment", "backend.api.services.entertainment_kb", "ENTERTAINMENT_DB"),
            ("daily_life", "backend.api.services.daily_life_kb", "DAILY_LIFE_DB"),
            ("language", "backend.api.services.language_kb", "LANGUAGE_DB"),
            ("food", "backend.api.services.food_kb", "FOOD_DB"),
            ("disaster", "backend.api.services.disaster_kb", "DISASTER_DB"),
        ]

        for domain_name, module_path, var_name in domain_configs:
            try:
                import importlib
                module = importlib.import_module(module_path)
                db = getattr(module, var_name, {})
                domains[domain_name] = db
            except Exception as e:
                logger.warning(f"Could not load KB for {domain_name}: {e}")

        return domains

    def generate_report(self) -> dict:
        """Generate comprehensive freshness report for all domains."""
        domains = self._load_all_domains()
        today = date.today()

        domain_reports = {}
        total_entries = 0
        confidence_counts = {k: 0 for k in CONFIDENCE_LEVELS}
        stale_entries = []
        deprecated_entries = []

        for domain_name, db in domains.items():
            entries = []
            for entry_id, entry_data in db.items():
                meta = entry_data.get("_meta", DEFAULT_META.copy())
                computed_confidence = self.checker.compute_confidence(meta)

                entry_info = {
                    "id": entry_id,
                    "name": entry_data.get("name_ja") or entry_data.get("name_en") or entry_id,
                    "confidence": computed_confidence,
                    "last_verified": meta.get("last_verified"),
                    "source": meta.get("source"),
                    "version": meta.get("version", "1.0.0"),
                }

                entries.append(entry_info)
                confidence_counts[computed_confidence] = confidence_counts.get(computed_confidence, 0) + 1
                total_entries += 1

                if computed_confidence == "stale":
                    stale_entries.append({"domain": domain_name, **entry_info})
                elif computed_confidence == "deprecated":
                    deprecated_entries.append({"domain": domain_name, **entry_info})

            # Domain-level summary
            domain_confidence_dist = {}
            for e in entries:
                c = e["confidence"]
                domain_confidence_dist[c] = domain_confidence_dist.get(c, 0) + 1

            domain_reports[domain_name] = {
                "total_entries": len(entries),
                "confidence_distribution": domain_confidence_dist,
                "health_score": self._compute_health_score(entries),
                "entries": entries,
            }

        # Platform health score
        platform_health = sum(
            CONFIDENCE_LEVELS.get(c, {}).get("trust_score", 0) * count
            for c, count in confidence_counts.items()
        ) / max(total_entries, 1) * 100

        return {
            "report_date": today.isoformat(),
            "platform": {
                "total_domains": len(domains),
                "total_entries": total_entries,
                "health_score": round(platform_health, 1),
                "confidence_distribution": confidence_counts,
            },
            "domains": domain_reports,
            "action_required": {
                "stale_entries": stale_entries,
                "deprecated_entries": deprecated_entries,
                "total_action_needed": len(stale_entries) + len(deprecated_entries),
            },
            "next_review": {
                "recommended_date": (today + timedelta(days=30)).isoformat(),
                "entries_due_for_review": sum(
                    1 for c, n in confidence_counts.items()
                    if c in ("needs_review", "stale", "deprecated")
                    for _ in range(n)
                ),
            },
        }

    def get_stale_entries(self) -> list:
        """Get all entries that need review or are stale/deprecated."""
        domains = self._load_all_domains()
        results = []

        for domain_name, db in domains.items():
            for entry_id, entry_data in db.items():
                meta = entry_data.get("_meta", DEFAULT_META.copy())
                computed = self.checker.compute_confidence(meta)

                if computed in ("needs_review", "stale", "deprecated"):
                    results.append({
                        "domain": domain_name,
                        "entry_id": entry_id,
                        "name": entry_data.get("name_ja") or entry_id,
                        "confidence": computed,
                        "last_verified": meta.get("last_verified"),
                        "source": meta.get("source"),
                        "days_since_verified": self._days_since(meta.get("last_verified")),
                    })

        # Sort by staleness (most stale first)
        results.sort(key=lambda x: x.get("days_since_verified") or 9999, reverse=True)
        return results

    def get_domain_report(self, domain: str) -> Optional[dict]:
        """Get freshness report for a specific domain."""
        report = self.generate_report()
        return report.get("domains", {}).get(domain)

    def _compute_health_score(self, entries: list) -> float:
        """Compute health score (0-100) for a set of entries."""
        if not entries:
            return 0.0
        total = sum(
            CONFIDENCE_LEVELS.get(e["confidence"], {}).get("trust_score", 0)
            for e in entries
        )
        return round(total / len(entries) * 100, 1)

    def _days_since(self, date_str: Optional[str]) -> Optional[int]:
        """Compute days since a date string."""
        if not date_str:
            return None
        try:
            d = date.fromisoformat(date_str)
            return (date.today() - d).days
        except (ValueError, TypeError):
            return None


# ── Module-level instances ─────────────────────────────────────

freshness_checker = FreshnessChecker()
freshness_report = FreshnessReport()
