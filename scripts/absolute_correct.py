#!/usr/bin/env python3
"""
ABSOLUTE CORRECTION — Fix every single discrepancy found by absolute_verify.py
Every field is corrected to match its authoritative source exactly.
"""
import json
import urllib.request
import ssl
import time
import re

ctx = ssl.create_default_context()
ASSETS_PATH = "/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/assets.json"

def fetch_json(url, retries=3):
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "EDITION-Fix/1.0"})
            with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt < retries:
                time.sleep(1.5)
            else:
                return {"_error": str(e)}

def normalize_met_text(s):
    """Strip HTML from Met API text"""
    if not s:
        return ""
    return re.sub(r'<[^>]+>', '', str(s)).strip()

def fix_all():
    with open(ASSETS_PATH) as f:
        data = json.load(f)
    
    assets = data["assets"]
    fixes = []
    
    # ===============================
    # PHASE 1: Fix all Met assets
    # ===============================
    for a in assets:
        if not a["id"].startswith("met-"):
            continue
        
        obj_id = a["id"].replace("met-", "")
        api = fetch_json(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}")
        
        if "_error" in api:
            print(f"  ⚠️ {a['id']}: API error, skipping")
            continue
        
        changed = False
        
        # FIX: Medium — use exact API value
        api_medium = normalize_met_text(api.get("medium", ""))
        if api_medium and api_medium != a.get("medium", ""):
            old = a["medium"]
            a["medium"] = api_medium
            fixes.append(f"MEDIUM: {a['id']} — '{old[:60]}' → '{api_medium[:60]}'")
            changed = True
        
        # FIX: Artist — add from API if missing
        api_artist = normalize_met_text(api.get("artistDisplayName", ""))
        if api_artist:
            if not a.get("artist"):
                a["artist"] = api_artist
                fixes.append(f"ARTIST ADD: {a['id']} — added '{api_artist}'")
                changed = True
            elif a["artist"] != api_artist:
                # Check for encoding differences (e.g. apostrophe types)
                # Only fix if actually different content
                def norm_compare(s):
                    return s.replace("'", "'").replace("'", "'").replace("–", "-").replace("—", "-")
                if norm_compare(a["artist"]) != norm_compare(api_artist):
                    old = a["artist"]
                    a["artist"] = api_artist
                    fixes.append(f"ARTIST FIX: {a['id']} — '{old}' → '{api_artist}'")
                    changed = True
        
        # FIX: Title — use API title but preserve our descriptive subtitle
        api_title = normalize_met_text(api.get("title", ""))
        if api_title:
            our_title = a["title_en"]
            # If we have "API Title — Our Subtitle", keep subtitle
            if " — " in our_title:
                base, subtitle = our_title.split(" — ", 1)
                if base != api_title:
                    new_title = f"{api_title} — {subtitle}"
                    a["title_en"] = new_title
                    fixes.append(f"TITLE: {a['id']} — '{our_title[:50]}' → '{new_title[:50]}'")
                    changed = True
            else:
                if our_title != api_title:
                    a["title_en"] = api_title
                    fixes.append(f"TITLE: {a['id']} — '{our_title[:50]}' → '{api_title[:50]}'")
                    changed = True
        
        # FIX: Period — use exact API value
        api_date = normalize_met_text(api.get("objectDate", ""))
        if api_date and api_date != a.get("period", ""):
            old = a.get("period", "")
            a["period"] = api_date
            fixes.append(f"PERIOD: {a['id']} — '{old}' → '{api_date}'")
            changed = True
        
        # FIX: Dimensions — use exact API value
        api_dims = normalize_met_text(api.get("dimensions", ""))
        if api_dims:
            old = a.get("dimensions", "")
            if old != api_dims:
                a["dimensions"] = api_dims
                fixes.append(f"DIMENSIONS: {a['id']} — updated to API value")
                changed = True
        
        if changed:
            print(f"  ✅ {a['id']}: corrected")
        else:
            print(f"  — {a['id']}: no changes needed")
        
        time.sleep(0.4)
    
    # ===============================
    # PHASE 2: Fix all AIC assets
    # ===============================
    for a in assets:
        if not a["id"].startswith("artic-"):
            continue
        
        obj_id = a["id"].replace("artic-", "")
        api = fetch_json(f"https://api.artic.edu/api/v1/artworks/{obj_id}?fields=id,title,date_display,artist_title,medium_display,dimensions,is_public_domain,image_id")
        
        if "_error" in api:
            print(f"  ⚠️ {a['id']}: API error, skipping")
            continue
        
        art = api.get("data", {})
        changed = False
        
        # FIX: Image ID — update to current API value (AIC changes these)
        api_image_id = art.get("image_id", "")
        if api_image_id:
            current_img = a.get("image", "")
            correct_url = f"https://www.artic.edu/iiif/2/{api_image_id}/full/843,/0/default.jpg"
            if api_image_id not in current_img:
                old = current_img
                a["image"] = correct_url
                fixes.append(f"IMAGE: {a['id']} — image_id updated to '{api_image_id}'")
                changed = True
        
        # FIX: Title
        api_title = art.get("title", "")
        if api_title:
            our_title = a["title_en"]
            our_base = our_title.split(" — ")[0].strip() if " — " in our_title else our_title
            def demacron(s):
                return s.replace("ō","o").replace("Ō","O").replace("ū","u").replace("Ū","U").replace("ē","e").replace("ā","a").replace("ô","o").replace("û","u")
            if demacron(our_base.lower()) != demacron(api_title.lower()):
                if " — " in our_title:
                    _, subtitle = our_title.split(" — ", 1)
                    new_title = f"{api_title} — {subtitle}"
                else:
                    new_title = api_title
                a["title_en"] = new_title
                fixes.append(f"TITLE: {a['id']} — '{our_title[:40]}' → '{new_title[:40]}'")
                changed = True
        
        # FIX: Medium — use exact API value
        api_medium = art.get("medium_display", "")
        if api_medium and api_medium != a.get("medium", ""):
            old = a.get("medium", "")
            a["medium"] = api_medium
            fixes.append(f"MEDIUM: {a['id']} — '{old[:50]}' → '{api_medium[:50]}'")
            changed = True
        
        # FIX: Date
        api_date = art.get("date_display", "")
        if api_date and api_date != a.get("period", ""):
            old = a.get("period", "")
            a["period"] = api_date
            fixes.append(f"PERIOD: {a['id']} — '{old}' → '{api_date}'")
            changed = True
        
        # FIX: Artist
        api_artist = art.get("artist_title", "")
        if api_artist:
            our_artist = a.get("artist", "")
            if not our_artist:
                a["artist"] = api_artist
                fixes.append(f"ARTIST ADD: {a['id']} — added '{api_artist}'")
                changed = True
            elif demacron(our_artist.lower()).replace("attributed to ", "") != demacron(api_artist.lower()):
                # Keep "Attributed to" prefix if we had it
                if "Attributed to" in our_artist and "Attributed to" not in api_artist:
                    a["artist"] = f"Attributed to {api_artist}"
                else:
                    a["artist"] = api_artist
                fixes.append(f"ARTIST FIX: {a['id']} — '{our_artist}' → '{a['artist']}'")
                changed = True
        
        if changed:
            print(f"  ✅ {a['id']}: corrected")
        else:
            print(f"  — {a['id']}: no changes needed")
        
        time.sleep(0.4)
    
    # Save
    data["assets"] = assets
    with open(ASSETS_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"CORRECTION COMPLETE")
    print(f"Total fixes applied: {len(fixes)}")
    for fix in fixes:
        print(f"  {fix}")

if __name__ == "__main__":
    fix_all()
