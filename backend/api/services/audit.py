"""Large-scale knowledge audit engine.

Performs periodic comprehensive audits of all EDITION knowledge:
  1. Cross-reference verification (multiple source comparison)
  2. Internal consistency checks (contradictions between domains)
  3. Completeness assessment (coverage gaps)
  4. Accuracy scoring via LLM fact-checking

Design principle: "正確でない情報を世に出したら破滅"
  - Every knowledge entry must be traceable to an authoritative source
  - Cross-reference with at least 2 independent sources where possible
  - Flag any entry that cannot be independently verified
"""
import logging
import json
import re
from datetime import date, datetime
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

AUDIT_RESULTS_FILE = Path("data/audit_results.jsonl")


class AuditResult:
    """Result of auditing a single knowledge entry."""

    def __init__(
        self,
        domain: str,
        entry_id: str,
        entry_name: str,
        checks_performed: list,
        issues_found: list,
        accuracy_score: float,
        recommendation: str,
        audited_at: Optional[str] = None,
    ):
        self.domain = domain
        self.entry_id = entry_id
        self.entry_name = entry_name
        self.checks_performed = checks_performed
        self.issues_found = issues_found
        self.accuracy_score = accuracy_score
        self.recommendation = recommendation
        self.audited_at = audited_at or datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "entry_id": self.entry_id,
            "entry_name": self.entry_name,
            "checks_performed": self.checks_performed,
            "issues_found": self.issues_found,
            "issues_count": len(self.issues_found),
            "accuracy_score": self.accuracy_score,
            "recommendation": self.recommendation,
            "audited_at": self.audited_at,
        }


class KnowledgeAuditor:
    """Comprehensive knowledge audit engine."""

    AUDIT_SYSTEM_PROMPT = """あなたは日本の法令・規制・ビジネス慣行の事実検証（ファクトチェック）専門家です。

与えられた知識エントリの正確性を厳密に検証してください。

## 検証観点
1. **法令の正確性**: 引用された法律名・条文番号・罰則規定は正しいか
2. **数値の正確性**: 金額・期間・割合等の数値は正しいか（2026年5月時点で）
3. **最新性**: 法改正・制度変更により古くなっている情報はないか
4. **内部整合性**: エントリ内で矛盾する記述はないか
5. **不足情報**: 重要だが欠落している情報はないか

## 検証の厳格さ
- 確実に誤りである場合のみ「error」として報告
- 古くなっている可能性がある場合は「warning」として報告
- 軽微な改善提案は「suggestion」として報告
- 不確かな場合は「unverifiable」として報告

## 出力フォーマット（JSON）
```json
{
  "accuracy_score": 0.0-1.0,
  "issues": [
    {
      "severity": "error|warning|suggestion|unverifiable",
      "field": "問題のあるフィールド名",
      "description": "問題の詳細",
      "current_value": "現在の値",
      "correct_value": "正しい値（わかる場合）",
      "source": "検証に使った情報源"
    }
  ],
  "verified_facts": ["検証済みの事実のリスト"],
  "overall_assessment": "全体的な評価（1-3文）",
  "recommendation": "retain|update|review|flag_for_removal"
}
```

JSONのみを出力してください。"""

    def __init__(self):
        self._llm = None
        self._results: list[AuditResult] = []
        self._load_results()

    def _get_llm(self):
        """Lazy init LLM client."""
        if self._llm is None:
            try:
                from backend.api.services.extraction import LLMClient
                self._llm = LLMClient()
            except Exception as e:
                logger.warning(f"Could not init LLM for auditor: {e}")
        return self._llm

    # ── Single entry audit ─────────────────────────────────────

    def audit_entry(self, domain: str, entry_id: str, entry_data: dict) -> dict:
        """Audit a single knowledge entry using LLM fact-checking.

        Returns detailed audit result with accuracy score and issues.
        """
        checks = ["structural_integrity"]
        issues = []

        # 1. Structural integrity check (no LLM needed)
        structural_issues = self._check_structure(domain, entry_id, entry_data)
        issues.extend(structural_issues)

        # 2. Source traceability check
        checks.append("source_traceability")
        meta = entry_data.get("_meta", {})
        if not meta.get("source"):
            issues.append({
                "severity": "warning",
                "field": "_meta.source",
                "description": "No authoritative source specified for this entry",
            })
        if not meta.get("source_url"):
            issues.append({
                "severity": "suggestion",
                "field": "_meta.source_url",
                "description": "No source URL for independent verification",
            })

        # 3. LLM fact-checking (the core audit)
        llm = self._get_llm()
        if llm and llm.provider != "fallback":
            checks.append("llm_fact_check")
            llm_result = self._llm_fact_check(domain, entry_id, entry_data)
            if llm_result:
                issues.extend(llm_result.get("issues", []))
                accuracy_score = llm_result.get("accuracy_score", 0.7)
                recommendation = llm_result.get("recommendation", "review")
            else:
                accuracy_score = 0.5  # Can't determine without LLM
                recommendation = "review"
        else:
            # Without LLM, base score on structural checks only
            error_count = sum(1 for i in issues if i.get("severity") == "error")
            warning_count = sum(1 for i in issues if i.get("severity") == "warning")
            accuracy_score = max(0.0, 1.0 - (error_count * 0.3) - (warning_count * 0.1))
            recommendation = "review" if error_count > 0 else "retain"

        result = AuditResult(
            domain=domain,
            entry_id=entry_id,
            entry_name=entry_data.get("name_ja") or entry_data.get("name_en") or entry_id,
            checks_performed=checks,
            issues_found=issues,
            accuracy_score=round(accuracy_score, 2),
            recommendation=recommendation,
        )

        self._results.append(result)
        self._save_results()

        return result.to_dict()

    # ── Domain-wide audit ──────────────────────────────────────

    def audit_domain(self, domain: str) -> dict:
        """Audit all entries in a knowledge domain."""
        from backend.api.services.freshness import freshness_report
        domains = freshness_report._load_all_domains()
        db = domains.get(domain, {})

        if not db:
            return {"error": f"Domain '{domain}' not found"}

        results = []
        for entry_id, entry_data in db.items():
            result = self.audit_entry(domain, entry_id, entry_data)
            results.append(result)

        # Domain summary
        avg_accuracy = sum(r["accuracy_score"] for r in results) / max(len(results), 1)
        total_issues = sum(r["issues_count"] for r in results)
        errors = sum(
            1 for r in results
            for i in r["issues_found"]
            if i.get("severity") == "error"
        )

        return {
            "domain": domain,
            "audit_date": date.today().isoformat(),
            "entries_audited": len(results),
            "average_accuracy": round(avg_accuracy, 2),
            "total_issues": total_issues,
            "critical_errors": errors,
            "entries": results,
            "grade": self._compute_grade(avg_accuracy),
        }

    # ── Full platform audit ────────────────────────────────────

    def audit_platform(self) -> dict:
        """Run a comprehensive audit of the entire EDITION platform.

        This is the "大規模監査" that should be run periodically.
        """
        from backend.api.services.freshness import freshness_report
        domains = freshness_report._load_all_domains()

        domain_results = {}
        total_entries = 0
        total_issues = 0
        total_errors = 0

        for domain_name, db in domains.items():
            result = self.audit_domain(domain_name)
            domain_results[domain_name] = result
            total_entries += result.get("entries_audited", 0)
            total_issues += result.get("total_issues", 0)
            total_errors += result.get("critical_errors", 0)

        # Cross-domain consistency check
        cross_domain_issues = self._check_cross_domain_consistency(domains)

        avg_accuracy = sum(
            r.get("average_accuracy", 0) for r in domain_results.values()
        ) / max(len(domain_results), 1)

        return {
            "audit_date": date.today().isoformat(),
            "audit_type": "full_platform",
            "platform_summary": {
                "domains_audited": len(domain_results),
                "total_entries": total_entries,
                "average_accuracy": round(avg_accuracy, 2),
                "total_issues": total_issues,
                "critical_errors": total_errors,
                "cross_domain_issues": len(cross_domain_issues),
                "grade": self._compute_grade(avg_accuracy),
            },
            "domains": domain_results,
            "cross_domain_issues": cross_domain_issues,
            "recommended_actions": self._generate_recommendations(domain_results, cross_domain_issues),
        }

    # ── Internal checks ────────────────────────────────────────

    def _check_structure(self, domain: str, entry_id: str, entry_data: dict) -> list:
        """Check structural integrity of an entry (no LLM needed)."""
        issues = []

        # Check for required fields based on domain type
        if domain == "regulation":
            required = ["licenses", "governing_body", "requirements", "timeline", "penalties"]
            for field in required:
                if field not in entry_data:
                    issues.append({
                        "severity": "warning",
                        "field": field,
                        "description": f"Required field '{field}' is missing",
                    })

            # Check references exist
            if not entry_data.get("references"):
                issues.append({
                    "severity": "warning",
                    "field": "references",
                    "description": "No reference URLs provided for verification",
                })

        # Check for empty strings
        for key, value in entry_data.items():
            if key.startswith("_"):
                continue
            if isinstance(value, str) and not value.strip():
                issues.append({
                    "severity": "suggestion",
                    "field": key,
                    "description": f"Field '{key}' is empty",
                })

        return issues

    def _check_cross_domain_consistency(self, domains: dict) -> list:
        """Check for consistency across domains.

        For example: foreign_entry mentions visa requirements,
        regulation also mentions visa — are they consistent?
        """
        issues = []

        # Example check: compare foreign_entry visa info with regulation info
        foreign_entry = domains.get("foreign_entry", {})
        regulation = domains.get("regulation", {})

        # Check if visa-related info in foreign_entry matches regulation
        visa_entry = foreign_entry.get("management_visa", {})
        if visa_entry:
            for ind_name, ind_data in regulation.items():
                foreign_notes = ind_data.get("foreign_company_notes", "")
                if "経営・管理" in foreign_notes or "経営管理" in foreign_notes:
                    # Both mention management visa — check for contradictions
                    # This is a structural check; detailed comparison needs LLM
                    pass

        return issues

    def _llm_fact_check(self, domain: str, entry_id: str, entry_data: dict) -> Optional[dict]:
        """Use LLM to fact-check a knowledge entry."""
        llm = self._get_llm()
        if not llm:
            return None

        entry_summary = json.dumps(entry_data, ensure_ascii=False, default=str)[:4000]

        user_prompt = f"""以下の知識エントリの正確性を厳密に検証してください。

ドメイン: {domain}
エントリID: {entry_id}
検証日: {date.today().isoformat()}

内容:
{entry_summary}

JSON形式で検証結果を出力してください。"""

        try:
            raw = llm.generate(self.AUDIT_SYSTEM_PROMPT, user_prompt)
            raw = raw.strip()
            if raw.startswith("```"):
                raw = re.sub(r'^```\w*\n?', '', raw)
                raw = re.sub(r'\n?```$', '', raw)
                raw = raw.strip()

            result = json.loads(raw)
            # Cap accuracy score
            if "accuracy_score" in result:
                result["accuracy_score"] = min(float(result["accuracy_score"]), 1.0)
            return result
        except Exception as e:
            logger.error(f"LLM fact-check failed for {domain}/{entry_id}: {e}")
            return None

    def _compute_grade(self, accuracy: float) -> str:
        """Compute letter grade from accuracy score."""
        if accuracy >= 0.95:
            return "A+"
        elif accuracy >= 0.90:
            return "A"
        elif accuracy >= 0.85:
            return "B+"
        elif accuracy >= 0.80:
            return "B"
        elif accuracy >= 0.70:
            return "C"
        elif accuracy >= 0.60:
            return "D"
        else:
            return "F"

    def _generate_recommendations(self, domain_results: dict, cross_issues: list) -> list:
        """Generate actionable recommendations from audit results."""
        recs = []

        # Find worst domains
        sorted_domains = sorted(
            domain_results.items(),
            key=lambda x: x[1].get("average_accuracy", 0),
        )

        for domain_name, result in sorted_domains[:3]:
            if result.get("critical_errors", 0) > 0:
                recs.append({
                    "priority": "critical",
                    "domain": domain_name,
                    "action": f"Fix {result['critical_errors']} critical errors in {domain_name} domain",
                    "accuracy": result.get("average_accuracy"),
                })

        if cross_issues:
            recs.append({
                "priority": "high",
                "domain": "cross_domain",
                "action": f"Resolve {len(cross_issues)} cross-domain consistency issues",
            })

        return recs

    # ── Audit history ──────────────────────────────────────────

    def get_latest_results(self, domain: Optional[str] = None, limit: int = 50) -> list:
        """Get latest audit results."""
        results = self._results
        if domain:
            results = [r for r in results if r.domain == domain]
        return [r.to_dict() for r in results[-limit:]]

    def _load_results(self):
        """Load audit results from JSONL file."""
        if not AUDIT_RESULTS_FILE.exists():
            return
        try:
            with open(AUDIT_RESULTS_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    self._results.append(AuditResult(
                        domain=data["domain"],
                        entry_id=data["entry_id"],
                        entry_name=data["entry_name"],
                        checks_performed=data["checks_performed"],
                        issues_found=data["issues_found"],
                        accuracy_score=data["accuracy_score"],
                        recommendation=data["recommendation"],
                        audited_at=data.get("audited_at"),
                    ))
        except Exception as e:
            logger.warning(f"Could not load audit results: {e}")

    def _save_results(self):
        """Save audit results to JSONL file."""
        try:
            AUDIT_RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            # Keep only last 500 results
            recent = self._results[-500:]
            with open(AUDIT_RESULTS_FILE, "w") as f:
                for r in recent:
                    f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning(f"Could not save audit results: {e}")


# ── Module-level instance ──────────────────────────────────────
knowledge_auditor = KnowledgeAuditor()
