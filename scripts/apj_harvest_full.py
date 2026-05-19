#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════
EDITION — Art Platform Japan Full Harvest (Playwright)
═══════════════════════════════════════════════════════════

Uses Playwright to fully render the DAJ page and extract
all 5,200+ artist entries via browser automation.

Run during off-peak hours (scheduled via launchd).

Prereqs on Mac Mini:
  pip install playwright
  playwright install chromium
"""

import json
import re
import sys
import logging
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("/Users/hiroshi/edition-collab/kanteishi/data")
OUTPUT_FILE = DATA_DIR / "apj_artists_full.jsonl"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
log = logging.getLogger(__name__)


def harvest_full():
    """Use Playwright to harvest all 5,200+ DAJ artists."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.error("Playwright not installed. Run: pip install playwright && playwright install chromium")
        return
    
    log.info("═══ Full DAJ Harvest via Playwright ═══")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        log.info("Loading https://artplatform.go.jp/artists ...")
        page.goto("https://artplatform.go.jp/artists", wait_until="networkidle", timeout=60000)
        
        # Wait for content to render
        page.wait_for_selector('a[href*="/artists/A"]', timeout=30000)
        
        # Scroll to bottom to trigger lazy loading
        log.info("Scrolling to load all sections...")
        prev_count = 0
        max_scrolls = 50
        for i in range(max_scrolls):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)
            
            current_count = page.evaluate("""
                () => document.querySelectorAll('a[href*="/artists/A"]').length
            """)
            
            log.info(f"  Scroll {i+1}: {current_count} artist links found")
            
            if current_count == prev_count and current_count > 0:
                break
            prev_count = current_count
        
        # Extract all artist entries
        log.info("Extracting artist data...")
        artists_raw = page.evaluate("""
            () => {
                const links = document.querySelectorAll('a[href*="/artists/A"]');
                return Array.from(links).map(a => ({
                    href: a.href,
                    text: a.textContent.trim()
                }));
            }
        """)
        
        browser.close()
    
    log.info(f"Raw entries: {len(artists_raw)}")
    
    # Parse entries
    artists = []
    pattern = re.compile(
        r'(.+?)'  # Japanese name
        r'([A-ZĀĪŪĒŌÜ][A-Za-zāīūēōüʼ\' ,.\-\(\)]+)'  # Romaji
        r'(?:(\d{4})(?:[–\-](\d{4})?)?)?'  # Years
        r'\s*(?:APJ\s+)?(A\d+)?'  # APJ ID
    )
    
    for entry in artists_raw:
        text = entry['text']
        url = entry['href']
        
        # Extract APJ ID from URL
        id_match = re.search(r'/artists/(A\d+)', url)
        if not id_match:
            continue
        apj_id = id_match.group(1)
        
        # Parse text
        m = pattern.match(text)
        if m:
            artists.append({
                'name_ja': m.group(1).strip(),
                'name_romaji': m.group(2).strip() if m.group(2) else None,
                'birth_year': int(m.group(3)) if m.group(3) else None,
                'death_year': int(m.group(4)) if m.group(4) else None,
                'apj_id': apj_id,
                'url': url,
                'source': 'apj_daj'
            })
        else:
            artists.append({
                'name_ja': text,
                'name_romaji': None,
                'birth_year': None,
                'death_year': None,
                'apj_id': apj_id,
                'url': url,
                'source': 'apj_daj'
            })
    
    # Deduplicate
    seen = set()
    unique = []
    for a in artists:
        if a['apj_id'] not in seen:
            seen.add(a['apj_id'])
            unique.append(a)
    
    log.info(f"Unique artists: {len(unique)}")
    
    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for a in unique:
            f.write(json.dumps(a, ensure_ascii=False) + '\n')
    
    log.info(f"Saved to {OUTPUT_FILE}")
    log.info(f"Timestamp: {datetime.utcnow().isoformat()}Z")


if __name__ == '__main__':
    harvest_full()
