"""Organization service — Japanese corporate structure and business practices."""
import logging
from typing import Optional

from backend.api.services.kb_loader import load_domain

logger = logging.getLogger(__name__)

ORGANIZATION_DB, ORGANIZATION_KEYWORDS = load_domain("organization")


class OrganizationService:
    """Japanese organization and corporate structure lookup service."""

    def check(self, query: str, category: Optional[str] = None) -> dict:
        if category and category in ORGANIZATION_DB:
            return self._format_result(category)
        matched = self._match_category(query or "")
        if matched:
            return self._format_result(matched)
        return {
            "matched_category": None,
            "message": f"'{query}' に該当する組織構造情報が見つかりませんでした。",
            "available_categories": self.list_categories(),
            "confidence": 0.0,
        }

    def list_categories(self) -> list[dict]:
        return [
            {"id": cid, "name_ja": d["name_ja"], "name_en": d["name_en"], "category": d["category"], "summary": d["summary"]}
            for cid, d in ORGANIZATION_DB.items()
        ]

    def get_category(self, category_id: str) -> Optional[dict]:
        if category_id in ORGANIZATION_DB:
            return self._format_result(category_id)
        return None

    def _format_result(self, category_id: str) -> dict:
        data = ORGANIZATION_DB[category_id]
        return {
            "category_id": category_id, **data,
            "confidence": 0.95,
            "source": "EDITION knowledge base (organization)",
            "disclaimer": "この情報は一般的な日本企業の慣行に基づきます。企業・業界により異なります。",
        }

    def _match_category(self, query: str) -> Optional[str]:
        search_text = query.lower()
        best_match, best_score = None, 0
        for cid, keywords in ORGANIZATION_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in search_text)
            if score > best_score:
                best_score = score
                best_match = cid
        return best_match if best_score > 0 else None
