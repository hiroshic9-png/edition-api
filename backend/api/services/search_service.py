"""Cross-domain search service — queries all knowledge domains at once."""
import logging
from typing import Optional

from backend.api.services.regulation_service import RegulationService
from backend.api.services.protocol_service import ProtocolService
from backend.api.services.calendar_service import CalendarService
from backend.api.services.regional_service import RegionalService
from backend.api.services.organization_service import OrganizationService
from backend.api.services.foreign_entry_service import ForeignEntryService

logger = logging.getLogger(__name__)


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
        domain_hits = 0

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
                domain_hits += 1
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
                domain_hits += 1
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
                domain_hits += 1
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
                domain_hits += 1
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
                domain_hits += 1
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
                domain_hits += 1
        except Exception as e:
            logger.warning(f"Foreign entry search failed: {e}")

        return {
            "query": query,
            "domains_searched": 6,
            "domains_matched": domain_hits,
            "results": results,
            "source": "EDITION cross-domain search",
        }
