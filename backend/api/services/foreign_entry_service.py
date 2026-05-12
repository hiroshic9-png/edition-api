"""Foreign entry service — Japan market entry knowledge for foreign companies."""
import logging
from typing import Optional
from backend.api.services.kb_loader import load_domain

logger = logging.getLogger(__name__)

FOREIGN_ENTRY_DB, FOREIGN_ENTRY_KEYWORDS = load_domain("foreign_entry")


class ForeignEntryService:
    def check(self, query: str, category: Optional[str] = None) -> dict:
        if category and category in FOREIGN_ENTRY_DB:
            return self._format(category)
        matched = self._match(query or "")
        if matched:
            return self._format(matched)
        return {"matched_category": None, "message": f"'{query}' に該当する情報が見つかりませんでした。", "available_categories": self.list_categories(), "confidence": 0.0}

    def list_categories(self) -> list[dict]:
        return [{"id": k, "name_ja": v["name_ja"], "name_en": v["name_en"], "category": v["category"], "summary": v["summary"]} for k, v in FOREIGN_ENTRY_DB.items()]

    def get_category(self, cid: str) -> Optional[dict]:
        return self._format(cid) if cid in FOREIGN_ENTRY_DB else None

    def _format(self, cid: str) -> dict:
        return {"category_id": cid, **FOREIGN_ENTRY_DB[cid], "confidence": 0.95, "source": "EDITION knowledge base (foreign entry)", "disclaimer": "この情報は一般的なガイダンスです。個別の状況により異なります。行政書士・弁護士への相談を推奨します。"}

    def _match(self, query: str) -> Optional[str]:
        s = query.lower()
        best, score = None, 0
        for k, kws in FOREIGN_ENTRY_KEYWORDS.items():
            c = sum(1 for w in kws if w.lower() in s)
            if c > score:
                score, best = c, k
        return best if score > 0 else None
