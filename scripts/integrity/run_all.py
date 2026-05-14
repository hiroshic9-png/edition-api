#!/usr/bin/env python3
"""
EDITION Integrity Engine — Full Pipeline Runner
=================================================
全Checkpointを順次実行し、完全な検証レポートを出力。

Usage:
  python3 scripts/integrity/run_all.py           # 全検証実行
  python3 scripts/integrity/run_all.py --audit    # 定期監査モード
  python3 scripts/integrity/run_all.py --init     # 学習DB初期化
"""
import json
import os
import sys
import time
from datetime import datetime, timezone

# Add integrity directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ASSETS_PATH, AUDIT_LOG_DIR
from checkpoint_alpha import run_alpha_batch
from checkpoint_bravo import run_bravo_batch
from checkpoint_charlie import run_charlie_batch
from continuous_audit import run_continuous_audit
from learning_loop import initialize_knowledge_base, load_knowledge, record_verification


def run_full_pipeline():
    """Run the complete integrity pipeline on all production data."""
    print("=" * 70)
    print("EDITION INTEGRITY ENGINE — Full Pipeline")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    with open(ASSETS_PATH) as f:
        assets = json.load(f)["assets"]

    print(f"\nAssets to verify: {len(assets)}")
    total_start = time.time()

    # ========================================
    # CHECKPOINT ALPHA — Source Authentication
    # ========================================
    print(f"\n{'─' * 70}")
    alpha_results = run_alpha_batch(assets)
    alpha_pass = sum(1 for r in alpha_results if r["verdict"] == "PASS")

    # ========================================
    # CHECKPOINT BRAVO — API Cross-Reference
    # ========================================
    print(f"\n{'─' * 70}")
    bravo_results = run_bravo_batch(assets)
    bravo_pass = sum(1 for r in bravo_results if r["verdict"] == "PASS")

    # ========================================
    # CHECKPOINT CHARLIE — Originality Guard
    # ========================================
    print(f"\n{'─' * 70}")
    charlie_results = run_charlie_batch(assets)
    charlie_pass = sum(1 for r in charlie_results if r["verdict"] == "PASS")
    charlie_rewrite = sum(1 for r in charlie_results if r["verdict"] == "REWRITE")

    # ========================================
    # SUMMARY
    # ========================================
    elapsed = time.time() - total_start

    print(f"\n{'=' * 70}")
    print("INTEGRITY ENGINE — FINAL REPORT")
    print(f"{'=' * 70}")
    print(f"  Assets verified:    {len(assets)}")
    print(f"  ALPHA (Source):     {alpha_pass}/{len(assets)} PASS")
    print(f"  BRAVO (API):        {bravo_pass}/{len(assets)} PASS")
    print(f"  CHARLIE (Original): {charlie_pass}/{len(assets)} PASS, {charlie_rewrite} REWRITE")
    print(f"  Elapsed:            {elapsed:.1f}s")

    all_pass = alpha_pass == len(assets) and bravo_pass == len(assets)

    if all_pass and charlie_rewrite == 0:
        print(f"\n✅ ALL CHECKPOINTS PASSED — Data integrity verified")
    elif all_pass and charlie_rewrite > 0:
        print(f"\n🟡 ALPHA/BRAVO PASSED — {charlie_rewrite} description(s) need rewriting")
    else:
        print(f"\n❌ INTEGRITY CHECK FAILED — Data must not be deployed")
        sys.exit(1)

    # Record in learning loop
    record_verification(
        total=len(assets) * 3,
        passed=alpha_pass + bravo_pass + charlie_pass,
        rejected=(len(assets) - alpha_pass) + (len(assets) - bravo_pass),
        corrections=0,
    )

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": len(assets),
        "alpha": {"pass": alpha_pass, "total": len(assets)},
        "bravo": {"pass": bravo_pass, "total": len(assets)},
        "charlie": {"pass": charlie_pass, "rewrite": charlie_rewrite, "total": len(assets)},
        "elapsed_seconds": round(elapsed, 1),
        "verdict": "PASS" if all_pass else "FAIL",
    }


if __name__ == "__main__":
    if "--init" in sys.argv:
        initialize_knowledge_base()
    elif "--audit" in sys.argv:
        run_continuous_audit()
    else:
        run_full_pipeline()
