"""Business protocol service — Japanese business customs and practices."""
import logging
from typing import Optional

from backend.api.services.kb_loader import load_domain

logger = logging.getLogger(__name__)

PROTOCOL_DB, PROTOCOL_KEYWORDS = load_domain("protocol")


class ProtocolService:
    """Japanese business protocol lookup service."""

    def check(self, query: str, category: Optional[str] = None) -> dict:
        """Look up business protocol by query or category."""
        # 1. Direct category match
        if category and category in PROTOCOL_DB:
            return self._format_result(category)

        # 2. Keyword match
        matched = self._match_protocol(query or "")
        if matched:
            return self._format_result(matched)

        # 3. No match
        return {
            "matched_protocol": None,
            "message": f"'{query}' に該当するビジネスプロトコルが見つかりませんでした。",
            "available_protocols": self.list_protocols(),
            "confidence": 0.0,
        }

    def list_protocols(self) -> list[dict]:
        """List all available protocols."""
        return [
            {
                "id": pid,
                "name_ja": data["name_ja"],
                "name_en": data["name_en"],
                "category": data["category"],
                "importance": data["importance"],
                "summary": data["summary"],
            }
            for pid, data in PROTOCOL_DB.items()
        ]

    def get_protocol(self, protocol_id: str) -> Optional[dict]:
        """Get full detail for a specific protocol."""
        if protocol_id in PROTOCOL_DB:
            return self._format_result(protocol_id)
        return None

    def _format_result(self, protocol_id: str) -> dict:
        """Format a protocol result."""
        data = PROTOCOL_DB[protocol_id]
        result = {
            "protocol_id": protocol_id,
            **data,
            "confidence": 0.95,
            "source": "EDITION knowledge base (business protocols)",
            "disclaimer": "この情報は一般的なビジネス慣習に基づく参考情報です。企業・業界により慣習は異なります。",
        }
        return result

    def _match_protocol(self, query: str) -> Optional[str]:
        """Match query text to a protocol."""
        search_text = query.lower()
        best_match = None
        best_score = 0
        for pid, keywords in PROTOCOL_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in search_text)
            if score > best_score:
                best_score = score
                best_match = pid
        return best_match if best_score > 0 else None
