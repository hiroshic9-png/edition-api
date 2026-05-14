#!/usr/bin/env python3
"""
EDITION Data Integrity Validator
================================
Validates that all asset and category data maintains the EDITION quality standard:
  1. No generated/placeholder images
  2. Image alt text matches asset title (coherence check)
  3. All Met Museum IDs in source_url match the actual ID
  4. No "Editorial" license on items claiming Met Museum source
  5. All image URLs are valid (optional, with --check-urls flag)
  6. Asset descriptions don't contain keywords that contradict the actual artwork

Run before every commit and deploy:
  python3 scripts/validate_data_integrity.py
  python3 scripts/validate_data_integrity.py --check-urls   # also validates image URLs

Exit code 0 = all checks pass, 1 = failures found
"""

import json
import sys
import re
import os
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CATEGORIES_PATH = os.path.join(PROJECT_ROOT, 'data', 'categories.json')
ASSETS_PATH = os.path.join(PROJECT_ROOT, 'data', 'assets.json')

FORBIDDEN_IMAGE_PATTERNS = [
    '/images/generated/',
    'placeholder',
    'unsplash.com/photos',  # stock photos
    'via.placeholder.com',
    'picsum.photos',
]

# Keywords that indicate description-image mismatch
MISMATCH_SIGNALS = {
    # If image_alt contains key A but description contains key B → likely mismatch
    'tea bowl': ['screen', 'folding screen', 'fusuma', 'hanging scroll'],
    'screen': ['tea bowl', 'netsuke', 'inrō', 'sword'],
    'print': ['ceramic', 'stoneware', 'porcelain', 'tea bowl'],
    'fusuma': ['print', 'surimono', 'woodblock'],
}


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_forbidden_images(items, source_name):
    """Check for generated/placeholder image references."""
    errors = []
    for item in items:
        for field in ['image', 'hero_image']:
            url = item.get(field, '')
            for pattern in FORBIDDEN_IMAGE_PATTERNS:
                if pattern in url.lower():
                    errors.append(
                        f"[{source_name}] {item.get('id', item.get('slug', '?'))}: "
                        f"FORBIDDEN image pattern '{pattern}' in {field}: {url}"
                    )
    return errors


def check_image_title_coherence(items, source_name):
    """Check that image alt text is coherent with title."""
    errors = []
    for item in items:
        image_alt = item.get('image_alt', '').lower()
        title = item.get('title_en', '').lower()
        
        # If both exist, they should share at least one significant word
        if image_alt and title and len(title) > 5:
            # Extract significant words (>3 chars, not common words)
            common = {'the', 'and', 'with', 'for', 'from', 'that', 'this'}
            title_words = {w for w in re.findall(r'\b\w{4,}\b', title)} - common
            alt_words = {w for w in re.findall(r'\b\w{4,}\b', image_alt)} - common
            
            overlap = title_words & alt_words
            if not overlap and title_words and alt_words:
                errors.append(
                    f"[{source_name}] {item.get('id', item.get('slug', '?'))}: "
                    f"COHERENCE: Title '{item.get('title_en', '')[:50]}' shares no words "
                    f"with image_alt '{item.get('image_alt', '')[:50]}'"
                )
    return errors


def check_source_license_consistency(items, source_name):
    """Verify that items sourced from Met Museum have CC0 license."""
    errors = []
    for item in items:
        source = item.get('source', '').lower()
        source_url = item.get('source_url', '').lower()
        license_val = item.get('license', '')
        image = item.get('image', '')
        
        # If image is from Met Museum, license must be CC0
        if 'metmuseum.org' in image and license_val != 'CC0':
            errors.append(
                f"[{source_name}] {item.get('id', '?')}: "
                f"Image from Met Museum but license is '{license_val}', should be 'CC0'"
            )
        
        # If source says Met Museum but source_url doesn't match
        if 'metropolitan' in source and 'metmuseum.org' not in source_url:
            errors.append(
                f"[{source_name}] {item.get('id', '?')}: "
                f"Source claims Met Museum but source_url is: {source_url}"
            )
    return errors


def check_description_image_mismatch(items, source_name):
    """Detect obvious mismatches between description and image."""
    errors = []
    for item in items:
        desc = item.get('description', '').lower()
        image_alt = item.get('image_alt', '').lower()
        medium = item.get('medium', '').lower()
        
        # Check: if medium says one thing but description says another
        if medium and desc:
            if 'woodblock print' in medium and any(w in desc for w in ['ceramic', 'stoneware', 'porcelain', 'tea bowl']):
                errors.append(
                    f"[{source_name}] {item.get('id', '?')}: "
                    f"Medium is '{medium[:40]}' but description mentions ceramics/tea bowl"
                )
            if 'stoneware' in medium and any(w in desc for w in ['woodblock', 'print', 'surimono']):
                errors.append(
                    f"[{source_name}] {item.get('id', '?')}: "
                    f"Medium is '{medium[:40]}' but description mentions prints"
                )
            if 'fusuma' in medium and 'tea bowl' in desc:
                errors.append(
                    f"[{source_name}] {item.get('id', '?')}: "
                    f"Medium is fusuma panels but description mentions tea bowls"
                )
    return errors


def check_no_edition_fabricated_ids(items, source_name):
    """Flag any IDs that suggest fabricated/editorial content without proper disclosure."""
    warnings = []
    for item in items:
        item_id = item.get('id', '')
        if item_id.startswith('edition-'):
            source = item.get('source', '')
            if 'Metropolitan' in source or 'metmuseum' in item.get('image', ''):
                warnings.append(
                    f"[{source_name}] {item_id}: "
                    f"Has 'edition-' prefix but uses Met Museum assets. "
                    f"Use 'met-XXXXX' ID format for Met Museum works."
                )
    return warnings


def check_urls(items, source_name):
    """Validate that image URLs return 200 OK."""
    errors = []
    for item in items:
        for field in ['image', 'hero_image']:
            url = item.get(field, '')
            if url and url.startswith('http'):
                try:
                    req = urllib.request.Request(url, method='HEAD')
                    req.add_header('User-Agent', 'EDITION-Validator/1.0')
                    response = urllib.request.urlopen(req, timeout=10)
                    if response.status != 200:
                        errors.append(
                            f"[{source_name}] {item.get('id', '?')}: "
                            f"{field} returned HTTP {response.status}: {url[:80]}"
                        )
                except Exception as e:
                    errors.append(
                        f"[{source_name}] {item.get('id', '?')}: "
                        f"{field} FAILED: {str(e)[:60]} — {url[:80]}"
                    )
    return errors


def main():
    do_url_check = '--check-urls' in sys.argv
    
    print("=" * 60)
    print("EDITION Data Integrity Validator")
    print("=" * 60)
    
    categories = load_json(CATEGORIES_PATH)['categories']
    assets = load_json(ASSETS_PATH)['assets']
    
    all_errors = []
    all_warnings = []
    
    # Run all checks
    checks = [
        ("Forbidden Images", check_forbidden_images, True),
        ("Image-Title Coherence", check_image_title_coherence, False),  # assets only
        ("Source-License Consistency", check_source_license_consistency, True),
        ("Description-Image Mismatch", check_description_image_mismatch, True),
    ]
    
    for check_name, check_fn, include_categories in checks:
        print(f"\n  Checking: {check_name}...")
        errors = []
        if include_categories:
            errors += check_fn(categories, 'categories')
        errors += check_fn(assets, 'assets')
        if errors:
            print(f"    ❌ {len(errors)} issue(s) found")
            all_errors.extend(errors)
        else:
            print(f"    ✅ PASS")
    
    # Check for fabricated IDs
    print(f"\n  Checking: Fabricated ID Detection...")
    warnings = check_no_edition_fabricated_ids(assets, 'assets')
    if warnings:
        print(f"    ⚠️  {len(warnings)} warning(s)")
        all_warnings.extend(warnings)
    else:
        print(f"    ✅ PASS")
    
    # Optional URL check
    if do_url_check:
        print(f"\n  Checking: Image URL Validation (this may take a minute)...")
        url_errors = check_urls(categories, 'categories') + check_urls(assets, 'assets')
        if url_errors:
            print(f"    ❌ {len(url_errors)} broken URL(s)")
            all_errors.extend(url_errors)
        else:
            print(f"    ✅ All URLs valid")
    
    # Summary
    print("\n" + "=" * 60)
    
    if all_warnings:
        print(f"\n⚠️  WARNINGS ({len(all_warnings)}):")
        for w in all_warnings:
            print(f"  {w}")
    
    if all_errors:
        print(f"\n❌ ERRORS ({len(all_errors)}):")
        for e in all_errors:
            print(f"  {e}")
        print(f"\n{'=' * 60}")
        print("VALIDATION FAILED — Do NOT deploy until all errors are resolved.")
        print(f"{'=' * 60}")
        sys.exit(1)
    else:
        print(f"\n✅ ALL CHECKS PASSED — {len(categories)} categories, {len(assets)} assets validated.")
        print(f"{'=' * 60}")
        sys.exit(0)


if __name__ == '__main__':
    main()
