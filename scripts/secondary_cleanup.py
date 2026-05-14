#!/usr/bin/env python3
"""
Phase B: 二次除去 — 構造的に不完全なデータの排除
1. ソース/エビデンスが0件のペアを排除
2. AVFでマーカーが0件のペアを排除
3. 科学的数値（スペクトルピーク等）の照合フラグ付与
"""
import json, datetime

now = datetime.datetime.utcnow().isoformat() + "Z"

with open("/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/training_pairs.json") as f:
    data = json.load(f)

before = len(data["pairs"])
removed_ids = []

# STEP 1: Remove pairs with NO sources AND NO evidence
no_source_pairs = []
has_source_pairs = []
for p in data["pairs"]:
    all_src = p.get("sources", []) + p.get("evidence", [])
    if len(all_src) == 0:
        no_source_pairs.append(p)
        removed_ids.append(p["id"])
    else:
        has_source_pairs.append(p)

print(f"STEP 1: Removed {len(no_source_pairs)} pairs with zero sources")
data["pairs"] = has_source_pairs

# STEP 2: Remove AVF with 0 markers
avf_removed = []
clean_pairs = []
for p in data["pairs"]:
    if p["type"] == "authentic_vs_fake":
        am = p.get("authentic_markers", [])
        fm = p.get("fake_markers", [])
        if len(am) == 0 or len(fm) == 0:
            avf_removed.append(p["id"])
            removed_ids.append(p["id"])
            continue
    clean_pairs.append(p)

print(f"STEP 2: Removed {len(avf_removed)} AVF pairs with empty markers")
data["pairs"] = clean_pairs

# STEP 3: Flag scientific claims for manual verification (don't remove, just flag)
flagged = 0
for p in data["pairs"]:
    if p["type"] == "forensic_qa":
        answer = p.get("answer", "")
        if "cm⁻¹" in answer or "°C" in answer:
            p["_needs_verification"] = "scientific_values"
            flagged += 1

print(f"STEP 3: Flagged {flagged} pairs with scientific values for verification")

# Update
data["total_pairs"] = len(data["pairs"])
data["generated_at"] = now

with open("/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/training_pairs.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Final clean stats
from collections import Counter
types = Counter(p["type"] for p in data["pairs"])
vb = Counter(p.get("verified_by", "?") for p in data["pairs"])
cats = Counter(p["category"] for p in data["pairs"])

print(f"\n{'='*60}")
print(f"SECONDARY CLEANUP: {before} → {data['total_pairs']}")
print(f"Removed total: {len(removed_ids)}")
print(f"{'='*60}")
print(f"\n=== BY TYPE ===")
for t, c in sorted(types.items(), key=lambda x: -x[1]): print(f"  {t}: {c}")
print(f"\n=== BY VERIFIED_BY ===")
for v, c in sorted(vb.items(), key=lambda x: -x[1]): print(f"  {v}: {c}")
print(f"\n=== BY CATEGORY ===")
for cat, c in sorted(cats.items(), key=lambda x: -x[1]): print(f"  {cat}: {c}")

# Verify: every remaining pair has at least 1 source
zero_src = sum(1 for p in data["pairs"] if len(p.get("sources",[]) + p.get("evidence",[])) == 0)
print(f"\n=== INTEGRITY CHECK ===")
print(f"Pairs with zero sources remaining: {zero_src}")
print(f"All pairs have sources: {'✅ YES' if zero_src == 0 else '❌ NO'}")
