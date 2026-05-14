#!/usr/bin/env python3
"""
Art Institute of Chicago — Japanese Art Ingestion Script
========================================================
CC0 public domain works from the Art Institute of Chicago.
No API key required. IIIF image support.

Usage:
  python3 scripts/ingest_chicago.py                    # Preview mode (no writes)
  python3 scripts/ingest_chicago.py --write            # Append to assets.json
  python3 scripts/ingest_chicago.py --category=bonsai  # Search specific category
"""

import json
import sys
import urllib.request
import urllib.parse
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_PATH = os.path.join(PROJECT_ROOT, 'data', 'assets.json')

API_BASE = "https://api.artic.edu/api/v1/artworks/search"
IIIF_BASE = "https://www.artic.edu/iiif/2"

# EDITION category → Chicago API search queries
CATEGORY_QUERIES = {
    "swords": ["japanese sword blade katana", "japanese armor samurai"],
    "ceramics": ["japanese tea bowl ceramics raku", "japanese stoneware pottery"],
    "ukiyoe": ["ukiyo-e japanese woodblock print", "japanese print hokusai hiroshige"],
    "painting": ["japanese painting ink screen", "japanese calligraphy scroll"],
    "lacquerware": ["japanese lacquer inro maki-e", "japanese lacquerware gold"],
    "netsuke": ["netsuke japanese miniature", "japanese ivory carving toggle"],
    "textiles": ["japanese kimono textile", "japanese noh costume silk"],
    "metalwork": ["japanese tsuba sword guard", "japanese metalwork shakudo"],
    "bonsai": ["bonsai potted tree japanese", "japanese potted plant pine suiseki viewing stone"],
    "sculpture": ["japanese buddhist sculpture", "japanese buddha wood carving"],
    "architecture": ["japanese folding screen byobu", "japanese architectural fitting"],
    "contemporary": ["contemporary japanese art", "japanese modern ceramics living national treasure"],
}

FIELDS = "id,title,artist_display,date_display,medium_display,dimensions,image_id,is_public_domain,classification_titles,department_title,credit_line,place_of_origin"


def search_chicago(query, limit=5):
    """Search Art Institute of Chicago API."""
    params = urllib.parse.urlencode({
        "q": query,
        "query[term][is_public_domain]": "true",
        "fields": FIELDS,
        "limit": limit,
    })
    url = f"{API_BASE}?{params}"
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'EDITION-Ingestion/1.0')
    data = json.loads(urllib.request.urlopen(req, timeout=15).read())
    return data


def to_edition_asset(item, category):
    """Convert Chicago API result to EDITION asset format."""
    if not item.get('image_id'):
        return None
    
    image_url = f"{IIIF_BASE}/{item['image_id']}/full/843,/0/default.jpg"
    
    return {
        "id": f"artic-{item['id']}",
        "category": category,
        "title_en": item.get('title', ''),
        "title_jp": "",  # Chicago API doesn't provide Japanese titles
        "period": item.get('date_display', ''),
        "era": "",
        "origin": item.get('place_of_origin', 'Japan'),
        "medium": item.get('medium_display', ''),
        "dimensions": item.get('dimensions', ''),
        "description": "",  # To be written by EDITION curator
        "significance": "",
        "image": image_url,
        "image_alt": f"{item.get('title', '')} by {item.get('artist_display', '').split(chr(10))[0]}, Art Institute of Chicago",
        "source": "Art Institute of Chicago",
        "source_url": f"https://www.artic.edu/artworks/{item['id']}",
        "license": "CC0",
        "_needs_curation": True,  # Flag: description needs to be written
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
    
    # Load existing assets to avoid duplicates
    if os.path.exists(ASSETS_PATH):
        with open(ASSETS_PATH) as f:
            existing = json.load(f)['assets']
            existing_ids = {a['id'] for a in existing}
    
    print("=" * 60)
    print("Art Institute of Chicago — Japanese Art Ingestion")
    print("=" * 60)
    
    for category, queries in categories.items():
        print(f"\n📂 {category}")
        for query in queries:
            try:
                data = search_chicago(query, limit=5)
                total = data.get('pagination', {}).get('total', 0)
                print(f"   🔍 '{query}' → {total} hits")
                
                for item in data.get('data', []):
                    asset = to_edition_asset(item, category)
                    if asset and asset['id'] not in existing_ids:
                        existing_ids.add(asset['id'])
                        all_results.append(asset)
                        print(f"      ✅ {asset['title_en'][:55]}")
                        print(f"         {asset['period']} | {asset['medium'][:50]}")
                    
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
