"""Calendar service — Japanese business calendar and seasonal awareness."""
import logging
from datetime import date
from typing import Optional

from backend.api.services.calendar_kb import CALENDAR_DB, CALENDAR_KEYWORDS

logger = logging.getLogger(__name__)


class CalendarService:
    """Japanese business calendar lookup service."""

    def check(self, query: str, category: Optional[str] = None) -> dict:
        if category and category in CALENDAR_DB:
            return self._format_result(category)

        matched = self._match_category(query or "")
        if matched:
            return self._format_result(matched)

        return {
            "matched_category": None,
            "message": f"'{query}' に該当するカレンダー情報が見つかりませんでした。",
            "available_categories": self.list_categories(),
            "confidence": 0.0,
        }

    def list_categories(self) -> list[dict]:
        return [
            {
                "id": cid,
                "name_ja": data["name_ja"],
                "name_en": data["name_en"],
                "category": data["category"],
                "summary": data["summary"],
            }
            for cid, data in CALENDAR_DB.items()
        ]

    def get_category(self, category_id: str) -> Optional[dict]:
        if category_id in CALENDAR_DB:
            return self._format_result(category_id)
        return None

    def _format_result(self, category_id: str) -> dict:
        data = CALENDAR_DB[category_id]
        return {
            "category_id": category_id,
            **data,
            "confidence": 0.95,
            "source": "EDITION knowledge base (calendar)",
            "disclaimer": "祝日の日付は年により変動する場合があります。最新の暦は内閣府のサイトで確認してください。",
        }

    def _match_category(self, query: str) -> Optional[str]:
        search_text = query.lower()
        best_match = None
        best_score = 0
        for cid, keywords in CALENDAR_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in search_text)
            if score > best_score:
                best_score = score
                best_match = cid
        return best_match if best_score > 0 else None
