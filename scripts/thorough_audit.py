#!/usr/bin/env python3
"""
Phase B: クリーンデータ徹底監査
残留393件を以下の観点で全件チェック:
1. ソースの実在性・正確性
2. 回答内容の事実確認可能性
3. 内部矛盾の検出
4. 書誌情報の検証
"""
import json, re
from collections import Counter

with open("/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/training_pairs.json") as f:
    data = json.load(f)

pairs = data["pairs"]
issues = []

print("=" * 60)
print("THOROUGH AUDIT OF 393 CLEAN PAIRS")
print("=" * 60)

# === AUDIT 1: Empty or weak sources ===
print("\n--- AUDIT 1: Source quality ---")
empty_sources = []
single_source = []
for p in pairs:
    all_src = p.get("sources", []) + p.get("evidence", [])
    if len(all_src) == 0:
        empty_sources.append(p["id"])
    elif len(all_src) == 1:
        single_source.append((p["id"], all_src[0]))

print(f"  Pairs with NO sources/evidence: {len(empty_sources)}")
for pid in empty_sources[:10]:
    print(f"    ❌ {pid}")
    issues.append({"id": pid, "issue": "no_sources", "severity": "critical"})

print(f"  Pairs with only 1 source: {len(single_source)}")

# === AUDIT 2: Source specificity ===
print("\n--- AUDIT 2: Vague/unverifiable sources ---")
vague_patterns = [
    "various", "general", "tradition", "standard", "common knowledge",
    "technical studies", "research", "analysis", "guidelines", "protocols",
    "records", "archives", "databases", "educational materials"
]
vague_sources = []
all_sources = []
for p in pairs:
    for s in p.get("sources", []) + p.get("evidence", []):
        all_sources.append(s)
        # Check if source is too vague to verify
        s_lower = s.lower()
        if any(vp in s_lower for vp in vague_patterns):
            if len(s) < 60:  # Short vague sources are worse
                vague_sources.append((p["id"], s))

print(f"  Total source citations: {len(all_sources)}")
print(f"  Vague/hard-to-verify sources: {len(vague_sources)}")
# Show unique vague sources
vague_unique = Counter(s for _, s in vague_sources)
for s, c in vague_unique.most_common(20):
    print(f"    ⚠️ [{c}x] {s}")

# === AUDIT 3: Book/author verification flags ===
print("\n--- AUDIT 3: Book citations needing verification ---")
# Extract book-like citations (Author, Title pattern)
book_citations = []
for s in set(all_sources):
    if "," in s and not any(x in s.lower() for x in ["museum", "institute", "university", "foundation", "association", "agency"]):
        book_citations.append(s)

print(f"  Book-format citations: {len(book_citations)}")
for b in sorted(book_citations)[:30]:
    print(f"    📚 {b}")

# === AUDIT 4: Factual claim verification flags ===
print("\n--- AUDIT 4: Specific factual claims requiring verification ---")
# Check for specific dates, numbers, temperatures in FQA answers
date_claims = 0
temp_claims = 0
percentage_claims = 0
for p in pairs:
    if p["type"] == "forensic_qa":
        answer = p.get("answer", "")
        # Specific year claims
        years = re.findall(r'\b(1[0-9]{3}|20[0-2][0-9])\b', answer)
        if years:
            date_claims += 1
        # Temperature claims
        temps = re.findall(r'\d+°C', answer)
        if temps:
            temp_claims += 1
        # Percentage claims
        pcts = re.findall(r'\d+%', answer)
        if pcts:
            percentage_claims += 1

print(f"  FQA with specific year claims: {date_claims}")
print(f"  FQA with temperature claims: {temp_claims}")
print(f"  FQA with percentage claims: {percentage_claims}")
print(f"  → These are verifiable claims that MUST be accurate")

# === AUDIT 5: Specific suspect content ===
print("\n--- AUDIT 5: Content with high fabrication risk ---")
# Check for very specific claims about named individuals/institutions
suspect_pairs = []
for p in pairs:
    if p["type"] == "forensic_qa":
        answer = p.get("answer", "")
        # Spectroscopy peak values (very specific, must be accurate)
        peaks = re.findall(r'\d+\s*cm⁻¹', answer)
        if peaks:
            suspect_pairs.append((p["id"], f"Spectroscopy peaks: {peaks[:3]}"))
        # Chemical formulas
        formulas = re.findall(r'[A-Z][a-z]?₂?O₄?', answer)
        if len(formulas) > 2:
            suspect_pairs.append((p["id"], f"Chemical formulas: {len(formulas)} found"))

print(f"  Pairs with highly specific scientific claims: {len(suspect_pairs)}")
for pid, detail in suspect_pairs[:15]:
    print(f"    🔬 {pid}: {detail}")

# === AUDIT 6: AVF marker quality ===
print("\n--- AUDIT 6: Authentic vs Fake marker quality ---")
avf = [p for p in pairs if p["type"] == "authentic_vs_fake"]
for p in avf:
    am = p.get("authentic_markers", [])
    fm = p.get("fake_markers", [])
    if len(am) < 2 or len(fm) < 2:
        print(f"  ⚠️ {p['id']}: only {len(am)} authentic / {len(fm)} fake markers")
        issues.append({"id": p["id"], "issue": "insufficient_markers", "severity": "warning"})

# === AUDIT 7: Provenance chain quality ===
print("\n--- AUDIT 7: Provenance chain quality ---")
prov = [p for p in pairs if p["type"] == "provenance_chain"]
for p in prov:
    vi = p.get("valid_indicators", [])
    rf = p.get("red_flags", [])
    vs = p.get("verification_steps", [])
    if len(vi) < 2 or len(rf) < 2 or len(vs) < 2:
        print(f"  ⚠️ {p['id']}: indicators={len(vi)} flags={len(rf)} steps={len(vs)}")
        issues.append({"id": p["id"], "issue": "thin_provenance_data", "severity": "warning"})

# === SUMMARY ===
print(f"\n{'='*60}")
print(f"AUDIT SUMMARY")
print(f"{'='*60}")
critical = [i for i in issues if i["severity"] == "critical"]
warnings = [i for i in issues if i["severity"] == "warning"]
print(f"  Critical issues: {len(critical)}")
print(f"  Warnings: {len(warnings)}")
print(f"  Pairs with no sources: {len(empty_sources)}")
print(f"  Vague sources to strengthen: {len(vague_unique)}")
print(f"  Book citations to verify: {len(book_citations)}")
print(f"  Scientific claims to verify: {len(suspect_pairs)}")
