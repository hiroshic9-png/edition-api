"""Cross-domain search service — queries all knowledge domains at once."""
import logging
from typing import Optional

from backend.api.services.regulation_service import RegulationService
from backend.api.services.protocol_service import ProtocolService
from backend.api.services.calendar_service import CalendarService
from backend.api.services.regional_service import RegionalService
from backend.api.services.organization_service import OrganizationService
from backend.api.services.foreign_entry_service import ForeignEntryService
from backend.api.services.travel_service import search_travel
from backend.api.services.entertainment_service import search_entertainment
from backend.api.services.daily_life_service import search_daily_life
from backend.api.services.language_service import search_language
from backend.api.services.food_service import search_food
from backend.api.services.disaster_service import search_disaster

logger = logging.getLogger(__name__)


def _search_keyword_domain(search_fn, domain_name, query, limit, results, domain_hits):
    """Helper to search a keyword-based domain (travel/entertainment/daily_life/etc)."""
    try:
        res = search_fn(query)
        if res and res.get("total_matches", 0) > 0:
            top = res["results"][0]
            results[domain_name] = {
                "matched": True,
                "name_ja": top.get("name_ja", ""),
                "summary": top.get("summary", ""),
                "topics": [r["topic"] for r in res.get("results", [])[:limit]],
                "total_matches": res.get("total_matches", 0),
                "confidence": min(top.get("relevance_score", 1) * 0.3, 1.0),
            }
            domain_hits[0] += 1
    except Exception as e:
        logger.warning(f"{domain_name} search failed: {e}")


class SearchService:
    """Unified search across all EDITION knowledge domains."""

    def __init__(self):
        self.regulation = RegulationService()
        self.protocol = ProtocolService()
        self.calendar = CalendarService()
        self.regional = RegionalService()
        self.organization = OrganizationService()
        self.foreign_entry = ForeignEntryService()

    def search(self, query: str, limit: int = 3) -> dict:
        """Search all domains for the given query and return combined results."""
        results = {}
        domain_hits = [0]  # mutable for helper

        # 1. Regulation — try to match industry
        try:
            reg = self.regulation.check(action=query, industry=query)
            if reg and reg.get("confidence", 0) > 0:
                results["regulation"] = {
                    "matched": True,
                    "industry": reg.get("matched_industry"),
                    "licenses": reg.get("licenses_required", []),
                    "governing_body": reg.get("governing_body"),
                    "procedures_count": reg.get("procedures_count", 0),
                    "confidence": reg.get("confidence", 0),
                }
                domain_hits[0] += 1
        except Exception as e:
            logger.warning(f"Regulation search failed: {e}")

        # 2. Protocol
        try:
            proto = self.protocol.check(query)
            if proto and proto.get("confidence", 0) > 0:
                results["protocol"] = {
                    "matched": True,
                    "protocol_id": proto.get("protocol_id"),
                    "name_ja": proto.get("name_ja"),
                    "summary": proto.get("summary"),
                    "confidence": proto.get("confidence", 0),
                }
                domain_hits[0] += 1
        except Exception as e:
            logger.warning(f"Protocol search failed: {e}")

        # 3. Calendar
        try:
            cal = self.calendar.check(query)
            if cal and cal.get("confidence", 0) > 0:
                results["calendar"] = {
                    "matched": True,
                    "category_id": cal.get("category_id"),
                    "name_ja": cal.get("name_ja"),
                    "summary": cal.get("summary"),
                    "confidence": cal.get("confidence", 0),
                }
                domain_hits[0] += 1
        except Exception as e:
            logger.warning(f"Calendar search failed: {e}")

        # 4. Regional
        try:
            reg = self.regional.check(query)
            if reg and reg.get("confidence", 0) > 0:
                results["regional"] = {
                    "matched": True,
                    "category_id": reg.get("category_id"),
                    "name_ja": reg.get("name_ja"),
                    "summary": reg.get("summary"),
                    "confidence": reg.get("confidence", 0),
                }
                domain_hits[0] += 1
        except Exception as e:
            logger.warning(f"Regional search failed: {e}")

        # 5. Organization
        try:
            org = self.organization.check(query)
            if org and org.get("confidence", 0) > 0:
                results["organization"] = {
                    "matched": True,
                    "category_id": org.get("category_id"),
                    "name_ja": org.get("name_ja"),
                    "summary": org.get("summary"),
                    "confidence": org.get("confidence", 0),
                }
                domain_hits[0] += 1
        except Exception as e:
            logger.warning(f"Organization search failed: {e}")

        # 6. Foreign Entry
        try:
            fe = self.foreign_entry.check(query=query)
            if fe and fe.get("confidence", 0) > 0:
                results["foreign_entry"] = {
                    "matched": True,
                    "category_id": fe.get("category_id"),
                    "name_ja": fe.get("name_ja"),
                    "summary": fe.get("summary"),
                    "confidence": fe.get("confidence", 0),
                }
                domain_hits[0] += 1
        except Exception as e:
            logger.warning(f"Foreign entry search failed: {e}")

        # 7-12. Keyword-based domains
        for fn, name in [
            (search_travel, "travel"),
            (search_entertainment, "entertainment"),
            (search_daily_life, "daily_life"),
            (search_language, "language"),
            (search_food, "food"),
            (search_disaster, "disaster"),
        ]:
            _search_keyword_domain(fn, name, query, limit, results, domain_hits)

        return {
            "query": query,
            "domains_searched": 12,
            "domains_matched": domain_hits[0],
            "results": results,
            "source": "EDITION cross-domain search",
        }
