"""Regional service — Japanese regional differences for business."""
import logging
from typing import Optional
from backend.api.services.kb_loader import load_domain

logger = logging.getLogger(__name__)

REGIONAL_DB, REGIONAL_KEYWORDS = load_domain("regional")


class RegionalService:
    def check(self, query: str, category: Optional[str] = None) -> dict:
        if category and category in REGIONAL_DB:
            return self._format_result(category)
        matched = self._match(query or "")
        if matched:
            return self._format_result(matched)
        return {"matched_category": None, "message": f"'{query}' に該当する地域情報が見つかりませんでした。", "available_categories": self.list_categories(), "confidence": 0.0}

    def list_categories(self) -> list[dict]:
        return [{"id": k, "name_ja": v["name_ja"], "name_en": v["name_en"], "category": v["category"], "summary": v["summary"]} for k, v in REGIONAL_DB.items()]

    def get_category(self, cid: str) -> Optional[dict]:
        return self._format_result(cid) if cid in REGIONAL_DB else None

    def _format_result(self, cid: str) -> dict:
        return {"category_id": cid, **REGIONAL_DB[cid], "confidence": 0.95, "source": "EDITION knowledge base (regional)", "disclaimer": "地域の規制・助成金は頻繁に変更されます。最新情報は各自治体に確認してください。"}

    def _match(self, query: str) -> Optional[str]:
        s = query.lower()
        best, score = None, 0
        for k, kws in REGIONAL_KEYWORDS.items():
            c = sum(1 for w in kws if w.lower() in s)
            if c > score:
                score, best = c, k
        return best if score > 0 else None
