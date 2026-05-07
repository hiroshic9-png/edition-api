"""Fact extraction service — LLM-powered knowledge extraction from Japanese text.

The core differentiator: extracting structured facts from Japanese text
while understanding keigo, subject omission, implicit agreement, and
social hierarchy — things Mem0/Letta/Zep cannot do.
"""
import json
import os
import re
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── System prompt for Japanese fact extraction ─────────────────

EXTRACTION_SYSTEM_PROMPT = """あなたは日本語テキストから構造化された事実（Fact）を抽出する専門家です。

## 抽出ルール

1. テキストから「主語 → 述語 → 目的語」の三つ組（トリプル）を抽出してください
2. 以下の日本語特有の要素を分析してください:
   - **主語省略**: 日本語では主語が省略されることが多い。文脈から推定してください
   - **敬語レベル**: 丁寧語(1) / 尊敬語(2) / 謙譲語(3) を判定
   - **社会的関係**: 話者と対象者の上下関係を推定
   - **確度**: 断定(1.0) / 推測(0.7) / 伝聞(0.5) / 否定的推測(0.3)
   - **時制**: 過去の事実 / 現在の状態 / 未来の予定・意図

3. 以下は事実として抽出しないでください:
   - 挨拶や社交辞令
   - 一般的な知識（「東京は日本の首都」など）
   - 曖昧すぎて構造化できない発言

## 出力フォーマット

JSON配列で出力してください。各要素:
```json
{
  "subject": "主語（人名、組織名、事物）",
  "predicate": "述語（動詞・形容詞の辞書形）",
  "object": "目的語・補語",
  "confidence": 0.0-1.0,
  "category": "preference|agreement|relationship|status|plan|attribute",
  "keigo_level": 0-3,
  "social_hierarchy": "superior|peer|subordinate|unknown",
  "tense": "past|present|future",
  "reasoning": "抽出の根拠を簡潔に"
}
```

事実が抽出できない場合は空配列 `[]` を返してください。"""

EXTRACTION_USER_TEMPLATE = """以下のテキストから事実を抽出してください:

テキスト: {text}

{context_hint}

JSON配列のみを出力してください。他のテキストは不要です。"""


# ── LLM Client abstraction ─────────────────────────────────────

class LLMClient:
    """Abstraction over LLM providers (OpenAI / Anthropic)."""

    def __init__(self):
        self.provider = None
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize with available API key."""
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if anthropic_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=anthropic_key)
                self.provider = "anthropic"
                logger.info("LLM provider: Anthropic (Claude)")
                return
            except ImportError:
                logger.warning("anthropic package not installed")

        if openai_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=openai_key)
                self.provider = "openai"
                logger.info("LLM provider: OpenAI")
                return
            except ImportError:
                logger.warning("openai package not installed")

        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=gemini_key)
                self.provider = "gemini"
                logger.info("LLM provider: Google Gemini")
                return
            except ImportError:
                logger.warning("google-genai package not installed")

        self.provider = "fallback"
        logger.warning("No LLM API key found. Using rule-based fallback extraction.")

    def generate(self, system: str, user: str) -> str:
        """Generate a response from the LLM."""
        if self.provider == "anthropic":
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return response.content[0].text

        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=2000,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return response.choices[0].message.content

        elif self.provider == "gemini":
            combined = f"{system}\n\n{user}"
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=combined,
            )
            return response.text

        else:
            return self._fallback_extract(user)

    def _fallback_extract(self, text: str) -> str:
        """Rule-based fallback when no LLM is available."""
        return "[]"


# ── Extraction Service ──────────────────────────────────────────

class ExtractionService:
    """Extract structured facts from Japanese text using LLM."""

    def __init__(self):
        self.llm = LLMClient()

    def extract_facts(
        self,
        text: str,
        context_hint: str = "",
    ) -> list[dict]:
        """Extract facts from text.

        Args:
            text: The text to extract facts from
            context_hint: Optional context (e.g., "This is a business meeting about...")

        Returns:
            List of extracted fact dicts
        """
        if self.llm.provider == "fallback":
            return self._rule_based_extract(text)

        user_prompt = EXTRACTION_USER_TEMPLATE.format(
            text=text,
            context_hint=f"コンテキスト: {context_hint}" if context_hint else "",
        )

        try:
            raw_response = self.llm.generate(EXTRACTION_SYSTEM_PROMPT, user_prompt)
            facts = self._parse_response(raw_response)
            return facts
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self._rule_based_extract(text)

    def _parse_response(self, response: str) -> list[dict]:
        """Parse LLM response into fact list."""
        # Try to find JSON array in response
        response = response.strip()

        # Remove markdown code fences if present
        if response.startswith("```"):
            response = re.sub(r'^```\w*\n?', '', response)
            response = re.sub(r'\n?```$', '', response)
            response = response.strip()

        try:
            facts = json.loads(response)
            if isinstance(facts, list):
                return [self._validate_fact(f) for f in facts if self._validate_fact(f)]
            return []
        except json.JSONDecodeError:
            # Try to find JSON array in the response
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                try:
                    facts = json.loads(match.group())
                    return [self._validate_fact(f) for f in facts if self._validate_fact(f)]
                except json.JSONDecodeError:
                    pass
            logger.warning(f"Could not parse LLM response as JSON: {response[:200]}")
            return []

    def _validate_fact(self, fact: dict) -> Optional[dict]:
        """Validate and normalize a fact dict."""
        required = ["subject", "predicate", "object"]
        if not all(k in fact and fact[k] for k in required):
            return None

        return {
            "subject": str(fact["subject"]).strip(),
            "predicate": str(fact["predicate"]).strip(),
            "object": str(fact["object"]).strip(),
            "confidence": float(fact.get("confidence", 0.8)),
            "category": fact.get("category", "unknown"),
            "metadata": {
                "keigo_level": fact.get("keigo_level", 0),
                "social_hierarchy": fact.get("social_hierarchy", "unknown"),
                "tense": fact.get("tense", "present"),
                "reasoning": fact.get("reasoning", ""),
                "extraction_method": "llm" if self.llm.provider != "fallback" else "rule_based",
            },
        }

    def _rule_based_extract(self, text: str) -> list[dict]:
        """Simple rule-based extraction as fallback (no LLM needed).

        Handles common Japanese patterns:
        - 「XはYです」 (X is Y)
        - 「XがYを好む」 (X likes Y)
        - 「XとYで合意」 (agreed on X and Y)
        """
        facts = []

        # Pattern: 〇〇は△△です / 〇〇は△△だ
        pattern_desu = re.compile(r'(.{1,20})[はが](.{1,30})[でだ](?:す|ある)')
        for match in pattern_desu.finditer(text):
            facts.append({
                "subject": match.group(1).strip(),
                "predicate": "である",
                "object": match.group(2).strip(),
                "confidence": 0.6,
                "category": "attribute",
                "metadata": {
                    "extraction_method": "rule_based",
                    "pattern": "XはYです",
                },
            })

        # Pattern: 合意 / 決定 / 確定
        agreement_words = ["合意", "決定", "確定", "決めた", "決まった"]
        for word in agreement_words:
            if word in text:
                facts.append({
                    "subject": "（参加者）",
                    "predicate": word,
                    "object": text[:50].strip(),
                    "confidence": 0.5,
                    "category": "agreement",
                    "metadata": {
                        "extraction_method": "rule_based",
                        "pattern": "agreement_keyword",
                    },
                })
                break

        # Pattern: 好き / 好む / 好み
        pref_words = ["好き", "好む", "好み", "お気に入り"]
        for word in pref_words:
            if word in text:
                facts.append({
                    "subject": "（対象者）",
                    "predicate": "好む",
                    "object": text[:50].strip(),
                    "confidence": 0.5,
                    "category": "preference",
                    "metadata": {
                        "extraction_method": "rule_based",
                        "pattern": "preference_keyword",
                    },
                })
                break

        return facts


# Singleton
_extraction_service: Optional[ExtractionService] = None


def get_extraction_service() -> ExtractionService:
    global _extraction_service
    if _extraction_service is None:
        _extraction_service = ExtractionService()
    return _extraction_service
