"""Context generation service — LLM-powered context summary.

Generates session_state.md-equivalent summaries from active facts and recent episodes.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

CONTEXT_SYSTEM_PROMPT = """あなたは会話の文脈を簡潔に要約する専門家です。

与えられた「現在有効な事実」と「直近のやり取り」から、エージェントが次の対話に必要な文脈サマリーを生成してください。

## 出力ルール
1. 重要度の高い情報を先に記載
2. 合意事項・決定事項は [DECISION] タグ付き
3. 未解決の課題は [OPEN] タグ付き
4. 人間関係・社会的階層に関する情報があれば明記
5. 簡潔に、箇条書きで
6. 日本語で出力"""

CONTEXT_USER_TEMPLATE = """以下の情報から文脈サマリーを生成してください:

## 現在有効な事実
{facts_text}

## 直近のやり取り
{episodes_text}

簡潔な文脈サマリーを出力してください。"""


class ContextGenerator:
    """Generate rich context summaries using LLM."""

    def __init__(self):
        self.llm = None
        self._init_llm()

    def _init_llm(self):
        """Lazy init LLM client."""
        try:
            from backend.api.services.extraction import LLMClient
            self.llm = LLMClient()
        except Exception as e:
            logger.warning(f"Could not init LLM for context generation: {e}")

    def generate(
        self,
        facts: list,
        episodes: list,
        use_llm: bool = True,
    ) -> str:
        """Generate context summary.

        Args:
            facts: List of Fact objects
            episodes: List of Episode objects
            use_llm: Whether to use LLM (falls back to template if False or unavailable)
        """
        if not facts and not episodes:
            return "記憶なし — まだやり取りが記録されていません。"

        # Always generate template-based summary
        template_summary = self._template_summary(facts, episodes)

        # Try LLM enhancement if available
        if use_llm and self.llm and self.llm.provider != "fallback":
            try:
                facts_text = self._format_facts(facts)
                episodes_text = self._format_episodes(episodes)

                user_prompt = CONTEXT_USER_TEMPLATE.format(
                    facts_text=facts_text or "（なし）",
                    episodes_text=episodes_text or "（なし）",
                )
                llm_summary = self.llm.generate(CONTEXT_SYSTEM_PROMPT, user_prompt)
                return llm_summary
            except Exception as e:
                logger.warning(f"LLM context generation failed, using template: {e}")

        return template_summary

    def _template_summary(self, facts: list, episodes: list) -> str:
        """Template-based summary (no LLM needed)."""
        lines = []

        # Group facts by category
        decisions = []
        preferences = []
        others = []

        for f in facts:
            meta = f.metadata_ or {} if hasattr(f, 'metadata_') else {}
            cat = meta.get("category", "unknown")
            fact_line = f"- {f.subject} → {f.predicate} → {f.object_}"
            if f.confidence < 1.0:
                fact_line += f" (確度: {f.confidence:.0%})"

            if cat == "agreement":
                decisions.append(fact_line)
            elif cat == "preference":
                preferences.append(fact_line)
            else:
                others.append(fact_line)

        if decisions:
            lines.append("## [DECISION] 合意事項")
            lines.extend(decisions)

        if preferences:
            lines.append("\n## 嗜好・好み")
            lines.extend(preferences)

        if others:
            lines.append("\n## その他の事実")
            lines.extend(others)

        if not (decisions or preferences or others) and facts:
            lines.append("## 現在有効な事実")
            for f in facts[:20]:
                conf_str = f" (確度: {f.confidence:.0%})" if f.confidence < 1.0 else ""
                lines.append(f"- {f.subject} → {f.predicate} → {f.object_}{conf_str}")

        if episodes:
            lines.append("\n## 直近のやり取り")
            for e in episodes[:5]:
                preview = e.content[:100] + "..." if len(e.content) > 100 else e.content
                lines.append(f"- [{e.role}] {preview}")

        return "\n".join(lines) if lines else "記憶なし"

    def _format_facts(self, facts: list) -> str:
        lines = []
        for f in facts[:30]:
            meta = f.metadata_ or {} if hasattr(f, 'metadata_') else {}
            hierarchy = meta.get("social_hierarchy", "")
            hierarchy_str = f" [{hierarchy}]" if hierarchy and hierarchy != "unknown" else ""
            conf_str = f" (確度: {f.confidence:.0%})" if f.confidence < 1.0 else ""
            lines.append(f"- {f.subject}{hierarchy_str} → {f.predicate} → {f.object_}{conf_str}")
        return "\n".join(lines)

    def _format_episodes(self, episodes: list) -> str:
        lines = []
        for e in episodes[:10]:
            preview = e.content[:150] + "..." if len(e.content) > 150 else e.content
            lines.append(f"- [{e.role}] {preview}")
        return "\n".join(lines)


_context_generator: Optional[ContextGenerator] = None


def get_context_generator() -> ContextGenerator:
    global _context_generator
    if _context_generator is None:
        _context_generator = ContextGenerator()
    return _context_generator
