"""Semi-automated knowledge update checker.

Architecture:
  1. Checks e-Gov Law API for law revision dates
  2. Checks official source URLs for last-modified headers
  3. Uses LLM (Gemini) to generate update proposals
  4. Flags entries for human review (never auto-updates)

This implements the "B" level automation:
  LLM generates update proposals → human approves/rejects
"""
import logging
import json
import re
from datetime import date, datetime
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Update proposal storage ────────────────────────────────────
# Stored in-memory + JSONL file for persistence across restarts
UPDATE_PROPOSALS_FILE = Path("data/update_proposals.jsonl")


class UpdateProposal:
    """A proposed knowledge update, pending human review."""

    def __init__(
        self,
        domain: str,
        entry_id: str,
        field: str,
        current_value: str,
        proposed_value: str,
        reason: str,
        source: str,
        source_url: Optional[str] = None,
        confidence: float = 0.5,
        created_at: Optional[str] = None,
        status: str = "pending",  # pending, approved, rejected
        proposal_id: Optional[str] = None,
    ):
        self.proposal_id = proposal_id or f"{domain}_{entry_id}_{field}_{date.today().isoformat()}"
        self.domain = domain
        self.entry_id = entry_id
        self.field = field
        self.current_value = current_value
        self.proposed_value = proposed_value
        self.reason = reason
        self.source = source
        self.source_url = source_url
        self.confidence = confidence
        self.created_at = created_at or datetime.now().isoformat()
        self.status = status

    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "domain": self.domain,
            "entry_id": self.entry_id,
            "field": self.field,
            "current_value": self.current_value[:200],  # Truncate for readability
            "proposed_value": self.proposed_value[:500],
            "reason": self.reason,
            "source": self.source,
            "source_url": self.source_url,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "status": self.status,
        }


class KnowledgeUpdater:
    """Semi-automated knowledge update engine."""

    E_GOV_LAW_API = "https://laws.e-gov.go.jp/api/1"

    def __init__(self):
        self._proposals: list[UpdateProposal] = []
        self._llm = None
        self._load_proposals()

    def _get_llm(self):
        """Lazy init LLM client."""
        if self._llm is None:
            try:
                from backend.api.services.extraction import LLMClient
                self._llm = LLMClient()
            except Exception as e:
                logger.warning(f"Could not init LLM for updater: {e}")
        return self._llm

    # ── e-Gov Law API Integration ──────────────────────────────

    def check_law_revision(self, law_name: str) -> Optional[dict]:
        """Check e-Gov Law API for the latest revision of a specific law.

        Returns law metadata including promulgation date and revision history.
        """
        try:
            import httpx
            # Search by law name
            params = {"lawName": law_name}
            resp = httpx.get(
                f"{self.E_GOV_LAW_API}/lawlists/1",
                params=params,
                timeout=15.0,
            )
            if resp.status_code != 200:
                logger.warning(f"e-Gov API returned {resp.status_code} for {law_name}")
                return None

            data = resp.json()
            laws = data.get("result", {}).get("lawNameListInfo", [])
            if not laws:
                return None

            # Find best match
            for law in laws:
                if law_name in law.get("lawName", ""):
                    return {
                        "law_name": law.get("lawName"),
                        "law_no": law.get("lawNo"),
                        "promulgation_date": law.get("promulgationDate"),
                        "law_id": law.get("lawId"),
                    }

            return None
        except Exception as e:
            logger.error(f"e-Gov law check failed for {law_name}: {e}")
            return None

    def check_source_freshness(self, url: str) -> Optional[dict]:
        """Check the Last-Modified header of an official source URL."""
        try:
            import httpx
            resp = httpx.head(url, timeout=10.0, follow_redirects=True)
            last_modified = resp.headers.get("last-modified")
            if last_modified:
                return {
                    "url": url,
                    "last_modified": last_modified,
                    "status_code": resp.status_code,
                }
            return {
                "url": url,
                "last_modified": None,
                "status_code": resp.status_code,
                "note": "No Last-Modified header available",
            }
        except Exception as e:
            logger.error(f"Source freshness check failed for {url}: {e}")
            return None

    # ── LLM-powered update proposal generation ─────────────────

    PROPOSAL_SYSTEM_PROMPT = """あなたは日本の法令・規制・ビジネス慣行の専門家です。

与えられた知識エントリについて、最新の情報に基づいて更新が必要かどうかを判断してください。

## ルール
1. 既知の法改正・制度変更がある場合、具体的な更新提案を出してください
2. 変更がない場合は「変更不要」と回答してください
3. 不確かな場合は confidence を低く設定してください
4. 推測で断言しないでください

## 出力フォーマット（JSON）
```json
{
  "needs_update": true/false,
  "proposals": [
    {
      "field": "更新が必要なフィールド名",
      "current_issue": "現在の記述の問題点",
      "proposed_change": "提案する更新内容",
      "reason": "更新理由（法改正の場合は施行日等を含む）",
      "source": "情報源",
      "confidence": 0.0-1.0
    }
  ],
  "overall_assessment": "エントリ全体の評価（1-2文）"
}
```

JSONのみを出力してください。"""

    def generate_update_proposals(self, domain: str, entry_id: str, entry_data: dict) -> list[dict]:
        """Use LLM to generate update proposals for a knowledge entry.

        This is the core of "B-level" semi-automation:
        LLM analyzes the entry and proposes updates, but never applies them.
        """
        llm = self._get_llm()
        if not llm or llm.provider == "fallback":
            return []

        # Prepare entry summary for LLM
        entry_summary = json.dumps(entry_data, ensure_ascii=False, default=str)[:3000]

        user_prompt = f"""以下の知識エントリの最新性を確認してください。

ドメイン: {domain}
エントリID: {entry_id}
現在の内容:
{entry_summary}

今日は {date.today().isoformat()} です。
この情報に更新が必要かどうか、JSON形式で回答してください。"""

        try:
            raw = llm.generate(self.PROPOSAL_SYSTEM_PROMPT, user_prompt)
            raw = raw.strip()
            if raw.startswith("```"):
                raw = re.sub(r'^```\w*\n?', '', raw)
                raw = re.sub(r'\n?```$', '', raw)
                raw = raw.strip()

            result = json.loads(raw)

            if not result.get("needs_update", False):
                return []

            proposals = []
            for p in result.get("proposals", []):
                proposal = UpdateProposal(
                    domain=domain,
                    entry_id=entry_id,
                    field=p.get("field", "unknown"),
                    current_value=p.get("current_issue", ""),
                    proposed_value=p.get("proposed_change", ""),
                    reason=p.get("reason", ""),
                    source=p.get("source", "LLM analysis"),
                    confidence=min(float(p.get("confidence", 0.5)), 0.8),
                )
                proposals.append(proposal)
                self._proposals.append(proposal)

            self._save_proposals()
            return [p.to_dict() for p in proposals]

        except Exception as e:
            logger.error(f"LLM update proposal generation failed: {e}")
            return []

    # ── Batch domain check ─────────────────────────────────────

    def check_domain(self, domain: str) -> dict:
        """Run update checks for all entries in a domain.

        For regulation domain: also checks e-Gov for law revisions.
        For all domains: checks source URLs for freshness.
        """
        from backend.api.services.freshness import freshness_report

        domains = freshness_report._load_all_domains()
        db = domains.get(domain, {})

        if not db:
            return {"error": f"Domain '{domain}' not found"}

        results = {
            "domain": domain,
            "entries_checked": 0,
            "source_checks": [],
            "law_checks": [],
            "llm_proposals": [],
        }

        for entry_id, entry_data in db.items():
            results["entries_checked"] += 1
            meta = entry_data.get("_meta", {})

            # Check source URL freshness
            source_url = meta.get("source_url")
            if source_url:
                check = self.check_source_freshness(source_url)
                if check:
                    results["source_checks"].append({
                        "entry_id": entry_id,
                        **check,
                    })

            # For regulation domain, check law revisions
            if domain == "regulation":
                law_name = entry_data.get("governing_law")
                if law_name:
                    law_check = self.check_law_revision(law_name)
                    if law_check:
                        results["law_checks"].append({
                            "entry_id": entry_id,
                            **law_check,
                        })

        return results

    # ── Proposal management ────────────────────────────────────

    def list_proposals(self, status: Optional[str] = None) -> list[dict]:
        """List all update proposals, optionally filtered by status."""
        proposals = self._proposals
        if status:
            proposals = [p for p in proposals if p.status == status]
        return [p.to_dict() for p in proposals]

    def approve_proposal(self, proposal_id: str) -> Optional[dict]:
        """Mark a proposal as approved (but don't apply it yet)."""
        for p in self._proposals:
            if p.proposal_id == proposal_id:
                p.status = "approved"
                self._save_proposals()
                return p.to_dict()
        return None

    def reject_proposal(self, proposal_id: str) -> Optional[dict]:
        """Mark a proposal as rejected."""
        for p in self._proposals:
            if p.proposal_id == proposal_id:
                p.status = "rejected"
                self._save_proposals()
                return p.to_dict()
        return None

    # ── Persistence ────────────────────────────────────────────

    def _load_proposals(self):
        """Load proposals from JSONL file."""
        if not UPDATE_PROPOSALS_FILE.exists():
            return
        try:
            with open(UPDATE_PROPOSALS_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    self._proposals.append(UpdateProposal(**data))
        except Exception as e:
            logger.warning(f"Could not load proposals: {e}")

    def _save_proposals(self):
        """Save proposals to JSONL file."""
        try:
            UPDATE_PROPOSALS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(UPDATE_PROPOSALS_FILE, "w") as f:
                for p in self._proposals:
                    f.write(json.dumps(p.to_dict(), ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning(f"Could not save proposals: {e}")


# ── Module-level instance ──────────────────────────────────────
knowledge_updater = KnowledgeUpdater()
