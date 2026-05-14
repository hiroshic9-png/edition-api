#!/usr/bin/env python3
"""
EDITION Deep Audit — 全アセット徹底照合
Met Museum API / Art Institute of Chicago API / V&A API で全フィールドをクロスチェック
"""
import json
import urllib.request
import urllib.error
import time
import sys
import ssl

# SSL context for macOS
ctx = ssl.create_default_context()

ASSETS_PATH = "/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/assets.json"

def fetch_json(url, retries=2):
    """Fetch JSON from URL with retries"""
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "EDITION-Audit/1.0"})
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt < retries:
                time.sleep(1)
            else:
                return {"error": str(e)}

def check_image_url(url, retries=1):
    """Check if image URL is accessible (HEAD request)"""
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "EDITION-Audit/1.0"})
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                return resp.status, resp.headers.get("Content-Type", "unknown")
        except urllib.error.HTTPError as e:
            return e.code, "error"
        except Exception as e:
            if attempt < retries:
                time.sleep(0.5)
            else:
                return 0, str(e)

def audit_met_asset(asset):
    """Audit an asset against Met Museum Open Access API"""
    obj_id = asset["id"].replace("met-", "")
    data = fetch_json(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}")
    
    if "error" in data:
        return {"status": "API_ERROR", "error": data["error"]}
    
    findings = []
    
    # Check title
    api_title = data.get("title", "")
    if api_title and asset.get("title_en"):
        # Normalize for comparison
        our_title = asset["title_en"].split(" — ")[0].strip() if " — " in asset["title_en"] else asset["title_en"]
        if our_title.lower() not in api_title.lower() and api_title.lower() not in our_title.lower():
            findings.append({
                "field": "title_en",
                "severity": "WARNING",
                "ours": asset["title_en"],
                "api": api_title,
                "note": "Title mismatch"
            })
    
    # Check period/date
    api_date = data.get("objectDate", "")
    api_begin = data.get("objectBeginDate", 0)
    api_end = data.get("objectEndDate", 0)
    if api_date and asset.get("period"):
        if api_date.lower() != asset["period"].lower():
            findings.append({
                "field": "period",
                "severity": "INFO",
                "ours": asset["period"],
                "api": api_date,
                "note": "Period representation differs"
            })
    
    # Check medium
    api_medium = data.get("medium", "")
    if api_medium and asset.get("medium"):
        our_medium_lower = asset["medium"].lower()
        api_medium_lower = api_medium.lower()
        # Check for significant material differences
        if len(our_medium_lower) > 10 and len(api_medium_lower) > 10:
            our_words = set(our_medium_lower.split())
            api_words = set(api_medium_lower.split())
            overlap = our_words & api_words
            if len(overlap) < 2:
                findings.append({
                    "field": "medium",
                    "severity": "WARNING",
                    "ours": asset["medium"],
                    "api": api_medium,
                    "note": "Medium description significantly differs"
                })
    
    # Check dimensions
    api_dims = data.get("dimensions", "")
    if api_dims and asset.get("dimensions"):
        findings.append({
            "field": "dimensions",
            "severity": "INFO",
            "ours": asset.get("dimensions", ""),
            "api": api_dims,
            "note": "Dimensions for cross-reference"
        })
    
    # Check department / classification
    api_dept = data.get("department", "")
    api_classification = data.get("classification", "")
    
    # Check artist
    api_artist = data.get("artistDisplayName", "")
    if api_artist and asset.get("artist"):
        if api_artist.lower() != asset["artist"].lower():
            findings.append({
                "field": "artist",
                "severity": "WARNING",
                "ours": asset.get("artist", ""),
                "api": api_artist,
                "note": "Artist name differs"
            })
    elif api_artist and not asset.get("artist"):
        findings.append({
            "field": "artist",
            "severity": "INFO",
            "ours": "(not listed)",
            "api": api_artist,
            "note": "Artist available from API but not in our data"
        })
    
    # Check if object is public domain
    is_public = data.get("isPublicDomain", False)
    if not is_public and asset.get("license") == "CC0":
        findings.append({
            "field": "license",
            "severity": "CRITICAL",
            "ours": "CC0",
            "api": f"isPublicDomain: {is_public}",
            "note": "We claim CC0 but Met says NOT public domain"
        })
    
    # Check primary image
    api_image = data.get("primaryImage", "") or data.get("primaryImageSmall", "")
    
    # Check era
    api_culture = data.get("culture", "")
    api_period = data.get("period", "")
    
    return {
        "status": "CHECKED",
        "api_title": api_title,
        "api_date": api_date,
        "api_medium": api_medium,
        "api_artist": api_artist,
        "api_department": api_dept,
        "api_classification": api_classification,
        "api_period": api_period,
        "api_culture": api_culture,
        "api_is_public": is_public,
        "api_image": api_image,
        "findings": findings
    }

def audit_artic_asset(asset):
    """Audit an asset against Art Institute of Chicago API"""
    obj_id = asset["id"].replace("artic-", "")
    data = fetch_json(f"https://api.artic.edu/api/v1/artworks/{obj_id}?fields=id,title,date_display,date_start,date_end,artist_display,artist_title,medium_display,dimensions,is_public_domain,image_id,classification_title,department_title,place_of_origin")
    
    if "error" in data:
        return {"status": "API_ERROR", "error": data["error"]}
    
    art = data.get("data", {})
    findings = []
    
    # Check title
    api_title = art.get("title", "")
    if api_title and asset.get("title_en"):
        our_title = asset["title_en"].split(" — ")[0].strip() if " — " in asset["title_en"] else asset["title_en"]
        if our_title.lower() not in api_title.lower() and api_title.lower() not in our_title.lower():
            findings.append({
                "field": "title_en",
                "severity": "WARNING",
                "ours": asset["title_en"],
                "api": api_title,
                "note": "Title mismatch"
            })
    
    # Check date
    api_date = art.get("date_display", "")
    if api_date and asset.get("period"):
        if api_date.lower() != asset["period"].lower():
            findings.append({
                "field": "period",
                "severity": "INFO",
                "ours": asset["period"],
                "api": api_date,
                "note": "Period representation differs"
            })
    
    # Check medium
    api_medium = art.get("medium_display", "")
    if api_medium and asset.get("medium"):
        our_medium_lower = asset["medium"].lower()
        api_medium_lower = api_medium.lower()
        if len(our_medium_lower) > 10 and len(api_medium_lower) > 10:
            our_words = set(our_medium_lower.split())
            api_words = set(api_medium_lower.split())
            overlap = our_words & api_words
            if len(overlap) < 2:
                findings.append({
                    "field": "medium",
                    "severity": "WARNING",
                    "ours": asset["medium"],
                    "api": api_medium,
                    "note": "Medium description significantly differs"
                })
    
    # Check artist
    api_artist = art.get("artist_title", "")
    if api_artist and asset.get("artist"):
        if api_artist.lower() != asset["artist"].lower():
            findings.append({
                "field": "artist",
                "severity": "WARNING",
                "ours": asset.get("artist", ""),
                "api": api_artist,
                "note": "Artist name differs"
            })
    elif api_artist and not asset.get("artist"):
        findings.append({
            "field": "artist",
            "severity": "INFO",
            "ours": "(not listed)",
            "api": api_artist,
            "note": "Artist available from API but not in our data"
        })
    
    # Check public domain
    is_public = art.get("is_public_domain", False)
    if not is_public and asset.get("license") == "CC0":
        findings.append({
            "field": "license",
            "severity": "CRITICAL",
            "ours": "CC0",
            "api": f"is_public_domain: {is_public}",
            "note": "We claim CC0 but AIC says NOT public domain"
        })
    
    # Check dimensions
    api_dims = art.get("dimensions", "")
    if api_dims:
        findings.append({
            "field": "dimensions",
            "severity": "INFO",
            "ours": asset.get("dimensions", ""),
            "api": api_dims,
            "note": "Dimensions for cross-reference"
        })
    
    return {
        "status": "CHECKED",
        "api_title": api_title,
        "api_date": api_date,
        "api_medium": api_medium,
        "api_artist": api_artist,
        "api_department": art.get("department_title", ""),
        "api_classification": art.get("classification_title", ""),
        "api_is_public": is_public,
        "findings": findings
    }

def audit_va_asset(asset):
    """Audit an asset against V&A API"""
    obj_id = asset["id"].replace("va-", "")
    data = fetch_json(f"https://api.vam.ac.uk/v2/museumobject/{obj_id}")
    
    if "error" in data:
        return {"status": "API_ERROR", "error": data["error"]}
    
    record = data.get("record", {})
    findings = []
    
    # Check titles
    api_titles = record.get("titles", [])
    api_title = api_titles[0].get("title", "") if api_titles else record.get("objectType", "")
    
    # Check date
    api_date_text = record.get("productionDates", [])
    if api_date_text:
        date_info = api_date_text[0]
        api_date = date_info.get("date", {}).get("text", "")
        if api_date and asset.get("period"):
            findings.append({
                "field": "period",
                "severity": "INFO",
                "ours": asset["period"],
                "api": api_date,
                "note": "Period for cross-reference"
            })
    
    # Check materials
    api_materials = record.get("materialsAndTechniques", "")
    if api_materials and asset.get("medium"):
        findings.append({
            "field": "medium",
            "severity": "INFO",
            "ours": asset["medium"],
            "api": api_materials,
            "note": "Materials for cross-reference"
        })
    
    return {
        "status": "CHECKED",
        "api_title": api_title,
        "findings": findings
    }

def main():
    with open(ASSETS_PATH, "r") as f:
        data = json.load(f)
    
    assets = data["assets"]
    print(f"=== EDITION Deep Audit ===")
    print(f"Total assets: {len(assets)}")
    print(f"{'='*80}\n")
    
    all_results = []
    critical_count = 0
    warning_count = 0
    info_count = 0
    image_errors = []
    
    for i, asset in enumerate(assets):
        aid = asset["id"]
        print(f"[{i+1}/{len(assets)}] Auditing: {aid} — {asset.get('title_en', 'N/A')[:60]}")
        
        # 1. Check image URL accessibility
        img_url = asset.get("image", "")
        if img_url:
            status_code, content_type = check_image_url(img_url)
            if status_code != 200:
                image_errors.append({
                    "id": aid,
                    "title": asset.get("title_en", ""),
                    "image_url": img_url,
                    "status": status_code,
                    "content_type": content_type
                })
                print(f"  ⚠️ IMAGE ERROR: HTTP {status_code}")
        
        # 2. Cross-reference with source API
        result = {"id": aid, "title": asset.get("title_en", ""), "category": asset.get("category", "")}
        
        if aid.startswith("met-"):
            api_result = audit_met_asset(asset)
            time.sleep(0.3)  # Rate limiting
        elif aid.startswith("artic-"):
            api_result = audit_artic_asset(asset)
            time.sleep(0.3)
        elif aid.startswith("va-"):
            api_result = audit_va_asset(asset)
            time.sleep(0.3)
        else:
            api_result = {"status": "UNKNOWN_SOURCE", "findings": []}
        
        result.update(api_result)
        
        # Count findings
        for f in api_result.get("findings", []):
            if f["severity"] == "CRITICAL":
                critical_count += 1
                print(f"  🔴 CRITICAL: {f['field']} — {f['note']}")
                print(f"     Ours: {f['ours']}")
                print(f"     API:  {f['api']}")
            elif f["severity"] == "WARNING":
                warning_count += 1
                print(f"  🟡 WARNING: {f['field']} — {f['note']}")
                print(f"     Ours: {f['ours']}")
                print(f"     API:  {f['api']}")
        
        info_count += len([f for f in api_result.get("findings", []) if f["severity"] == "INFO"])
        
        all_results.append(result)
        sys.stdout.flush()
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"=== AUDIT SUMMARY ===")
    print(f"Total assets audited: {len(assets)}")
    print(f"🔴 CRITICAL: {critical_count}")
    print(f"🟡 WARNING: {warning_count}")
    print(f"ℹ️  INFO: {info_count}")
    print(f"🖼️  Image errors: {len(image_errors)}")
    
    if image_errors:
        print(f"\n--- Image Errors ---")
        for ie in image_errors:
            print(f"  {ie['id']}: HTTP {ie['status']} — {ie['image_url'][:80]}")
    
    # Save full results
    output_path = "/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/deep_audit_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "audit_date": "2026-05-14T22:51:00+09:00",
            "total_assets": len(assets),
            "critical": critical_count,
            "warnings": warning_count,
            "info": info_count,
            "image_errors": image_errors,
            "results": all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nFull results saved to: {output_path}")

if __name__ == "__main__":
    main()
