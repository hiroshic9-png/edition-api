#!/usr/bin/env python3
"""
KANTEISHI Training Data Quality Gate
=====================================
教師データ投入前に必ず実行する品質ゲート。
1つでもFAILがあればデータの投入を禁止する。

Usage:
  python3 scripts/quality_gate.py              # 全件チェック
  python3 scripts/quality_gate.py --strict     # 厳格モード（warningもfail扱い）
"""
import json, sys, re
from collections import Counter

STRICT = "--strict" in sys.argv

with open("data/training_pairs.json") as f:
    data = json.load(f)

pairs = data["pairs"]
fails = []
warnings = []

print("=" * 60)
print("KANTEISHI QUALITY GATE")
print(f"Mode: {'STRICT' if STRICT else 'STANDARD'}")
print(f"Pairs: {len(pairs)}")
print("=" * 60)

# === GATE 1: No self-referencing sources ===
print("\n[GATE 1] Self-reference check...")
self_refs = []
for p in pairs:
    for s in p.get("sources", []) + p.get("evidence", []):
        # Check for actual EDITION self-reference, not substring matches like "editions"
        s_upper = s.upper()
        if s_upper.startswith("EDITION ") or " EDITION " in s_upper or s_upper == "EDITION":
            self_refs.append((p["id"], s))
if self_refs:
    fails.append(f"GATE 1 FAIL: {len(self_refs)} self-referencing sources found")
    for pid, s in self_refs[:5]:
        print(f"  ❌ {pid}: {s}")
else:
    print("  ✅ PASS — No self-references")

# === GATE 2: All pairs have external sources ===
print("\n[GATE 2] Source presence check...")
no_source = []
for p in pairs:
    all_src = p.get("sources", []) + p.get("evidence", [])
    if len(all_src) == 0:
        no_source.append(p["id"])
if no_source:
    fails.append(f"GATE 2 FAIL: {len(no_source)} pairs have no sources")
    for pid in no_source[:5]:
        print(f"  ❌ {pid}")
else:
    print("  ✅ PASS — All pairs have sources")

# === GATE 3: verified_by integrity ===
print("\n[GATE 3] verified_by integrity...")
bad_verified = []
for p in pairs:
    if "verified_by" not in p:
        bad_verified.append((p["id"], "missing verified_by"))
    elif p["verified_by"] == "source_verified":
        all_src = p.get("sources", []) + p.get("evidence", [])
        if len(all_src) == 0:
            bad_verified.append((p["id"], "source_verified but no sources"))
if bad_verified:
    fails.append(f"GATE 3 FAIL: {len(bad_verified)} verified_by integrity violations")
    for pid, reason in bad_verified[:5]:
        print(f"  ❌ {pid}: {reason}")
else:
    print("  ✅ PASS — verified_by labels are consistent")

# === GATE 4: No duplicate IDs ===
print("\n[GATE 4] Unique ID check...")
ids = [p["id"] for p in pairs]
dupes = [id for id, c in Counter(ids).items() if c > 1]
if dupes:
    fails.append(f"GATE 4 FAIL: {len(dupes)} duplicate IDs")
    for d in dupes:
        print(f"  ❌ {d}")
else:
    print("  ✅ PASS — All IDs unique")

# === GATE 5: AVF marker completeness ===
print("\n[GATE 5] AVF marker check...")
avf_issues = []
for p in pairs:
    if p["type"] == "authentic_vs_fake":
        am = len(p.get("authentic_markers", []))
        fm = len(p.get("fake_markers", []))
        if am < 2 or fm < 2:
            avf_issues.append((p["id"], am, fm))
if avf_issues:
    msg = f"GATE 5: {len(avf_issues)} AVF pairs with < 2 markers"
    if STRICT:
        fails.append(msg)
    else:
        warnings.append(msg)
    for pid, am, fm in avf_issues[:5]:
        print(f"  ⚠️ {pid}: authentic={am} fake={fm}")
else:
    print("  ✅ PASS — All AVF pairs have adequate markers")

# === GATE 6: Price data reality check ===
print("\n[GATE 6] Price data round-number check...")
pc = [p for p in pairs if p["type"] == "price_comparable"]
if pc:
    prices = []
    for p in pc:
        for c in p.get("comparables", []):
            prices.append(c.get("sale_price", 0))
    total = len([pr for pr in prices if pr > 0])
    round_pct = sum(1 for pr in prices if pr > 0 and pr % 1000 == 0) / max(total, 1) * 100
    if round_pct > 50:
        fails.append(f"GATE 6 FAIL: {round_pct:.0f}% of prices are exact thousands (likely fabricated)")
        print(f"  ❌ {round_pct:.0f}% round numbers — suspected fabrication")
    elif round_pct > 30:
        warnings.append(f"GATE 6 WARN: {round_pct:.0f}% round prices — verify sources")
        print(f"  ⚠️ {round_pct:.0f}% round numbers — needs verification")
    else:
        print(f"  ✅ PASS — {round_pct:.0f}% round numbers (acceptable)")
else:
    print("  ✅ PASS — No price_comparable data to check")

# === GATE 7: Required fields present ===
print("\n[GATE 7] Required fields check...")
field_issues = []
for p in pairs:
    required = ["id", "type", "category", "created_at"]
    for f in required:
        if f not in p:
            field_issues.append((p.get("id", "UNKNOWN"), f))
    if p["type"] == "forensic_qa":
        for f in ["question", "answer", "difficulty"]:
            if f not in p:
                field_issues.append((p["id"], f))
if field_issues:
    fails.append(f"GATE 7 FAIL: {len(field_issues)} missing required fields")
    for pid, field in field_issues[:5]:
        print(f"  ❌ {pid}: missing '{field}'")
else:
    print("  ✅ PASS — All required fields present")

# === SUMMARY ===
print(f"\n{'='*60}")
if fails:
    print(f"🔴 QUALITY GATE FAILED — {len(fails)} failures, {len(warnings)} warnings")
    for f in fails:
        print(f"  ❌ {f}")
    for w in warnings:
        print(f"  ⚠️ {w}")
    print("\n⛔ DATA MUST NOT BE DEPLOYED UNTIL ALL FAILURES ARE RESOLVED")
    sys.exit(1)
elif warnings and STRICT:
    print(f"🟡 QUALITY GATE FAILED (STRICT MODE) — {len(warnings)} warnings")
    for w in warnings:
        print(f"  ⚠️ {w}")
    sys.exit(1)
elif warnings:
    print(f"🟡 QUALITY GATE PASSED WITH WARNINGS — {len(warnings)} warnings")
    for w in warnings:
        print(f"  ⚠️ {w}")
    sys.exit(0)
else:
    print(f"✅ QUALITY GATE PASSED — ALL CHECKS CLEAN")
    sys.exit(0)
