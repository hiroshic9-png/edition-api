#!/usr/bin/env python3
"""
QUARANTINE ZONE — Data Isolation Manager
==========================================
全ての新規データはここを経由する。直接本番投入は許されない。

フロー:
  1. 新規データ → data/quarantine/pending_assets.json に投入
  2. CHECKPOINT ALPHA/BRAVO/CHARLIE を順次実行
  3. 全通過 → data/assets.json に自動昇格
  4. 1つでも不合格 → 保留のまま（理由を記録）
  5. 全判定は data/quarantine/audit_log.json に記録
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from copy import deepcopy

from config import (
    ASSETS_PATH,
    QUARANTINE_DIR,
    AUDIT_LOG_DIR,
    AUTO_PROMOTE_ON_PASS,
)


def ensure_dirs():
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    os.makedirs(AUDIT_LOG_DIR, exist_ok=True)


def load_quarantine():
    """Load pending assets from quarantine."""
    path = os.path.join(QUARANTINE_DIR, "pending_assets.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"pending": [], "rejected": [], "promoted": []}


def save_quarantine(data):
    path = os.path.join(QUARANTINE_DIR, "pending_assets.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log_audit(entry):
    """Append audit log entry."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = os.path.join(AUDIT_LOG_DIR, f"{today}.json")

    if os.path.exists(log_path):
        with open(log_path) as f:
            log = json.load(f)
    else:
        log = {"date": today, "entries": []}

    log["entries"].append(entry)

    with open(log_path, "w") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def submit_to_quarantine(assets):
    """Submit new assets to quarantine zone."""
    ensure_dirs()
    q = load_quarantine()

    existing_ids = {a["id"] for a in q["pending"]}
    added = 0

    for asset in assets:
        if asset["id"] not in existing_ids:
            asset["_quarantine_submitted"] = datetime.now(timezone.utc).isoformat()
            asset["_quarantine_status"] = "PENDING"
            asset["_checkpoint_results"] = {}
            q["pending"].append(asset)
            existing_ids.add(asset["id"])
            added += 1

            log_audit({
                "action": "SUBMIT",
                "asset_id": asset["id"],
                "timestamp": asset["_quarantine_submitted"],
            })

    save_quarantine(q)
    print(f"📥 Submitted {added} assets to quarantine ({len(q['pending'])} total pending)")
    return added


def run_checkpoints(asset):
    """Run all checkpoints on a quarantined asset."""
    from checkpoint_alpha import run_alpha
    from checkpoint_bravo import run_bravo
    from checkpoint_charlie import run_charlie

    results = {}

    # ALPHA
    alpha = run_alpha(asset)
    results["alpha"] = alpha
    if alpha["verdict"] == "REJECT":
        return results, "REJECT", f"ALPHA: {alpha['checks'][-1].get('reason', 'Failed')}"

    time.sleep(0.3)

    # BRAVO
    bravo = run_bravo(asset)
    results["bravo"] = bravo
    if bravo["verdict"] == "REJECT":
        mismatches = bravo.get("mismatches", [])
        reason = f"BRAVO: {len(mismatches)} field mismatch(es)"
        return results, "REJECT", reason

    time.sleep(0.3)

    # CHARLIE
    charlie = run_charlie(asset)
    results["charlie"] = charlie
    if charlie["verdict"] == "REJECT":
        return results, "REJECT", "CHARLIE: Plagiarism detected"
    elif charlie["verdict"] == "REWRITE":
        return results, "REWRITE", f"CHARLIE: Originality score {charlie['originality_score']}/100"

    return results, "PASS", "All checkpoints passed"


def promote_asset(asset, production_assets):
    """Promote a verified asset from quarantine to production."""
    # Remove quarantine metadata
    clean = deepcopy(asset)
    for key in list(clean.keys()):
        if key.startswith("_quarantine") or key.startswith("_checkpoint") or key == "_needs_curation":
            del clean[key]

    # Add verification metadata
    clean["last_verified"] = datetime.now(timezone.utc).isoformat()
    clean["integrity_status"] = "verified"

    production_assets.append(clean)
    return clean


def process_quarantine():
    """Process all pending assets in quarantine."""
    ensure_dirs()
    q = load_quarantine()

    if not q["pending"]:
        print("📭 No pending assets in quarantine")
        return

    print("=" * 70)
    print("QUARANTINE ZONE — Processing Pending Assets")
    print(f"Pending: {len(q['pending'])}")
    print("=" * 70)

    # Load production assets
    with open(ASSETS_PATH) as f:
        prod_data = json.load(f)
    prod_ids = {a["id"] for a in prod_data["assets"]}

    promoted = []
    rejected = []
    rewrite = []
    still_pending = []

    for asset in q["pending"]:
        aid = asset["id"]

        # Skip if already in production
        if aid in prod_ids:
            print(f"  {aid}: Already in production, skipping")
            continue

        print(f"\n  Processing: {aid}")

        # Run all checkpoints
        results, verdict, reason = run_checkpoints(asset)
        asset["_checkpoint_results"] = results

        if verdict == "PASS" and AUTO_PROMOTE_ON_PASS:
            promoted_asset = promote_asset(asset, prod_data["assets"])
            promoted.append(aid)
            q["promoted"].append({
                "id": aid,
                "promoted_at": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
            })
            print(f"  ✅ {aid}: PROMOTED to production")

            log_audit({
                "action": "PROMOTE",
                "asset_id": aid,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
            })

        elif verdict == "REWRITE":
            rewrite.append(aid)
            asset["_quarantine_status"] = "REWRITE_REQUIRED"
            still_pending.append(asset)
            print(f"  🟡 {aid}: REWRITE REQUIRED — {reason}")

            log_audit({
                "action": "REWRITE_REQUIRED",
                "asset_id": aid,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
            })

        else:
            rejected.append(aid)
            q["rejected"].append({
                "id": aid,
                "rejected_at": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
            })
            print(f"  ❌ {aid}: REJECTED — {reason}")

            log_audit({
                "action": "REJECT",
                "asset_id": aid,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
            })

    # Update quarantine
    q["pending"] = still_pending
    save_quarantine(q)

    # Save production data if any promotions
    if promoted:
        with open(ASSETS_PATH, "w") as f:
            json.dump(prod_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"QUARANTINE RESULTS:")
    print(f"  ✅ Promoted: {len(promoted)}")
    print(f"  🟡 Rewrite: {len(rewrite)}")
    print(f"  ❌ Rejected: {len(rejected)}")
    print(f"  📥 Still pending: {len(still_pending)}")


if __name__ == "__main__":
    if "--submit" in sys.argv:
        # Read from stdin or a file
        idx = sys.argv.index("--submit")
        if idx + 1 < len(sys.argv):
            with open(sys.argv[idx + 1]) as f:
                new_assets = json.load(f)
            if isinstance(new_assets, list):
                submit_to_quarantine(new_assets)
            elif isinstance(new_assets, dict) and "assets" in new_assets:
                submit_to_quarantine(new_assets["assets"])
        else:
            print("Usage: quarantine.py --submit <path_to_assets.json>")
    else:
        process_quarantine()
