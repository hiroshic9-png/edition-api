#!/usr/bin/env python3
"""
KANTEISHI Training Data Seed Generator
=======================================
Generates initial training pairs from existing EDITION curated data.
All generated pairs are tier_3 (AI-generated, needs review).

Usage:
  python3 scripts/seed_training_data.py              # Preview
  python3 scripts/seed_training_data.py --write       # Write to data/training_pairs.json
"""

import json
import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CATEGORIES_PATH = os.path.join(PROJECT_ROOT, 'data', 'categories.json')
ASSETS_PATH = os.path.join(PROJECT_ROOT, 'data', 'assets.json')
OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'data', 'training_pairs.json')

NOW = datetime.utcnow().isoformat() + 'Z'


def generate_forensic_qa_from_category(cat):
    """Generate forensic QA pairs from category article sections."""
    pairs = []
    article = cat.get('article', {})
    slug = cat['slug']
    
    for i, section in enumerate(article.get('sections', [])):
        title = section.get('title', '')
        body = section.get('body', '')
        
        if not body or len(body) < 100:
            continue
        
        # Generate a forensic question from each section
        if 'authentication' in title.lower() or 'reading' in title.lower():
            pair = {
                "id": f"fqa-{slug}-{i+1:03d}",
                "type": "forensic_qa",
                "category": slug,
                "difficulty": "intermediate",
                "question": f"What are the key authentication considerations for {cat['title_en'].lower()}? Specifically regarding: {title}",
                "answer": body[:1500],  # Use the curated article text as the answer
                "evidence": [f"EDITION Category Article: {cat['title_en']} — {title}"],
                "related_assets": [],
                "tags": [slug, "authentication", title.lower().replace(' ', '_')],
                "created_at": NOW,
                "verified_by": "source_verified"  # tier_2: from our curated content
            }
            pairs.append(pair)
        
        elif 'master' in title.lower() or 'school' in title.lower() or 'lineage' in title.lower():
            pair = {
                "id": f"fqa-{slug}-{i+1:03d}",
                "type": "forensic_qa",
                "category": slug,
                "difficulty": "expert",
                "question": f"Describe the major schools and master practitioners in the field of {cat['title_en'].lower()}, focusing on: {title}",
                "answer": body[:1500],
                "evidence": [f"EDITION Category Article: {cat['title_en']} — {title}"],
                "related_assets": [],
                "tags": [slug, "schools", "masters", "lineage"],
                "created_at": NOW,
                "verified_by": "source_verified"
            }
            pairs.append(pair)
        
        else:
            pair = {
                "id": f"fqa-{slug}-{i+1:03d}",
                "type": "forensic_qa",
                "category": slug,
                "difficulty": "basic",
                "question": f"Explain the significance of {title.lower()} in the context of {cat['title_en'].lower()}.",
                "answer": body[:1500],
                "evidence": [f"EDITION Category Article: {cat['title_en']} — {title}"],
                "related_assets": [],
                "tags": [slug, title.lower().replace(' ', '_')],
                "created_at": NOW,
                "verified_by": "source_verified"
            }
            pairs.append(pair)
    
    return pairs


def generate_forensic_qa_from_asset(asset):
    """Generate forensic QA pairs from individual asset descriptions."""
    pairs = []
    
    if not asset.get('description') or len(asset.get('description', '')) < 50:
        return pairs
    
    pair = {
        "id": f"fqa-asset-{asset['id']}",
        "type": "forensic_qa",
        "category": asset['category'],
        "difficulty": "intermediate",
        "question": f"Describe the artwork '{asset['title_en']}' ({asset.get('period', '')}) and explain its art-historical significance.",
        "answer": f"{asset['description']}\n\nSignificance: {asset.get('significance', '')}",
        "evidence": [
            f"{asset.get('source', '')} — {asset.get('source_url', '')}",
        ],
        "related_assets": [asset['id']],
        "tags": [asset['category'], asset.get('era', ''), asset.get('medium', '')[:30]],
        "created_at": NOW,
        "verified_by": "source_verified"
    }
    pairs.append(pair)
    
    return pairs


def generate_authentic_vs_fake_from_categories(cats):
    """Extract authentic vs fake markers from authentication sections."""
    pairs = []
    
    for cat in cats:
        slug = cat['slug']
        article = cat.get('article', {})
        
        for section in article.get('sections', []):
            title = section.get('title', '')
            body = section.get('body', '')
            
            if 'authentication' in title.lower() or 'scientific' in title.lower():
                pair = {
                    "id": f"avf-{slug}-001",
                    "type": "authentic_vs_fake",
                    "category": slug,
                    "subject": f"{cat['title_en']} — Authentication Framework",
                    "authentic_markers": [],
                    "fake_markers": [],
                    "raw_knowledge": body[:2000],
                    "confidence_notes": "Extracted from EDITION curated authentication framework. Needs expert decomposition into structured markers.",
                    "sources": [f"EDITION Category Article: {cat['title_en']} — {title}"],
                    "verified_by": "ai_generated",
                    "_needs_decomposition": True
                }
                pairs.append(pair)
                break  # One per category
    
    return pairs


def main():
    write_mode = '--write' in sys.argv
    
    with open(CATEGORIES_PATH) as f:
        categories = json.load(f)['categories']
    with open(ASSETS_PATH) as f:
        assets = json.load(f)['assets']
    
    all_pairs = []
    
    # 1. Generate from category articles
    print("=== Generating forensic QA from category articles ===")
    for cat in categories:
        pairs = generate_forensic_qa_from_category(cat)
        all_pairs.extend(pairs)
        print(f"  {cat['slug']:15s}: {len(pairs)} pairs")
    
    # 2. Generate from individual assets
    print("\n=== Generating forensic QA from asset descriptions ===")
    asset_pairs = []
    for asset in assets:
        pairs = generate_forensic_qa_from_asset(asset)
        asset_pairs.extend(pairs)
    all_pairs.extend(asset_pairs)
    print(f"  Total asset pairs: {len(asset_pairs)}")
    
    # 3. Generate authentic vs fake frameworks
    print("\n=== Generating authentic vs fake frameworks ===")
    avf_pairs = generate_authentic_vs_fake_from_categories(categories)
    all_pairs.extend(avf_pairs)
    print(f"  Total avf frameworks: {len(avf_pairs)}")
    
    # Summary
    from collections import Counter
    type_counts = Counter(p['type'] for p in all_pairs)
    tier_counts = Counter(p['verified_by'] for p in all_pairs)
    cat_counts = Counter(p['category'] for p in all_pairs)
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL TRAINING PAIRS: {len(all_pairs)}")
    print(f"\nBy type:")
    for t, c in type_counts.items():
        print(f"  {t}: {c}")
    print(f"\nBy quality tier:")
    for t, c in tier_counts.items():
        print(f"  {t}: {c}")
    print(f"\nBy category:")
    for cat, c in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat:15s}: {c}")
    
    if write_mode:
        output = {
            "schema_version": "1.0.0",
            "generated_at": NOW,
            "total_pairs": len(all_pairs),
            "pairs": all_pairs
        }
        with open(OUTPUT_PATH, 'w') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Written to {OUTPUT_PATH}")
    else:
        print(f"\nℹ️  Preview mode. Run with --write to save.")


if __name__ == '__main__':
    main()
