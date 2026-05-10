"""Freshness, update, and audit API routes.

Provides endpoints for:
  - Knowledge freshness reporting
  - Semi-automated update proposal management
  - Large-scale knowledge auditing
"""
from typing import Optional
from fastapi import APIRouter, Query

from backend.api.services.freshness import freshness_report, freshness_checker
from backend.api.services.knowledge_updater import knowledge_updater
from backend.api.services.audit import knowledge_auditor

router = APIRouter(prefix="/api/v1", tags=["Knowledge Quality"])


# ── Freshness Endpoints ───────────────────────────────────────

@router.get("/freshness/report")
def get_freshness_report():
    """Full platform freshness report across all knowledge domains."""
    return freshness_report.generate_report()


@router.get("/freshness/stale")
def get_stale_entries():
    """List all entries that need review or are stale/deprecated."""
    entries = freshness_report.get_stale_entries()
    return {
        "total": len(entries),
        "entries": entries,
        "action": "Review and re-verify these entries against current official sources",
    }


@router.get("/freshness/domain/{domain}")
def get_domain_freshness(domain: str):
    """Freshness report for a specific knowledge domain."""
    report = freshness_report.get_domain_report(domain)
    if not report:
        return {"error": f"Domain '{domain}' not found"}
    return {"domain": domain, **report}


@router.post("/freshness/verify/{domain}/{entry_id}")
def verify_entry(domain: str, entry_id: str):
    """Mark a knowledge entry as manually verified (admin action).

    This updates the entry's last_verified date to today.
    Note: In the current architecture, this updates the in-memory
    representation. Persistent updates require modifying the KB files.
    """
    from backend.api.services.freshness import freshness_report as fr
    domains = fr._load_all_domains()
    db = domains.get(domain, {})
    entry = db.get(entry_id)

    if not entry:
        return {"error": f"Entry '{entry_id}' not found in domain '{domain}'"}

    # Update in-memory meta
    if "_meta" not in entry:
        entry["_meta"] = {}
    from datetime import date
    entry["_meta"]["last_verified"] = date.today().isoformat()
    entry["_meta"]["confidence"] = "verified"

    return {
        "status": "verified",
        "domain": domain,
        "entry_id": entry_id,
        "verified_date": date.today().isoformat(),
        "note": "In-memory verification applied. KB file update recommended for persistence.",
    }


# ── Update Management Endpoints ───────────────────────────────

@router.get("/updates/proposals")
def list_update_proposals(
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected"),
):
    """List all knowledge update proposals."""
    proposals = knowledge_updater.list_proposals(status=status)
    return {
        "total": len(proposals),
        "proposals": proposals,
    }


@router.post("/updates/check/{domain}")
def check_domain_updates(domain: str):
    """Run update checks for all entries in a domain.

    Checks:
      - e-Gov Law API for law revisions (regulation domain)
      - Source URL freshness (all domains)
    """
    return knowledge_updater.check_domain(domain)


@router.post("/updates/generate/{domain}/{entry_id}")
def generate_update_proposal(domain: str, entry_id: str):
    """Use LLM to generate update proposals for a specific entry.

    Semi-automated (B-level): LLM analyzes and proposes, human approves.
    """
    from backend.api.services.freshness import freshness_report as fr
    domains = fr._load_all_domains()
    db = domains.get(domain, {})
    entry = db.get(entry_id)

    if not entry:
        return {"error": f"Entry '{entry_id}' not found in domain '{domain}'"}

    proposals = knowledge_updater.generate_update_proposals(domain, entry_id, entry)
    return {
        "domain": domain,
        "entry_id": entry_id,
        "proposals_generated": len(proposals),
        "proposals": proposals,
    }


@router.post("/updates/approve/{proposal_id}")
def approve_update_proposal(proposal_id: str):
    """Approve an update proposal for implementation."""
    result = knowledge_updater.approve_proposal(proposal_id)
    if not result:
        return {"error": f"Proposal '{proposal_id}' not found"}
    return {"status": "approved", "proposal": result}


@router.post("/updates/reject/{proposal_id}")
def reject_update_proposal(proposal_id: str):
    """Reject an update proposal."""
    result = knowledge_updater.reject_proposal(proposal_id)
    if not result:
        return {"error": f"Proposal '{proposal_id}' not found"}
    return {"status": "rejected", "proposal": result}


# ── Audit Endpoints ───────────────────────────────────────────

@router.post("/audit/entry/{domain}/{entry_id}")
def audit_single_entry(domain: str, entry_id: str):
    """Audit a single knowledge entry for accuracy.

    Uses LLM fact-checking against known authoritative sources.
    """
    from backend.api.services.freshness import freshness_report as fr
    domains = fr._load_all_domains()
    db = domains.get(domain, {})
    entry = db.get(entry_id)

    if not entry:
        return {"error": f"Entry '{entry_id}' not found in domain '{domain}'"}

    return knowledge_auditor.audit_entry(domain, entry_id, entry)


@router.post("/audit/domain/{domain}")
def audit_domain(domain: str):
    """Run a comprehensive audit of all entries in a domain.

    ⚠️ This may take 30-60 seconds for large domains due to LLM calls.
    """
    return knowledge_auditor.audit_domain(domain)


@router.post("/audit/platform")
def audit_platform():
    """Run a full platform audit across all knowledge domains.

    ⚠️ This is a heavy operation (大規模監査).
    Expected duration: 5-15 minutes depending on platform size and LLM latency.
    Should be run monthly or on-demand.
    """
    return knowledge_auditor.audit_platform()


@router.get("/audit/results")
def get_audit_results(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    limit: int = Query(50, ge=1, le=200, description="Max results to return"),
):
    """Get latest audit results."""
    results = knowledge_auditor.get_latest_results(domain=domain, limit=limit)
    return {
        "total": len(results),
        "results": results,
    }
