#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════
EDITION — Art Platform Japan (DAJ) Artist Enrichment
═══════════════════════════════════════════════════════════

Harvests artist data from Art Platform Japan's Dictionary of
Artists in Japan (DAJ) and cross-matches with KANTEISHI's
existing artist profiles to enrich birth/death years and
Japanese name variants.

Source: https://artplatform.go.jp/artists (NCAR / 国立アートリサーチセンター)
License: Public research data, non-commercial use

Usage:
  python3 apj_enrichment.py --harvest   # Harvest DAJ index pages
  python3 apj_enrichment.py --match     # Match against KANTEISHI artists
  python3 apj_enrichment.py --all       # Both steps
"""

import json
import re
import sys
import time
import unicodedata
import logging
from pathlib import Path
from typing import Optional

# Rate limit: respect government server
RATE_LIMIT_SECONDS = 2.0
BASE_URL = "https://artplatform.go.jp/artists"
DATA_DIR = Path("/Users/hiroshi/edition-collab/kanteishi/data")
OUTPUT_FILE = DATA_DIR / "apj_artists.jsonl"
PROFILES_FILE = DATA_DIR / "artist_profiles_v3.jsonl"
ENRICHED_FILE = DATA_DIR / "artist_profiles_v4.jsonl"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
log = logging.getLogger(__name__)


def normalize_name(name: str) -> str:
    """Normalize artist name for fuzzy matching."""
    # Full-width to half-width
    name = unicodedata.normalize('NFKC', name)
    # Remove all whitespace types
    name = re.sub(r'[\s\u3000]+', '', name)
    # Lowercase for romaji
    name = name.lower()
    return name


def parse_artist_line(line: str) -> Optional[dict]:
    """
    Parse a single DAJ artist entry line.
    
    Format examples:
    [安倍安人ABE Anjin1938–APJ A3989](url)
    [会田誠AIDA Makoto1965–APJ A1004](url)
    [阿部展也ABE Nobuya1913–1971APJ A1040](url)
    """
    # Match: [JP_NAME ROMAJI_NAME YEARS APJ ID](URL)
    m = re.match(
        r'\[(.+?)((?:[A-ZĀĪŪĒŌ][\w\s,.\-\(\)ʼ\']*?))'
        r'(\d{4}(?:-\d{2}-\d{2})?(?:（.*?）)?)'
        r'[–\-]'
        r'(\d{4})?'
        r'APJ\s+(A\d+)\]'
        r'\((https?://[^\)]+)\)',
        line
    )
    if not m:
        # Try simpler pattern without death year
        m2 = re.match(
            r'\[(.+?)((?:[A-ZĀĪŪĒŌ][\w\s,.\-\(\)ʼ\']*?))'
            r'APJ\s+(A\d+)\]'
            r'\((https?://[^\)]+)\)',
            line
        )
        if m2:
            return {
                'name_ja': m2.group(1).strip(),
                'name_romaji': m2.group(2).strip(),
                'birth_year': None,
                'death_year': None,
                'apj_id': m2.group(3),
                'url': m2.group(4)
            }
        return None
    
    # Extract birth year (just the 4-digit year)
    birth_raw = m.group(3)
    birth_year = int(birth_raw[:4]) if birth_raw else None
    death_year = int(m.group(4)) if m.group(4) else None
    
    return {
        'name_ja': m.group(1).strip(),
        'name_romaji': m.group(2).strip(),
        'birth_year': birth_year,
        'death_year': death_year,
        'apj_id': m.group(5),
        'url': m.group(6)
    }


def harvest_daj():
    """Harvest all artist entries from DAJ index pages."""
    try:
        import requests
    except ImportError:
        log.error("requests not available. Install: pip install requests")
        return
    
    from html.parser import HTMLParser
    
    log.info("═══ Harvesting Art Platform Japan DAJ ═══")
    
    all_artists = []
    
    # DAJ lists all artists on the main /artists page with anchor sections
    log.info(f"Fetching {BASE_URL}...")
    
    try:
        resp = requests.get(BASE_URL, timeout=30, headers={
            'User-Agent': 'EDITION-Research/1.0 (Academic Research; contact: h.sato@c-9.co.jp)',
            'Accept-Language': 'en,ja'
        })
        resp.raise_for_status()
    except Exception as e:
        log.error(f"Failed to fetch DAJ: {e}")
        return
    
    content = resp.text
    
    # Parse all artist links from the page
    # Pattern: <a href="/artists/AXXX">JP_NAME<span>ROMAJI</span><span>YEARS</span><span>APJ ID</span></a>
    # Actually the HTML structure varies, so let's extract from link texts
    
    # Find all artist entry patterns in the HTML
    # Each entry is a link like: <a href="/artists/A1004">会田誠<span>AIDA Makoto</span><span>1965–</span><span>APJ A1004</span></a>
    
    # More robust: find all /artists/A\d+ links
    link_pattern = re.compile(
        r'<a[^>]*href="(/artists/(A\d+))"[^>]*>(.*?)</a>',
        re.DOTALL
    )
    
    for m in link_pattern.finditer(content):
        url_path = m.group(1)
        apj_id = m.group(2)
        inner_html = m.group(3)
        
        # Clean HTML tags
        text = re.sub(r'<[^>]+>', ' ', inner_html).strip()
        text = re.sub(r'\s+', ' ', text)
        
        # Try to parse structured data
        # Common format: "日本語名 ROMAJI Name 1900–1999 APJ A1234"
        parsed = parse_entry_text(text, apj_id, f"https://artplatform.go.jp{url_path}")
        if parsed:
            all_artists.append(parsed)
    
    if not all_artists:
        log.warning("No artists parsed from HTML. Trying text-based approach...")
        # Fallback: parse the rendered text content
        text_content = re.sub(r'<[^>]+>', '\n', content)
        for line in text_content.split('\n'):
            line = line.strip()
            if 'APJ A' in line:
                parsed = parse_entry_text(line, None, None)
                if parsed:
                    all_artists.append(parsed)
    
    log.info(f"Parsed {len(all_artists)} artist entries")
    
    # Deduplicate by APJ ID
    seen = set()
    unique = []
    for a in all_artists:
        if a['apj_id'] not in seen:
            seen.add(a['apj_id'])
            unique.append(a)
    
    log.info(f"Unique artists: {len(unique)}")
    
    # Save
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for a in unique:
            f.write(json.dumps(a, ensure_ascii=False) + '\n')
    
    log.info(f"Saved to {OUTPUT_FILE}")
    return unique


def parse_entry_text(text: str, apj_id: Optional[str], url: Optional[str]) -> Optional[dict]:
    """Parse artist entry from cleaned text."""
    if not text or len(text) < 3:
        return None
    
    # Extract APJ ID if not provided
    if not apj_id:
        m = re.search(r'APJ\s+(A\d+)', text)
        if m:
            apj_id = m.group(1)
        else:
            return None
    
    # Try to split Japanese name from Romaji
    # Japanese chars come first, then uppercase Romaji
    m = re.match(
        r'(.+?)'                        # Japanese name (greedy until romaji)
        r'([A-ZĀĪŪĒŌÜ][A-Za-zāīūēōü\s,.\-\(\)ʼ\']+?)'  # Romaji name
        r'(?:(\d{4})(?:[–\-](\d{4})?)?)?'  # Optional birth-death
        r'\s*(?:APJ\s+A\d+)?',           # Optional APJ ID
        text
    )
    
    if m:
        name_ja = m.group(1).strip()
        name_romaji = m.group(2).strip()
        birth_year = int(m.group(3)) if m.group(3) else None
        death_year = int(m.group(4)) if m.group(4) else None
    else:
        # Can't parse, store raw
        name_ja = text
        name_romaji = None
        birth_year = None
        death_year = None
    
    if not url:
        url = f"https://artplatform.go.jp/artists/{apj_id}"
    
    return {
        'name_ja': name_ja,
        'name_romaji': name_romaji,
        'birth_year': birth_year,
        'death_year': death_year,
        'apj_id': apj_id,
        'url': url,
        'source': 'apj_daj'
    }


def match_and_enrich():
    """Match DAJ artists against KANTEISHI profiles and enrich."""
    log.info("═══ Matching DAJ against KANTEISHI Profiles ═══")
    
    # Load DAJ data
    if not OUTPUT_FILE.exists():
        log.error(f"DAJ data not found: {OUTPUT_FILE}. Run --harvest first.")
        return
    
    apj_artists = []
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                apj_artists.append(json.loads(line))
    
    log.info(f"DAJ artists loaded: {len(apj_artists)}")
    
    # Build lookup indices
    apj_by_ja = {}  # normalized Japanese name -> APJ entry
    apj_by_romaji = {}  # normalized romaji -> APJ entry
    
    for a in apj_artists:
        if a.get('name_ja'):
            key = normalize_name(a['name_ja'])
            apj_by_ja[key] = a
        if a.get('name_romaji'):
            key = normalize_name(a['name_romaji'])
            apj_by_romaji[key] = a
    
    # Load existing KANTEISHI profiles
    if not PROFILES_FILE.exists():
        log.error(f"Profiles not found: {PROFILES_FILE}")
        return
    
    profiles = []
    with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                profiles.append(json.loads(line))
    
    log.info(f"KANTEISHI profiles loaded: {len(profiles)}")
    
    # Match and enrich
    matched = 0
    enriched_birth = 0
    enriched_death = 0
    enriched_ja = 0
    
    for p in profiles:
        artist_name = p.get('artist_name', '')
        norm = normalize_name(artist_name)
        
        apj = apj_by_ja.get(norm) or apj_by_romaji.get(norm)
        
        if not apj:
            # Try partial match: remove spaces from artist name
            norm_nospace = re.sub(r'[\s\u3000　]+', '', artist_name)
            norm_nospace_lower = norm_nospace.lower()
            apj = apj_by_ja.get(norm_nospace_lower) or apj_by_romaji.get(norm_nospace_lower)
        
        if apj:
            matched += 1
            p['apj_id'] = apj['apj_id']
            p['apj_url'] = apj['url']
            
            if apj.get('name_ja') and not p.get('name_ja'):
                p['name_ja'] = apj['name_ja']
                enriched_ja += 1
            
            if apj.get('name_romaji') and not p.get('name_romaji'):
                p['name_romaji'] = apj['name_romaji']
            
            if apj.get('birth_year') and not p.get('birth_year'):
                p['birth_year'] = apj['birth_year']
                enriched_birth += 1
            
            if apj.get('death_year') and not p.get('death_year'):
                p['death_year'] = apj['death_year']
                enriched_death += 1
                p['is_deceased'] = True
    
    # Save enriched profiles
    with open(ENRICHED_FILE, 'w', encoding='utf-8') as f:
        for p in profiles:
            f.write(json.dumps(p, ensure_ascii=False) + '\n')
    
    log.info(f"═══ Enrichment Results ═══")
    log.info(f"  Total profiles: {len(profiles)}")
    log.info(f"  DAJ matched: {matched} ({matched/len(profiles)*100:.1f}%)")
    log.info(f"  New birth_year: +{enriched_birth}")
    log.info(f"  New death_year: +{enriched_death}")
    log.info(f"  New name_ja: +{enriched_ja}")
    log.info(f"  Saved to: {ENRICHED_FILE}")


if __name__ == '__main__':
    if '--harvest' in sys.argv:
        harvest_daj()
    elif '--match' in sys.argv:
        match_and_enrich()
    elif '--all' in sys.argv:
        harvest_daj()
        match_and_enrich()
    else:
        print("Usage:")
        print("  python3 apj_enrichment.py --harvest   # Harvest DAJ data")
        print("  python3 apj_enrichment.py --match     # Match & enrich KANTEISHI profiles")
        print("  python3 apj_enrichment.py --all       # Both steps")
