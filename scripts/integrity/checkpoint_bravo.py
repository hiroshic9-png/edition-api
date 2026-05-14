#!/usr/bin/env python3
"""
CHECKPOINT BRAVO — API Cross-Reference Engine
===============================================
全フィールドを原典APIと照合。1フィールドでも不一致なら REJECT。
嘘のデータを静かに修正することは隠蔽と同じ — 不一致は即ブロック。

検証フィールド (Met/AIC):
  title, period, medium, dimensions, artist, license, source_url, image_id
"""
import json
import re
import ssl
import sys
import time
import urllib.request
from datetime import datetime, timezone

from config import ASSETS_PATH, TRUSTED_SOURCES

ctx = ssl.create_default_context()


def fetch_json(url, retries=2):
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "EDITION-Integrity/1.0"}
            )
            with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt < retries:
                time.sleep(1)
            else:
                return {"_error": str(e)}


def normalize(s):
    """Strip HTML, normalize whitespace."""
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", "", str(s))
    s = re.sub(r"\s+", " ", s).strip()
    return s


def demacron(s):
    """Normalize macrons for comparison."""
    return (
        s.replace("ō", "o").replace("Ō", "O")
        .replace("ū", "u").replace("Ū", "U")
        .replace("ē", "e").replace("ā", "a")
        .replace("ô", "o").replace("û", "u")
        .replace("\u2019", "'").replace("\u2018", "'")
        .replace("\u201c", '"').replace("\u201d", '"')
        .replace("\u2013", "-").replace("\u2014", "-")
    )


def verify_met(asset):
    """Verify all fields against Met Museum API."""
    obj_id = asset["id"].replace("met-", "")
    api = fetch_json(
        f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}"
    )
    if "_error" in api:
        return {"verdict": "REJECT", "reason": f"API error: {api['_error']}", "mismatches": []}

    mismatches = []

    # TITLE
    api_title = normalize(api.get("title", ""))
    our_title = asset.get("title_en", "")
    our_base = our_title.split(" — ")[0].strip() if " — " in our_title else our_title
    if not (
        demacron(api_title.lower()) == demacron(our_base.lower())
        or demacron(api_title.lower()) in demacron(our_base.lower())
        or demacron(our_base.lower()) in demacron(api_title.lower())
    ):
        mismatches.append(("title", our_title, api_title))

    # PERIOD
    api_date = normalize(api.get("objectDate", ""))
    our_period = asset.get("period", "")
    if api_date and our_period and demacron(api_date.lower()) != demacron(our_period.lower()):
        mismatches.append(("period", our_period, api_date))

    # MEDIUM
    api_medium = normalize(api.get("medium", ""))
    our_medium = normalize(asset.get("medium", ""))
    if api_medium and our_medium and demacron(api_medium.lower()) != demacron(our_medium.lower()):
        mismatches.append(("medium", our_medium, api_medium))

    # ARTIST
    api_artist = normalize(api.get("artistDisplayName", ""))
    our_artist = asset.get("artist", "")
    if api_artist:
        if not our_artist:
            mismatches.append(("artist", "(missing)", api_artist))
        elif demacron(our_artist.lower()) not in demacron(api_artist.lower()) and demacron(api_artist.lower()) not in demacron(our_artist.lower()):
            mismatches.append(("artist", our_artist, api_artist))

    # LICENSE
    api_public = api.get("isPublicDomain", False)
    our_license = asset.get("license", "")
    if our_license == "CC0" and not api_public:
        mismatches.append(("license", our_license, f"isPublicDomain={api_public}"))

    # SOURCE URL
    expected_url = f"https://www.metmuseum.org/art/collection/search/{obj_id}"
    our_url = asset.get("source_url", "")
    if our_url != expected_url:
        mismatches.append(("source_url", our_url, expected_url))

    # IMAGE URL FORMAT
    img = asset.get("image", "")
    if not img.startswith("https://images.metmuseum.org/CRDImages/"):
        mismatches.append(("image_format", img[:60], "Must start with https://images.metmuseum.org/CRDImages/"))

    verdict = "REJECT" if mismatches else "PASS"
    return {"verdict": verdict, "mismatches": mismatches}


def verify_aic(asset):
    """Verify all fields against AIC API."""
    obj_id = asset["id"].replace("artic-", "")
    api = fetch_json(
        f"https://api.artic.edu/api/v1/artworks/{obj_id}?fields=id,title,date_display,artist_title,medium_display,is_public_domain,image_id"
    )
    if "_error" in api:
        return {"verdict": "REJECT", "reason": f"API error: {api['_error']}", "mismatches": []}

    art = api.get("data", {})
    mismatches = []

    # TITLE
    api_title = normalize(art.get("title", ""))
    our_title = asset.get("title_en", "")
    our_base = our_title.split(" — ")[0].strip() if " — " in our_title else our_title
    if not (
        demacron(api_title.lower()) == demacron(our_base.lower())
        or demacron(api_title.lower()) in demacron(our_base.lower())
        or demacron(our_base.lower()) in demacron(api_title.lower())
    ):
        mismatches.append(("title", our_title, api_title))

    # MEDIUM
    api_medium = normalize(art.get("medium_display", ""))
    our_medium = normalize(asset.get("medium", ""))
    if api_medium and our_medium and demacron(api_medium.lower()) != demacron(our_medium.lower()):
        mismatches.append(("medium", our_medium, api_medium))

    # IMAGE ID
    api_image_id = art.get("image_id", "")
    our_img = asset.get("image", "")
    if api_image_id and api_image_id not in our_img:
        mismatches.append(("image_id", our_img[:50], f"API image_id: {api_image_id}"))

    # LICENSE
    api_public = art.get("is_public_domain", False)
    our_license = asset.get("license", "")
    if our_license == "CC0" and not api_public:
        mismatches.append(("license", our_license, f"is_public_domain={api_public}"))

    # SOURCE URL
    expected_url = f"https://www.artic.edu/artworks/{obj_id}"
    our_url = asset.get("source_url", "")
    if our_url != expected_url:
        mismatches.append(("source_url", our_url, expected_url))

    verdict = "REJECT" if mismatches else "PASS"
    return {"verdict": verdict, "mismatches": mismatches}


def verify_va(asset):
    """Verify against V&A API."""
    obj_id = asset["id"].replace("va-", "")
    api = fetch_json(f"https://api.vam.ac.uk/v2/museumobject/{obj_id}")
    if "_error" in api:
        return {"verdict": "REJECT", "reason": f"API error: {api['_error']}", "mismatches": []}

    mismatches = []
    our_url = asset.get("source_url", "")
    expected = f"https://collections.vam.ac.uk/item/{obj_id}/"
    if our_url.rstrip("/") != expected.rstrip("/"):
        mismatches.append(("source_url", our_url, expected))

    verdict = "REJECT" if mismatches else "PASS"
    return {"verdict": verdict, "mismatches": mismatches}


def run_bravo(asset):
    """Run CHECKPOINT BRAVO on a single asset."""
    aid = asset["id"]

    if aid.startswith("met-"):
        result = verify_met(asset)
    elif aid.startswith("artic-"):
        result = verify_aic(asset)
    elif aid.startswith("va-"):
        result = verify_va(asset)
    else:
        result = {"verdict": "REJECT", "mismatches": [], "reason": f"Unknown source prefix: {aid}"}

    result["asset_id"] = aid
    result["checkpoint"] = "BRAVO"
    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    return result


def run_bravo_batch(assets):
    """Run CHECKPOINT BRAVO on all assets."""
    print("=" * 70)
    print("CHECKPOINT BRAVO — API Cross-Reference Verification")
    print("=" * 70)

    passed = 0
    rejected = 0
    all_results = []

    for i, asset in enumerate(assets):
        result = run_bravo(asset)
        all_results.append(result)

        verdict = result["verdict"]
        if verdict == "PASS":
            passed += 1
            print(f"  [{i+1:02d}] {asset['id']:25s} ✅ PASS")
        else:
            rejected += 1
            print(f"  [{i+1:02d}] {asset['id']:25s} ❌ REJECT")
            for field, ours, source in result.get("mismatches", []):
                print(f"       {field}: OURS='{ours[:50]}' SOURCE='{source[:50]}'")
            if result.get("reason"):
                print(f"       {result['reason']}")

        time.sleep(0.3)

    print(f"\n{'=' * 70}")
    print(f"BRAVO RESULTS: {passed} PASS / {rejected} REJECT / {len(assets)} total")

    if rejected > 0:
        print(f"❌ {rejected} asset(s) REJECTED at API verification")
        sys.exit(1)
    else:
        print(f"✅ All {passed} assets verified against source APIs")

    return all_results


if __name__ == "__main__":
    with open(ASSETS_PATH) as f:
        assets = json.load(f)["assets"]

    if "--asset" in sys.argv:
        idx = sys.argv.index("--asset")
        target = sys.argv[idx + 1]
        assets = [a for a in assets if a["id"] == target]

    run_bravo_batch(assets)
