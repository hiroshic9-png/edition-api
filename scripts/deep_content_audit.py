#!/usr/bin/env python3
"""
EDITION Training Data Deep Content Audit
Every single pair is examined for factual accuracy, verifiable sources, and data integrity.
"""
import json
import re

PAIRS_PATH = "/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/training_pairs.json"

def load_pairs():
    with open(PAIRS_PATH) as f:
        return json.load(f)["pairs"]

def audit_forensic_qa(pairs):
    """Audit forensic_qa pairs for content accuracy issues"""
    fqa_pairs = [p for p in pairs if p["type"] == "forensic_qa"]
    issues = []
    
    for p in fqa_pairs:
        pid = p["id"]
        question = p.get("question", "")
        answer = p.get("answer", "")
        evidence = p.get("evidence", [])
        verified = p.get("verified_by", "")
        
        # Check 1: Verified_by = source_verified but no URL in evidence
        if verified == "source_verified":
            evidence_str = json.dumps(evidence)
            if "http" not in evidence_str:
                issues.append({
                    "id": pid,
                    "severity": "WARNING",
                    "issue": "source_verified but no URL in evidence",
                    "detail": f"evidence: {str(evidence)[:100]}"
                })
        
        # Check 2: Answer contains specific numerical claims (dates, measurements, prices)
        # that need verification
        date_patterns = re.findall(r'\b(1[0-9]{3}|20[0-2][0-9])\b', answer)
        price_patterns = re.findall(r'[\$¥£€][\d,\.]+(?:\s*(?:million|billion))?', answer)
        percentage_patterns = re.findall(r'\d+\.?\d*\s*%', answer)
        
        specific_claims = []
        if price_patterns:
            specific_claims.extend([f"price: {p}" for p in price_patterns])
        if percentage_patterns:
            specific_claims.extend([f"percentage: {p}" for p in percentage_patterns])
        
        if specific_claims and verified != "source_verified":
            issues.append({
                "id": pid,
                "severity": "WARNING",
                "issue": "Contains specific numerical claims but not source_verified",
                "detail": f"claims: {specific_claims}"
            })
        
        # Check 3: Answer length too short (potentially low quality)
        if len(answer) < 50:
            issues.append({
                "id": pid,
                "severity": "WARNING",
                "issue": "Answer too short",
                "detail": f"length: {len(answer)}"
            })
        
        # Check 4: Look for potentially fabricated book/author references
        book_refs = re.findall(r'"([^"]+)"(?:\s*\([^)]+\))?(?:\s*by\s+([A-Z][a-z]+\s+[A-Z][a-z]+))?', answer)
        author_refs = re.findall(r'(?:by|according to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', answer)
        
        if book_refs or author_refs:
            refs = []
            for b in book_refs:
                if b[0] and len(b[0]) > 5:
                    refs.append(f'book: "{b[0]}"')
            for a in author_refs:
                refs.append(f'author: {a}')
            if refs:
                issues.append({
                    "id": pid,
                    "severity": "CHECK",
                    "issue": "Contains book/author references that need verification",
                    "detail": str(refs)[:200]
                })
        
        # Check 5: Look for temperature/scientific claims
        temp_claims = re.findall(r'(\d+(?:,\d+)?)\s*°[CF]', answer)
        if temp_claims:
            issues.append({
                "id": pid,
                "severity": "CHECK",
                "issue": "Contains temperature claims needing verification",
                "detail": f"temperatures: {temp_claims}"
            })
    
    return issues

def audit_authentic_vs_fake(pairs):
    """Audit authentic_vs_fake pairs"""
    avf_pairs = [p for p in pairs if p["type"] == "authentic_vs_fake"]
    issues = []
    
    for p in avf_pairs:
        pid = p["id"]
        auth_markers = p.get("authentic_markers", [])
        fake_markers = p.get("fake_markers", [])
        sources = p.get("sources", [])
        
        # Check 1: Minimum markers
        if len(auth_markers) < 2:
            issues.append({
                "id": pid,
                "severity": "WARNING",
                "issue": "Too few authentic markers",
                "detail": f"count: {len(auth_markers)}"
            })
        if len(fake_markers) < 2:
            issues.append({
                "id": pid,
                "severity": "WARNING",
                "issue": "Too few fake markers",
                "detail": f"count: {len(fake_markers)}"
            })
        
        # Check 2: Sources quality
        has_verifiable = False
        for s in sources:
            if isinstance(s, str) and ('http' in s or len(s) > 20):
                has_verifiable = True
            elif isinstance(s, dict) and s.get('url'):
                has_verifiable = True
        
        if not has_verifiable:
            issues.append({
                "id": pid,
                "severity": "WARNING",
                "issue": "No verifiable sources",
                "detail": f"sources: {str(sources)[:100]}"
            })
        
        # Check 3: Marker detail quality
        for i, m in enumerate(auth_markers):
            if isinstance(m, dict):
                detail = m.get("detail", "")
                if len(detail) < 15:
                    issues.append({
                        "id": pid,
                        "severity": "WARNING",
                        "issue": f"Authentic marker #{i+1} has insufficient detail",
                        "detail": f"'{detail}'"
                    })
        
        for i, m in enumerate(fake_markers):
            if isinstance(m, dict):
                detail = m.get("detail", "")
                if len(detail) < 15:
                    issues.append({
                        "id": pid,
                        "severity": "WARNING",
                        "issue": f"Fake marker #{i+1} has insufficient detail",
                        "detail": f"'{detail}'"
                    })
    
    return issues

def audit_provenance_chain(pairs):
    """Audit provenance_chain pairs"""
    prov_pairs = [p for p in pairs if p["type"] == "provenance_chain"]
    issues = []
    
    for p in prov_pairs:
        pid = p["id"]
        sources = p.get("sources", [])
        valid_indicators = p.get("valid_indicators", [])
        red_flags = p.get("red_flags", [])
        verification_steps = p.get("verification_steps", [])
        
        # Check 1: Must have verification steps
        if not verification_steps or len(verification_steps) < 2:
            issues.append({
                "id": pid,
                "severity": "WARNING",
                "issue": "Insufficient verification steps",
                "detail": f"count: {len(verification_steps) if verification_steps else 0}"
            })
        
        # Check 2: Sources quality
        has_verifiable = False
        for s in sources:
            if isinstance(s, str) and ('http' in s or len(s) > 20):
                has_verifiable = True
        if not has_verifiable:
            issues.append({
                "id": pid,
                "severity": "WARNING",
                "issue": "No verifiable sources for provenance claims",
                "detail": f"sources: {str(sources)[:100]}"
            })
        
        # Check 3: Red flags must be specific
        if len(red_flags) < 2:
            issues.append({
                "id": pid,
                "severity": "WARNING",
                "issue": "Too few red flags defined",
                "detail": f"count: {len(red_flags)}"
            })
    
    return issues

def audit_price_comparable(pairs):
    """Audit price_comparable pairs — most critical for accuracy"""
    pc_pairs = [p for p in pairs if p["type"] == "price_comparable"]
    issues = []
    
    for p in pc_pairs:
        pid = p["id"]
        comparables = p.get("comparables", [])
        sources = p.get("sources", [])
        
        # Check 1: Each comparable must have source_url
        for i, c in enumerate(comparables):
            if isinstance(c, dict):
                if not c.get("source_url"):
                    issues.append({
                        "id": pid,
                        "severity": "CRITICAL",
                        "issue": f"Comparable #{i+1} missing source_url",
                        "detail": f"sale: {c.get('description', '')[:60]}, price: {c.get('sale_price', 'N/A')}"
                    })
                
                # Check price is reasonable
                price = c.get("sale_price", 0)
                if isinstance(price, (int, float)):
                    if price <= 0:
                        issues.append({
                            "id": pid,
                            "severity": "CRITICAL",
                            "issue": f"Comparable #{i+1} has invalid price",
                            "detail": f"price: {price}"
                        })
                
                # Check sale_date format
                sale_date = c.get("sale_date", "")
                if sale_date and not re.match(r'\d{4}-\d{2}-\d{2}', str(sale_date)):
                    issues.append({
                        "id": pid,
                        "severity": "WARNING",
                        "issue": f"Comparable #{i+1} has non-standard date format",
                        "detail": f"date: {sale_date}"
                    })
                
                # Check auction house is named
                auction = c.get("auction_house", "")
                if not auction:
                    issues.append({
                        "id": pid,
                        "severity": "WARNING",
                        "issue": f"Comparable #{i+1} missing auction_house",
                        "detail": f"sale: {c.get('description', '')[:60]}"
                    })
    
    return issues

def audit_cross_category(pairs):
    """Cross-category checks"""
    issues = []
    
    # Check for duplicates
    ids = [p["id"] for p in pairs]
    seen = {}
    for pid in ids:
        if pid in seen:
            issues.append({
                "id": pid,
                "severity": "CRITICAL",
                "issue": "Duplicate ID",
                "detail": "Same ID appears multiple times"
            })
        seen[pid] = True
    
    # Check question/subject uniqueness (dedup)
    questions = {}
    for p in pairs:
        q = p.get("question", "") or p.get("subject", "")
        if q in questions:
            issues.append({
                "id": p["id"],
                "severity": "WARNING",
                "issue": "Duplicate question/subject",
                "detail": f"Same as {questions[q]}: '{q[:60]}'"
            })
        else:
            questions[q] = p["id"]
    
    return issues

def main():
    pairs = load_pairs()
    
    print("=" * 80)
    print("EDITION TRAINING DATA — DEEP CONTENT AUDIT")
    print(f"Total pairs: {len(pairs)}")
    print("=" * 80)
    
    all_issues = []
    
    # Run all audits
    print("\n📋 Auditing forensic_qa...")
    fqa_issues = audit_forensic_qa(pairs)
    all_issues.extend(fqa_issues)
    
    print("📋 Auditing authentic_vs_fake...")
    avf_issues = audit_authentic_vs_fake(pairs)
    all_issues.extend(avf_issues)
    
    print("📋 Auditing provenance_chain...")
    prov_issues = audit_provenance_chain(pairs)
    all_issues.extend(prov_issues)
    
    print("📋 Auditing price_comparable...")
    pc_issues = audit_price_comparable(pairs)
    all_issues.extend(pc_issues)
    
    print("📋 Cross-category checks...")
    cross_issues = audit_cross_category(pairs)
    all_issues.extend(cross_issues)
    
    # Summary
    critical = [i for i in all_issues if i["severity"] == "CRITICAL"]
    warnings = [i for i in all_issues if i["severity"] == "WARNING"]
    checks = [i for i in all_issues if i["severity"] == "CHECK"]
    
    print(f"\n{'='*80}")
    print(f"AUDIT RESULTS")
    print(f"{'='*80}")
    print(f"🔴 CRITICAL: {len(critical)}")
    print(f"🟡 WARNING:  {len(warnings)}")
    print(f"🔍 CHECK:    {len(checks)}")
    
    if critical:
        print(f"\n--- CRITICAL ISSUES ---")
        for i in critical:
            print(f"  [{i['id']}] {i['issue']}: {i['detail']}")
    
    if warnings:
        print(f"\n--- WARNINGS (top 30) ---")
        for i in warnings[:30]:
            print(f"  [{i['id']}] {i['issue']}: {i['detail'][:80]}")
    
    if checks:
        print(f"\n--- ITEMS TO CHECK (need manual/API verification) ---")
        for i in checks[:20]:
            print(f"  [{i['id']}] {i['issue']}: {i['detail'][:80]}")
    
    # Save results
    output_path = "/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/content_audit_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "total_pairs": len(pairs),
            "critical": len(critical),
            "warnings": len(warnings),
            "checks": len(checks),
            "issues": all_issues
        }, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {output_path}")

    # Detailed breakdown of verified_by=source_verified without URLs
    sv_no_url = [i for i in all_issues if i["issue"] == "source_verified but no URL in evidence"]
    print(f"\n--- source_verified without URL count: {len(sv_no_url)} ---")

if __name__ == "__main__":
    main()
