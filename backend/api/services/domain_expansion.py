"""Domain expansion intelligence — Phase 2 data-driven domain planning.

Analyzes telemetry data + external signals to recommend new knowledge domains.
Provides a structured framework for evaluating domain candidates.

Current 20 domains:
  regulation, protocol, calendar, regional, organization, foreign_entry,
  travel, entertainment, daily_life, language, food, disaster

Expansion candidates (6 new domains for 14→20):
  tax, visa_immigration, banking_finance, healthcare_detailed,
  education, real_estate_detailed
"""
import logging
from datetime import date
from typing import Optional

logger = logging.getLogger(__name__)


# ── Domain Expansion Candidates ────────────────────────────────
EXPANSION_CANDIDATES = {
    "tax": {
        "name_ja": "税務・確定申告",
        "name_en": "Tax & Filing",
        "description": "Japanese tax system for foreign nationals and companies: income tax brackets, consumption tax, withholding tax, residence tax, year-end adjustment (nenmatsu chosei), final tax return (kakutei shinkoku), e-Tax system, tax treaty benefits, and crypto/stock capital gains treatment.",
        "priority": "HIGH",
        "rationale": "Tax queries are embedded across regulation, foreign_entry, and daily_life but lack dedicated depth. Most common real-world need for foreigners operating in Japan.",
        "estimated_entries": 8,
        "source_authority": "official_gov",
        "key_sources": [
            "https://www.nta.go.jp/ (国税庁)",
            "https://www.soumu.go.jp/main_sosiki/jichi_zeisei/ (総務省 地方税)",
        ],
        "demand_signals": [
            "Cross-domain queries containing '税' or 'tax'",
            "foreign_entry domain has tax procedures embedded",
            "Daily life domain has utility/NHK tax mentions",
        ],
        "dependencies": ["foreign_entry", "regulation"],
    },
    "visa_immigration": {
        "name_ja": "ビザ・在留資格・入管",
        "name_en": "Visa & Immigration",
        "description": "Complete visa and immigration guide: 29 status of residence categories, change/renewal procedures, permanent residency (eijuken) requirements, points-based preferential immigration (kodo jinzai), work permit categories, dependent visas, re-entry permits, immigration bureau procedures, and deportation avoidance.",
        "priority": "HIGH",
        "rationale": "Currently scattered across foreign_entry. Visa is THE #1 query for any foreign individual or company entering Japan. Deserves dedicated, comprehensive treatment.",
        "estimated_entries": 10,
        "source_authority": "official_gov",
        "key_sources": [
            "https://www.moj.go.jp/isa/ (出入国在留管理庁)",
            "https://www.mofa.go.jp/mofaj/toko/ (外務省 領事局)",
        ],
        "demand_signals": [
            "foreign_entry_check queries mentioning visa",
            "Protocol/regulation queries about management visa",
        ],
        "dependencies": ["foreign_entry"],
    },
    "banking_finance": {
        "name_ja": "銀行・金融・送金",
        "name_en": "Banking & Finance",
        "description": "Japanese banking for foreigners: bank account opening procedures (mega banks vs net banks vs JP Bank), inkan (seal) requirements, online banking setup, international wire transfers (including SWIFT/correspondent fees), credit card application (challenges for non-residents), mobile payments (PayPay, Suica, etc.), ATM usage guide, and foreign exchange regulations.",
        "priority": "HIGH",
        "rationale": "Bank account opening is the #2 pain point after visa. Currently a single procedure in foreign_entry but needs 5-8 detailed entries covering different scenarios.",
        "estimated_entries": 7,
        "source_authority": "official_gov",
        "key_sources": [
            "https://www.fsa.go.jp/ (金融庁)",
            "https://www.zenginkyo.or.jp/ (全国銀行協会)",
        ],
        "demand_signals": [
            "foreign_entry queries about bank accounts",
            "Daily life financial queries",
        ],
        "dependencies": ["foreign_entry", "daily_life"],
    },
    "healthcare_detailed": {
        "name_ja": "医療・健康保険・介護",
        "name_en": "Healthcare & Insurance",
        "description": "Japanese healthcare system in depth: National Health Insurance (NHI) vs Employee Health Insurance (shakai hoken), enrollment procedures, out-of-pocket costs (typically 30%), high-cost medical expense benefit (kougaku ryouyouhi), hospital visit etiquette, prescription system, mental health services, dental care, maternity/childcare benefits, and Long-Term Care Insurance (kaigo hoken).",
        "priority": "MEDIUM",
        "rationale": "Currently a single entry in daily_life. Healthcare is critical for long-term residents and deserves its own domain with detailed procedural knowledge.",
        "estimated_entries": 8,
        "source_authority": "official_gov",
        "key_sources": [
            "https://www.mhlw.go.jp/ (厚生労働省)",
            "https://www.kokuho.or.jp/ (国民健康保険中央会)",
        ],
        "demand_signals": [
            "daily_life_search queries about healthcare/insurance",
        ],
        "dependencies": ["daily_life"],
    },
    "education": {
        "name_ja": "教育・学校制度",
        "name_en": "Education System",
        "description": "Japanese education system: 6-3-3-4 structure, school enrollment for foreign children, international schools, Japanese language schools (nihongo gakkou), university admission (including for foreign students), student visa procedures, JLPT/EJU test guides, scholarship programs (MEXT, JASSO), and PTA participation culture.",
        "priority": "MEDIUM",
        "rationale": "Growing demand from expat families and international students. No current coverage. Japan is a top destination for language study.",
        "estimated_entries": 6,
        "source_authority": "official_gov",
        "key_sources": [
            "https://www.mext.go.jp/ (文部科学省)",
            "https://www.jasso.go.jp/ (日本学生支援機構)",
        ],
        "demand_signals": [
            "No direct telemetry yet — strategic expansion",
        ],
        "dependencies": [],
    },
    "real_estate_detailed": {
        "name_ja": "不動産・賃貸・住居",
        "name_en": "Real Estate & Housing",
        "description": "Japanese real estate in depth: apartment hunting vocabulary (1LDK, tatami, etc.), key money (reikin) and deposit (shikikin) explained, guarantor company (hoshounin) system, foreigner-friendly agencies, contract renewal procedures, move-in/move-out inspection, neighborhood association (jichikai/chonaikai), and property purchase guide for foreign buyers.",
        "priority": "MEDIUM",
        "rationale": "Currently touched in foreign_entry (property search) and daily_life but deserves dedicated deep coverage. Housing is the #3 pain point for foreigners.",
        "estimated_entries": 7,
        "source_authority": "domain_expert",
        "key_sources": [
            "https://www.mlit.go.jp/ (国土交通省)",
            "https://suumo.jp/ (不動産情報)",
        ],
        "demand_signals": [
            "foreign_entry queries about real estate",
            "daily_life queries about housing",
        ],
        "dependencies": ["foreign_entry", "daily_life"],
    },
}


class DomainExpansionPlanner:
    """Analyzes expansion candidates and prioritizes based on data signals."""

    def get_expansion_roadmap(self) -> dict:
        """Get full expansion roadmap with prioritized candidates."""
        high = [k for k, v in EXPANSION_CANDIDATES.items() if v["priority"] == "HIGH"]
        medium = [k for k, v in EXPANSION_CANDIDATES.items() if v["priority"] == "MEDIUM"]

        total_new_entries = sum(v["estimated_entries"] for v in EXPANSION_CANDIDATES.values())

        return {
            "current_domains": 14,
            "target_domains": 14 + len(EXPANSION_CANDIDATES),
            "expansion_candidates": len(EXPANSION_CANDIDATES),
            "total_new_entries_estimated": total_new_entries,
            "priority_order": {
                "high": high,
                "medium": medium,
            },
            "candidates": EXPANSION_CANDIDATES,
            "next_action": "Implement HIGH priority domains first (tax, visa_immigration, banking_finance)",
        }

    def get_candidate_detail(self, domain_id: str) -> Optional[dict]:
        """Get detailed info for a specific expansion candidate."""
        return EXPANSION_CANDIDATES.get(domain_id)

    def evaluate_demand_from_telemetry(self, db) -> dict:
        """Cross-reference telemetry data with expansion candidates.

        Looks for queries in existing domains that suggest demand for new domains.
        """
        from backend.api.models.analytics import ApiRequestLog
        from sqlalchemy import func, desc
        from datetime import datetime, timezone, timedelta

        since = datetime.now(timezone.utc) - timedelta(days=30)

        # Get all queries from the last 30 days
        queries = (
            db.query(ApiRequestLog.query_text, ApiRequestLog.domain, func.count().label("count"))
            .filter(
                ApiRequestLog.timestamp >= since,
                ApiRequestLog.query_text.isnot(None),
            )
            .group_by(ApiRequestLog.query_text, ApiRequestLog.domain)
            .order_by(desc(func.count()))
            .limit(100)
            .all()
        )

        # Check for expansion domain signals
        signals = {}
        tax_keywords = ["税", "tax", "確定申告", "消費税", "所得税", "e-tax"]
        visa_keywords = ["ビザ", "visa", "在留", "永住", "帰化", "入管"]
        banking_keywords = ["銀行", "bank", "送金", "口座", "クレジット", "payment"]
        healthcare_keywords = ["保険", "病院", "医療", "healthcare", "doctor"]
        education_keywords = ["学校", "大学", "教育", "留学", "jlpt"]
        housing_keywords = ["賃貸", "apartment", "不動産", "引越", "家賃"]

        keyword_map = {
            "tax": tax_keywords,
            "visa_immigration": visa_keywords,
            "banking_finance": banking_keywords,
            "healthcare_detailed": healthcare_keywords,
            "education": education_keywords,
            "real_estate_detailed": housing_keywords,
        }

        for candidate_id, keywords in keyword_map.items():
            matching_queries = []
            for q in queries:
                if q.query_text and any(kw in q.query_text.lower() for kw in keywords):
                    matching_queries.append({
                        "query": q.query_text,
                        "current_domain": q.domain,
                        "count": q.count,
                    })
            signals[candidate_id] = {
                "matching_queries": matching_queries,
                "signal_strength": len(matching_queries),
                "recommendation": (
                    "STRONG — implement now" if len(matching_queries) >= 3
                    else "MODERATE — plan for next sprint" if len(matching_queries) >= 1
                    else "LOW — monitor"
                ),
            }

        return {
            "analysis_date": date.today().isoformat(),
            "period_days": 30,
            "total_queries_analyzed": len(queries),
            "domain_signals": signals,
        }


# ── Module singleton ──
expansion_planner = DomainExpansionPlanner()
