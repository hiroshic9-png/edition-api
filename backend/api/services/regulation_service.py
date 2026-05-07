"""Regulation service — Japan regulatory compliance check with RAG.

Architecture:
  1. Static knowledge base lookup (fast, high confidence)
  2. LLM-powered RAG fallback (broader coverage, lower confidence)
  3. Source citations and confidence scoring
"""
import logging
from typing import Optional

from backend.api.services.regulation_kb import (
    REGULATION_DB,
    TOURIST_REGULATIONS,
    INDUSTRY_KEYWORDS,
    TOURIST_KEYWORDS,
)

logger = logging.getLogger(__name__)

# ── LLM RAG prompt ────────────────────────────────────

RAG_SYSTEM_PROMPT = """あなたは日本の規制・法令に関する専門家アシスタントです。

## ルール
1. 質問に対して、日本の法令・規制に基づいた回答を提供してください
2. 回答には必ず「確度」を付与してください（あなたが確信している度合い）
3. 法的助言ではなく、参考情報であることを明記してください
4. 不確かな情報は「不確か」と明記してください。推測で断言しないでください
5. 関連する法令名を可能な限り挙げてください
6. 外国企業/外国人に関する質問の場合は、在留資格・ビザ関連の注意事項も含めてください

## 出力フォーマット（JSON）
```json
{
  "matched_industry": "該当する業種名（特定できない場合はnull）",
  "summary": "回答の要約（2-3文）",
  "licenses_required": ["必要な許認可のリスト"],
  "governing_body": "管轄省庁",
  "governing_law": "根拠法令",
  "requirements": ["主な要件のリスト"],
  "estimated_timeline": "取得にかかる期間の目安",
  "penalties": "違反時の罰則",
  "confidence": 0.0-1.0,
  "caveats": ["注意事項のリスト"],
  "foreign_company_notes": "外国企業向けの追加情報（該当する場合）"
}
```

JSONのみを出力してください。"""

RAG_USER_TEMPLATE = """以下の質問に回答してください:

アクション: {action}
業種: {industry}
主体: {entity_type_ja}

{context}

JSON形式で回答してください。"""


class RegulationService:
    """Japan regulatory compliance check service."""

    def __init__(self):
        self._llm = None

    def _get_llm(self):
        """Lazy init LLM client."""
        if self._llm is None:
            try:
                from backend.api.services.extraction import LLMClient
                self._llm = LLMClient()
            except Exception as e:
                logger.warning(f"Could not init LLM for regulation service: {e}")
        return self._llm

    # ── Main check endpoint ───────────────────────────

    def check(
        self,
        action: str,
        industry: Optional[str] = None,
        entity_type: str = "foreign_company",
    ) -> dict:
        """Check regulations for a given action/industry.

        Strategy:
          1. Try static KB match (high confidence)
          2. Try tourist regulation match (if entity_type is tourist)
          3. Fall back to LLM RAG (broader but lower confidence)
        """
        # 1. Tourist-specific check
        if entity_type == "tourist":
            tourist_result = self._check_tourist(action)
            if tourist_result:
                return tourist_result

        # 2. Static KB match
        matched_industry = self._match_industry(action, industry)
        if matched_industry and matched_industry in REGULATION_DB:
            return self._format_kb_result(matched_industry, entity_type)

        # 3. Tourist regulation check (even for non-tourist entity types)
        tourist_result = self._check_tourist(action)
        if tourist_result:
            return tourist_result

        # 4. LLM RAG fallback
        llm_result = self._llm_check(action, industry, entity_type)
        if llm_result:
            return llm_result

        # 5. No match
        return {
            "matched_industry": None,
            "message": f"'{action}' に該当する規制情報が見つかりませんでした。",
            "suggestion": "対応業種: " + ", ".join(sorted(REGULATION_DB.keys())),
            "tourist_categories": list(TOURIST_REGULATIONS.keys()),
            "confidence": 0.0,
            "disclaimer": "この情報は参考用です。法的助言ではありません。",
        }

    # ── Tourist regulation check ──────────────────────

    def _check_tourist(self, action: str) -> Optional[dict]:
        """Check tourist-specific regulations."""
        matched = self._match_tourist_category(action)
        if not matched:
            return None

        reg = TOURIST_REGULATIONS[matched]
        result = {
            "category": "tourist",
            "matched_topic": matched,
            "overview": reg["overview"],
            "key_rules": reg["key_rules"],
            "confidence": 0.9,
            "source": "japan-ops knowledge base (tourist regulations)",
            "disclaimer": "この情報は参考用です。最新の規則は公式情報を確認してください。",
        }
        if "penalties" in reg:
            result["penalties"] = reg["penalties"]
        if "recent_changes" in reg:
            result["recent_changes"] = reg["recent_changes"]
        return result

    # ── Static KB result formatting ───────────────────

    def _format_kb_result(self, industry: str, entity_type: str) -> dict:
        """Format a static knowledge base result."""
        reg = REGULATION_DB[industry]
        result = {
            "matched_industry": industry,
            "licenses_required": reg["licenses"],
            "governing_body": reg["governing_body"],
            "governing_law": reg.get("governing_law", ""),
            "requirements": reg["requirements"],
            "estimated_timeline": reg["timeline"],
            "penalties_for_non_compliance": reg["penalties"],
            "costs": reg.get("costs", ""),
            "renewal": reg.get("renewal", ""),
            "confidence": 0.9,
            "source": "japan-ops knowledge base",
            "references": reg.get("references", []),
            "disclaimer": "この情報は参考用です。法的助言ではありません。最新の法令を確認し、専門家にご相談ください。",
        }

        if reg.get("recent_changes"):
            result["recent_changes"] = reg["recent_changes"]

        if entity_type == "foreign_company" and reg.get("foreign_company_notes"):
            result["foreign_company_notes"] = reg["foreign_company_notes"]

        if entity_type == "tourist" and reg.get("tourist_relevance"):
            result["tourist_relevance"] = reg["tourist_relevance"]

        return result

    # ── LLM RAG fallback ──────────────────────────────

    def _llm_check(self, action: str, industry: Optional[str], entity_type: str) -> Optional[dict]:
        """Use LLM to answer regulation questions not in the KB."""
        llm = self._get_llm()
        if not llm or llm.provider == "fallback":
            return None

        entity_type_ja = {
            "foreign_company": "外国企業",
            "domestic_company": "日本企業",
            "individual": "個人",
            "tourist": "訪日旅行者",
        }.get(entity_type, entity_type)

        # Provide KB context to LLM for grounding
        kb_context = "参考: 当システムのナレッジベースには以下の業種が登録されています:\n"
        kb_context += ", ".join(sorted(REGULATION_DB.keys()))

        user_prompt = RAG_USER_TEMPLATE.format(
            action=action,
            industry=industry or "不明",
            entity_type_ja=entity_type_ja,
            context=kb_context,
        )

        try:
            import json, re
            raw = llm.generate(RAG_SYSTEM_PROMPT, user_prompt)
            raw = raw.strip()
            if raw.startswith("```"):
                raw = re.sub(r'^```\w*\n?', '', raw)
                raw = re.sub(r'\n?```$', '', raw)
                raw = raw.strip()

            result = json.loads(raw)
            result["source"] = "LLM-generated (lower confidence)"
            result["disclaimer"] = "この情報はAIが生成した参考情報です。法的助言ではありません。正確性を保証するものではないため、必ず専門家にご確認ください。"
            # Cap LLM confidence
            if "confidence" in result:
                result["confidence"] = min(float(result["confidence"]), 0.7)
            return result
        except Exception as e:
            logger.error(f"LLM regulation check failed: {e}")
            return None

    # ── Listings ──────────────────────────────────────

    def list_industries(self) -> list[dict]:
        """List all supported industries with detail."""
        return [
            {
                "industry": name,
                "licenses": data["licenses"],
                "governing_body": data["governing_body"],
                "governing_law": data.get("governing_law", ""),
                "costs": data.get("costs", ""),
            }
            for name, data in sorted(REGULATION_DB.items())
        ]

    def list_tourist_categories(self) -> list[dict]:
        """List tourist regulation categories."""
        return [
            {
                "category": name,
                "overview": data["overview"],
            }
            for name, data in TOURIST_REGULATIONS.items()
        ]

    def get_industry_detail(self, industry: str) -> Optional[dict]:
        """Get full detail for a specific industry."""
        if industry in REGULATION_DB:
            return self._format_kb_result(industry, "foreign_company")
        return None

    def get_tourist_detail(self, category: str) -> Optional[dict]:
        """Get full detail for a tourist regulation category."""
        if category in TOURIST_REGULATIONS:
            return self._check_tourist(category)
        return None

    # ── Matching helpers ──────────────────────────────

    def _match_industry(self, action: str, industry: Optional[str]) -> Optional[str]:
        """Match action/industry text to a known industry."""
        search_text = f"{action} {industry or ''}".lower()

        # Exact match first
        for ind_name in REGULATION_DB:
            if ind_name.lower() in search_text:
                return ind_name

        # Keyword match
        best_match = None
        best_score = 0
        for ind_name, keywords in INDUSTRY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in search_text)
            if score > best_score:
                best_score = score
                best_match = ind_name

        return best_match if best_score > 0 else None

    def _match_tourist_category(self, action: str) -> Optional[str]:
        """Match action text to a tourist regulation category."""
        search_text = action.lower()

        best_match = None
        best_score = 0
        for cat_name, keywords in TOURIST_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in search_text)
            if score > best_score:
                best_score = score
                best_match = cat_name

        return best_match if best_score > 0 else None
