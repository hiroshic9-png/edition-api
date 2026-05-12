#!/usr/bin/env python3
"""Standalone KB audit runner for CI/CD pipelines.

Performs structural integrity checks on all EDITION knowledge base JSON files
without requiring LLM access. Designed to run in GitHub Actions.

Usage:
    PYTHONPATH=. python scripts/audit_runner.py --output data/audit_results.json
    PYTHONPATH=. python scripts/audit_runner.py --domain calendar --output /tmp/audit.json
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.api.services.kb_loader import load_all_domains, load_domain, load_regulation


# ── Required fields per domain type ──────────────────────────────
COMMON_REQUIRED = ["name_ja", "name_en", "summary"]

DOMAIN_REQUIRED = {
    "regulation": ["licenses", "governing_body", "requirements", "timeline", "penalties"],
    "protocol": ["name_ja", "name_en", "category", "importance", "summary"],
}

META_REQUIRED = ["last_verified", "source", "confidence", "version"]


def audit_entry(domain: str, entry_id: str, entry_data: dict) -> dict:
    """Audit a single knowledge entry for structural issues."""
    issues = []

    # 1. Check _meta block
    meta = entry_data.get("_meta")
    if not meta:
        issues.append({
            "severity": "error",
            "field": "_meta",
            "description": "Missing _meta block — no provenance tracking",
        })
    else:
        for field in META_REQUIRED:
            if field not in meta or meta[field] is None:
                # source_url can be null for some entries
                if field == "source_url":
                    continue
                issues.append({
                    "severity": "warning" if field != "last_verified" else "error",
                    "field": f"_meta.{field}",
                    "description": f"Missing required meta field: {field}",
                })

        # Check source_url exists
        if not meta.get("source_url"):
            issues.append({
                "severity": "warning",
                "field": "_meta.source_url",
                "description": "No source URL for independent verification",
            })

    # 2. Check common required fields
    for field in COMMON_REQUIRED:
        if field not in entry_data:
            issues.append({
                "severity": "warning",
                "field": field,
                "description": f"Missing common field: {field}",
            })

    # 3. Check domain-specific required fields
    required = DOMAIN_REQUIRED.get(domain, [])
    for field in required:
        if field not in entry_data:
            issues.append({
                "severity": "warning",
                "field": field,
                "description": f"Missing domain-required field: {field}",
            })

    # 4. Check for empty strings
    for key, value in entry_data.items():
        if key.startswith("_"):
            continue
        if isinstance(value, str) and not value.strip():
            issues.append({
                "severity": "suggestion",
                "field": key,
                "description": f"Empty string value in field: {key}",
            })

    # 5. Check references (regulation domain)
    if domain == "regulation" and not entry_data.get("references"):
        issues.append({
            "severity": "warning",
            "field": "references",
            "description": "No reference URLs for verification",
        })

    error_count = sum(1 for i in issues if i["severity"] == "error")
    warning_count = sum(1 for i in issues if i["severity"] == "warning")
    score = max(0.0, 1.0 - (error_count * 0.3) - (warning_count * 0.1))

    return {
        "domain": domain,
        "entry_id": entry_id,
        "entry_name": entry_data.get("name_ja") or entry_data.get("name_en") or entry_id,
        "issues": issues,
        "error_count": error_count,
        "warning_count": warning_count,
        "accuracy_score": round(score, 2),
    }


def audit_domain(domain_name: str, db: dict) -> dict:
    """Audit all entries in a domain."""
    results = []
    for entry_id, entry_data in db.items():
        result = audit_entry(domain_name, entry_id, entry_data)
        results.append(result)

    total_errors = sum(r["error_count"] for r in results)
    total_warnings = sum(r["warning_count"] for r in results)
    avg_score = sum(r["accuracy_score"] for r in results) / max(len(results), 1)

    return {
        "domain": domain_name,
        "entries_audited": len(results),
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "average_score": round(avg_score, 2),
        "entries": results,
    }


def audit_keywords(domain_name: str, db: dict, keywords: dict) -> list:
    """Check that keyword entries map to actual DB entries."""
    issues = []
    for kw_key in keywords:
        if kw_key not in db:
            issues.append({
                "severity": "error",
                "domain": domain_name,
                "entry_id": kw_key,
                "description": f"Keyword entry '{kw_key}' has no matching DB entry",
            })
    for db_key in db:
        if db_key not in keywords:
            issues.append({
                "severity": "warning",
                "domain": domain_name,
                "entry_id": db_key,
                "description": f"DB entry '{db_key}' has no keyword mapping (undiscoverable)",
            })
    return issues


def run_full_audit(target_domain: str = None) -> dict:
    """Run a full platform audit or single domain audit."""
    domains = load_all_domains()
    
    if target_domain:
        if target_domain not in domains:
            print(f"ERROR: Domain '{target_domain}' not found. Available: {list(domains.keys())}")
            sys.exit(1)
        domains = {target_domain: domains[target_domain]}

    domain_reports = {}
    all_errors = []
    total_entries = 0
    total_errors = 0
    total_warnings = 0

    for domain_name, db in domains.items():
        report = audit_domain(domain_name, db)
        domain_reports[domain_name] = report
        total_entries += report["entries_audited"]
        total_errors += report["total_errors"]
        total_warnings += report["total_warnings"]

        # Collect errors for issue creation
        for entry in report["entries"]:
            for issue in entry["issues"]:
                if issue["severity"] == "error":
                    all_errors.append({
                        "domain": domain_name,
                        "entry_id": entry["entry_id"],
                        "description": issue["description"],
                    })

        # Check keyword consistency
        if domain_name == "regulation":
            # Regulation has industry DB + tourist DB mapped to industry + tourist keywords
            reg_db, tourist_db, industry_kw, tourist_kw = load_regulation()
            # Industry keywords should map to regulation DB
            kw_issues = audit_keywords(domain_name, reg_db, industry_kw)
            # Tourist keywords should map to tourist regulations DB
            kw_issues += audit_keywords(f"{domain_name}:tourist", tourist_db, tourist_kw)
        else:
            _, keywords = load_domain(domain_name)
            kw_issues = audit_keywords(domain_name, db, keywords)
        for issue in kw_issues:
            if issue["severity"] == "error":
                total_errors += 1
                all_errors.append(issue)
            else:
                total_warnings += 1

    health_score = round(
        sum(r["average_score"] for r in domain_reports.values()) / max(len(domain_reports), 1) * 100,
        1
    )

    return {
        "summary": {
            "audit_date": date.today().isoformat(),
            "audit_type": "full" if not target_domain else f"domain:{target_domain}",
            "domains_audited": len(domain_reports),
            "total_entries": total_entries,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "health_score": health_score,
        },
        "domains": domain_reports,
        "errors": all_errors,
    }


def main():
    parser = argparse.ArgumentParser(description="EDITION KB Audit Runner")
    parser.add_argument("--output", "-o", default="data/audit_results.json",
                        help="Output file path for audit results")
    parser.add_argument("--domain", "-d", default="",
                        help="Specific domain to audit (empty for full platform)")
    args = parser.parse_args()

    print(f"🔍 EDITION KB Audit — {date.today().isoformat()}")
    print(f"   Target: {'Full Platform' if not args.domain else args.domain}")
    print()

    report = run_full_audit(args.domain or None)
    summary = report["summary"]

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Print summary
    print(f"📊 Audit Summary")
    print(f"   Domains:  {summary['domains_audited']}")
    print(f"   Entries:  {summary['total_entries']}")
    print(f"   Errors:   {summary['total_errors']}")
    print(f"   Warnings: {summary['total_warnings']}")
    print(f"   Health:   {summary['health_score']}/100")
    print()

    if report["errors"]:
        print(f"❌ Errors found:")
        for err in report["errors"][:10]:
            print(f"   - {err['domain']}/{err['entry_id']}: {err['description']}")
        print()

    print(f"📁 Report saved to: {output_path}")

    # Set GitHub Actions output
    if summary["total_errors"] > 0:
        # Write to GITHUB_OUTPUT if available
        import os
        gh_output = os.environ.get("GITHUB_OUTPUT")
        if gh_output:
            with open(gh_output, "a") as f:
                f.write("has_errors=true\n")
        print("\n⚠️  Audit FAILED — errors detected")
        sys.exit(1)
    else:
        import os
        gh_output = os.environ.get("GITHUB_OUTPUT")
        if gh_output:
            with open(gh_output, "a") as f:
                f.write("has_errors=false\n")
        print("\n✅ Audit PASSED")


if __name__ == "__main__":
    main()
