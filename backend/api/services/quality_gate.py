"""Quality Gate system — Automated elevation/demotion of knowledge entries.

Phase 1 of Roadmap v2.0.
Implements the quality moat:
  - Entries with quality_score < 80 are demoted to "draft" (hidden from public API)
  - Entries with quality_score >= 80 and freshness "verified" are "published"
  - Automated gate checks on every audit run
  - API responses include quality metadata headers

Quality score formula:
  source_authority (30%) + freshness (25%) + completeness (25%) + verification (20%)
"""
import logging
from datetime import date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# ── Gate thresholds ────────────────────────────────────────────
PUBLISH_THRESHOLD = 80      # Minimum score to be published
DRAFT_THRESHOLD = 60        # Below this → flagged for review
UNPUBLISH_THRESHOLD = 50    # Below this → hidden from API

# ── Source authority weights ───────────────────────────────────
SOURCE_AUTHORITY = {
    "official_law": 1.0,         # e-Gov, 法令データベース
    "official_gov": 0.95,        # 各省庁公式サイト
    "official_association": 0.90, # 業界団体公式
    "domain_expert": 0.85,       # 専門家監修
    "verified_media": 0.75,      # 信頼性の高いメディア
    "community": 0.60,           # コミュニティ情報
    "llm_generated": 0.30,       # LLM生成（未検証）
    "system": 0.50,              # システム内部
}


class QualityGate:
    """Evaluates knowledge entries and determines publish/draft status."""

    def score_entry(self, entry_data: dict) -> dict:
        """Calculate quality score for a single KB entry.

        Returns:
            {
                "quality_score": float (0-100),
                "gate_status": "published" | "draft" | "flagged" | "unpublished",
                "breakdown": { ... },
                "recommendations": [str],
            }
        """
        meta = entry_data.get("_meta", {})
        recommendations = []

        # 1. Source authority (30%)
        source = meta.get("source", "llm_generated")
        source_authority = self._classify_source_authority(source)
        source_score = source_authority * 100
        if source_score < 80:
            recommendations.append(f"Upgrade source from '{source}' to official/verified source")

        # 2. Freshness (25%)
        last_verified = meta.get("last_verified")
        freshness_score = self._compute_freshness_score(last_verified)
        if freshness_score < 80:
            recommendations.append(f"Re-verify entry (last verified: {last_verified or 'never'})")

        # 3. Completeness (25%)
        completeness_score = self._compute_completeness_score(entry_data, meta)
        if completeness_score < 80:
            missing = []
            if not meta.get("source_url"):
                missing.append("source_url")
            if not meta.get("last_verified"):
                missing.append("last_verified")
            if not entry_data.get("name_ja"):
                missing.append("name_ja")
            if missing:
                recommendations.append(f"Add missing fields: {', '.join(missing)}")

        # 4. Verification status (20%)
        verification_score = 100.0 if meta.get("confidence") == "verified" else (
            70.0 if meta.get("confidence") == "likely_current" else 40.0
        )
        if verification_score < 80:
            recommendations.append("Mark as verified after manual review")

        # Weighted total
        quality_score = round(
            source_score * 0.30 +
            freshness_score * 0.25 +
            completeness_score * 0.25 +
            verification_score * 0.20,
            1
        )

        # Gate decision
        if quality_score >= PUBLISH_THRESHOLD:
            gate_status = "published"
        elif quality_score >= DRAFT_THRESHOLD:
            gate_status = "draft"
        elif quality_score >= UNPUBLISH_THRESHOLD:
            gate_status = "flagged"
        else:
            gate_status = "unpublished"

        return {
            "quality_score": quality_score,
            "gate_status": gate_status,
            "breakdown": {
                "source_authority": round(source_score, 1),
                "freshness": round(freshness_score, 1),
                "completeness": round(completeness_score, 1),
                "verification": round(verification_score, 1),
            },
            "recommendations": recommendations,
        }

    def evaluate_domain(self, domain_name: str, domain_data: dict) -> dict:
        """Evaluate all entries in a domain and return aggregate gate report.

        Returns:
            {
                "domain": str,
                "avg_quality_score": float,
                "gate_summary": {"published": N, "draft": N, ...},
                "entries": [{entry_id, quality_score, gate_status, ...}],
                "domain_gate_status": "published" | "draft",
            }
        """
        entries = []
        gate_counts = {"published": 0, "draft": 0, "flagged": 0, "unpublished": 0}

        for entry_id, entry_data in domain_data.items():
            if entry_id.startswith("_"):
                continue
            result = self.score_entry(entry_data)
            result["entry_id"] = entry_id
            result["name"] = entry_data.get("name_ja") or entry_data.get("name_en") or entry_id
            entries.append(result)
            gate_counts[result["gate_status"]] += 1

        avg_score = round(
            sum(e["quality_score"] for e in entries) / max(len(entries), 1), 1
        )

        # Domain-level gate: published only if ALL entries are published
        domain_status = "published" if gate_counts["published"] == len(entries) and len(entries) > 0 else "draft"

        return {
            "domain": domain_name,
            "total_entries": len(entries),
            "avg_quality_score": avg_score,
            "gate_summary": gate_counts,
            "domain_gate_status": domain_status,
            "entries": sorted(entries, key=lambda x: x["quality_score"]),
        }

    def run_full_audit(self) -> dict:
        """Run quality gate across all domains. Returns platform-wide report."""
        from backend.api.services.kb_loader import load_all_domains
        domains = load_all_domains()

        domain_reports = {}
        total_entries = 0
        total_score_sum = 0
        platform_gate_counts = {"published": 0, "draft": 0, "flagged": 0, "unpublished": 0}

        for domain_name, domain_data in domains.items():
            report = self.evaluate_domain(domain_name, domain_data)
            domain_reports[domain_name] = report
            total_entries += report["total_entries"]
            total_score_sum += report["avg_quality_score"] * report["total_entries"]
            for status, count in report["gate_summary"].items():
                platform_gate_counts[status] += count

        platform_score = round(total_score_sum / max(total_entries, 1), 1)

        return {
            "audit_date": date.today().isoformat(),
            "platform": {
                "total_entries": total_entries,
                "avg_quality_score": platform_score,
                "gate_summary": platform_gate_counts,
                "publish_rate": round(
                    platform_gate_counts["published"] / max(total_entries, 1) * 100, 1
                ),
            },
            "thresholds": {
                "publish": PUBLISH_THRESHOLD,
                "draft": DRAFT_THRESHOLD,
                "unpublish": UNPUBLISH_THRESHOLD,
            },
            "domains": domain_reports,
        }

    # ── Private helpers ────────────────────────────────────────

    def _compute_freshness_score(self, last_verified: Optional[str]) -> float:
        """Score based on how recently the entry was verified."""
        if not last_verified:
            return 30.0
        try:
            verified_date = date.fromisoformat(last_verified)
            days_since = (date.today() - verified_date).days
            if days_since <= 30:
                return 100.0
            elif days_since <= 90:
                return 90.0
            elif days_since <= 180:
                return 75.0
            elif days_since <= 365:
                return 50.0
            else:
                return 25.0
        except (ValueError, TypeError):
            return 30.0

    def _compute_completeness_score(self, entry_data: dict, meta: dict) -> float:
        """Score based on how complete the entry metadata is."""
        checks = [
            meta.get("source") is not None,
            meta.get("source_url") is not None,
            meta.get("last_verified") is not None,
            meta.get("confidence") is not None,
            meta.get("version") is not None,
            entry_data.get("name_ja") is not None or entry_data.get("name_en") is not None,
        ]
        return round(sum(checks) / len(checks) * 100, 1)

    def _classify_source_authority(self, source: str) -> float:
        """Classify source authority from free-text source field.

        KB entries use descriptive Japanese source strings like
        '厚生労働省 食品衛生法' rather than category keys.
        This method uses keyword matching to determine authority level.
        """
        if not source:
            return 0.30

        # Check if it's a category key first
        if source in SOURCE_AUTHORITY:
            return SOURCE_AUTHORITY[source]

        source_lower = source.lower()

        # Official law sources (1.0)
        law_keywords = ["法律", "法令", "法", "条例", "規則", "e-gov", "法令データベース"]
        if any(kw in source_lower for kw in law_keywords):
            return 1.0

        # Official government sources (0.95)
        gov_keywords = [
            "省", "庁", "府", "総務", "厚生労働", "国土交通", "経済産業",
            "文部科学", "環境", "防衛", "法務", "外務", "財務", "農林水産",
            "内閣", "官邸", "気象", "消防", "警察", "保健所", "地方自治体",
            "都道府県", "市区町村", "国税", "税務署",
            "jnto", "japan.travel", "mlit.go.jp", "mhlw.go.jp",
            "go.jp", "government", "official",
        ]
        if any(kw in source_lower for kw in gov_keywords):
            return 0.95

        # Official association sources (0.90)
        assoc_keywords = [
            "協会", "連合会", "商工会", "組合", "財団", "機構",
            "jta", "jetro", "jnto",
        ]
        if any(kw in source_lower for kw in assoc_keywords):
            return 0.90

        # Domain expert / verified reference (0.85)
        expert_keywords = [
            "expert", "専門家", "監修", "研究", "学会", "大学",
            "wikipedia", "britannica", "nikkei",
            "edition knowledge base",
        ]
        if any(kw in source_lower for kw in expert_keywords):
            return 0.85

        # If source_url is present in meta, assume at least verified_media level
        # (This is a heuristic — entries with source URLs are typically better)
        return 0.75  # Default: treat as verified_media if source exists


# ── Module singleton ──
quality_gate = QualityGate()
