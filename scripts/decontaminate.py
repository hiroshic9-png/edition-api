#!/usr/bin/env python3
"""
Phase A: 汚染データの完全除去
1. price_comparable 107件を全削除
2. EDITION自己参照ソースを全除去
3. verified_byの再評価（循環参照→ai_generated に降格）
4. verified_by欠落フィールドにai_generatedを付与
"""
import json, datetime, copy

now = datetime.datetime.utcnow().isoformat() + "Z"

with open("/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/training_pairs.json") as f:
    data = json.load(f)

original_count = len(data["pairs"])
print(f"=== PHASE A: DATA DECONTAMINATION ===")
print(f"Starting pairs: {original_count}")

# STEP 1: Remove ALL price_comparable
pc_removed = [p for p in data["pairs"] if p["type"] == "price_comparable"]
data["pairs"] = [p for p in data["pairs"] if p["type"] != "price_comparable"]
print(f"\nSTEP 1: Removed {len(pc_removed)} price_comparable pairs")

# STEP 2: Remove EDITION self-references from sources/evidence
edition_refs_removed = 0
for p in data["pairs"]:
    for field in ["sources", "evidence"]:
        if field in p:
            original_len = len(p[field])
            p[field] = [s for s in p[field] if "EDITION" not in s]
            edition_refs_removed += (original_len - len(p[field]))

print(f"STEP 2: Removed {edition_refs_removed} self-referencing EDITION citations")

# STEP 3: Reassess verified_by
# If sources/evidence is now empty after removing EDITION refs -> ai_generated
# If verified_by is missing -> ai_generated
# If verified_by is source_verified but no external sources -> ai_generated
downgraded = 0
missing_fixed = 0
for p in data["pairs"]:
    all_sources = p.get("sources", []) + p.get("evidence", [])
    
    if "verified_by" not in p:
        p["verified_by"] = "ai_generated"
        missing_fixed += 1
    elif p["verified_by"] == "source_verified" and len(all_sources) == 0:
        p["verified_by"] = "ai_generated"
        downgraded += 1

print(f"STEP 3: Downgraded {downgraded} false 'source_verified' to 'ai_generated'")
print(f"STEP 3: Fixed {missing_fixed} missing verified_by fields")

# Update metadata
data["total_pairs"] = len(data["pairs"])
data["generated_at"] = now

with open("/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/training_pairs.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Final stats
from collections import Counter
types = Counter(p["type"] for p in data["pairs"])
vb = Counter(p.get("verified_by", "MISSING") for p in data["pairs"])
cats = Counter(p["category"] for p in data["pairs"])

print(f"\n{'='*60}")
print(f"DECONTAMINATION COMPLETE: {original_count} → {data['total_pairs']}")
print(f"{'='*60}")
print(f"\n=== BY TYPE ===")
for t, c in sorted(types.items(), key=lambda x: -x[1]): print(f"  {t}: {c}")
print(f"\n=== BY VERIFIED_BY ===")
for v, c in sorted(vb.items(), key=lambda x: -x[1]): print(f"  {v}: {c}")
print(f"\n=== BY CATEGORY ===")
for cat, c in sorted(cats.items(), key=lambda x: -x[1]): print(f"  {cat}: {c}")

# Check remaining self-references
remaining_edition = 0
for p in data["pairs"]:
    for s in p.get("sources", []) + p.get("evidence", []):
        if "EDITION" in s:
            remaining_edition += 1
print(f"\n=== RESIDUAL CHECK ===")
print(f"Remaining EDITION self-references: {remaining_edition}")
