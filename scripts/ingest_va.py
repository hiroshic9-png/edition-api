#!/usr/bin/env python3
"""
Victoria & Albert Museum — Japanese Art Ingestion Script
========================================================
Works from the V&A Museum's collection API.
No API key required.

Usage:
  python3 scripts/ingest_va.py                    # Preview mode
  python3 scripts/ingest_va.py --write            # Append to assets.json
  python3 scripts/ingest_va.py --category=swords  # Specific category
"""

import json
import sys
import urllib.request
import urllib.parse
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_PATH = os.path.join(PROJECT_ROOT, 'data', 'assets.json')

API_BASE = "https://api.vam.ac.uk/v2/objects/search"

# EDITION category → V&A search queries
CATEGORY_QUERIES = {
    "swords": ["japanese sword", "japanese armour katana"],
    "ceramics": ["japanese ceramics tea", "japanese porcelain stoneware"],
    "ukiyoe": ["japanese woodblock print", "ukiyo-e"],
    "painting": ["japanese painting scroll", "japanese screen"],
    "lacquerware": ["japanese lacquer", "japanese inro"],
    "netsuke": ["netsuke", "japanese miniature carving"],
    "textiles": ["japanese kimono", "japanese textile silk"],
    "metalwork": ["japanese tsuba", "japanese metalwork"],
    "bonsai": ["bonsai", "japanese potted plant"],
    "sculpture": ["japanese sculpture buddha", "japanese carving"],
    "architecture": ["japanese screen furniture", "japanese architectural"],
    "contemporary": ["japanese contemporary", "japanese modern art"],
}


def search_va(query, limit=5):
    """Search V&A Museum API."""
    params = urllib.parse.urlencode({
        "q": query,
        "images_exist": "true",
        "page_size": limit,
    })
    url = f"{API_BASE}?{params}"
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'EDITION-Ingestion/1.0')
    data = json.loads(urllib.request.urlopen(req, timeout=15).read())
    return data


def get_image_url(record):
    """Extract best available image URL from V&A record."""
    images = record.get('_images', {})
    iiif = images.get('_iiif_image_base_url', '')
    if iiif:
        return f"{iiif}/full/800,/0/default.jpg"
    primary = images.get('_primary_thumbnail', '')
    if primary:
        # Upgrade thumbnail to larger size
        return primary.replace('!100,100', '!800,800')
    return None


def to_edition_asset(record, category):
    """Convert V&A API result to EDITION asset format."""
    image_url = get_image_url(record)
    if not image_url:
        return None
    
    sys_num = record.get('systemNumber', '')
    title = record.get('_primaryTitle', '') or record.get('objectType', 'Untitled')
    artist = record.get('_primaryMaker', {}).get('name', '')
    
    return {
        "id": f"va-{sys_num}",
        "category": category,
        "title_en": title,
        "title_jp": "",
        "period": record.get('_primaryDate', ''),
        "era": "",
        "origin": record.get('_primaryPlace', 'Japan'),
        "medium": ", ".join(record.get('materialsAndTechniques', '').split('; ')[:3]) if record.get('materialsAndTechniques') else '',
        "dimensions": "",
        "description": "",  # To be written by EDITION curator
        "significance": "",
        "image": image_url,
        "image_alt": f"{title}{f' by {artist}' if artist else ''}, Victoria and Albert Museum",
        "source": "Victoria and Albert Museum",
        "source_url": f"https://collections.vam.ac.uk/item/{sys_num}/",
        "license": "CC BY-NC",  # V&A uses CC BY-NC for most images
        "_needs_curation": True,
    }


def main():
    write_mode = '--write' in sys.argv
    target_cat = None
    for arg in sys.argv:
        if arg.startswith('--category='):
            target_cat = arg.split('=')[1]
    
    categories = {target_cat: CATEGORY_QUERIES[target_cat]} if target_cat else CATEGORY_QUERIES
    
    all_results = []
    existing_ids = set()
    
    if os.path.exists(ASSETS_PATH):
        with open(ASSETS_PATH) as f:
            existing = json.load(f)['assets']
            existing_ids = {a['id'] for a in existing}
    
    print("=" * 60)
    print("Victoria & Albert Museum — Japanese Art Ingestion")
    print("=" * 60)
    
    for category, queries in categories.items():
        print(f"\n📂 {category}")
        for query in queries:
            try:
                data = search_va(query, limit=5)
                total = data.get('info', {}).get('record_count', 0)
                print(f"   🔍 '{query}' → {total} hits")
                
                for record in data.get('records', [])[:5]:
                    asset = to_edition_asset(record, category)
                    if asset and asset['id'] not in existing_ids:
                        existing_ids.add(asset['id'])
                        all_results.append(asset)
                        print(f"      ✅ {asset['title_en'][:55]}")
                        print(f"         {asset['period']} | {asset.get('origin','')}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"Found {len(all_results)} new assets across {len(categories)} categories")
    
    if write_mode and all_results:
        with open(ASSETS_PATH) as f:
            data = json.load(f)
        data['assets'].extend(all_results)
        with open(ASSETS_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Appended {len(all_results)} assets to {ASSETS_PATH}")
        print(f"⚠️  Assets marked with _needs_curation=true require description writing")
    elif all_results:
        print(f"ℹ️  Preview mode. Run with --write to append to assets.json")
    
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
