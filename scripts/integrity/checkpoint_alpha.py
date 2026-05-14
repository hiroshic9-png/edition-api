#!/usr/bin/env python3
"""
CHECKPOINT ALPHA — Source Authentication Gate
==============================================
入口ゲート。全ての情報は、ここを通過しなければシステムに入れない。

検証項目:
  1. ソースが TRUSTED_SOURCES ホワイトリストに含まれるか
  2. ソースAPI がオブジェクトの存在を確認できるか
  3. ライセンスが確認できるか
  4. 画像URLが禁止パターンに該当しないか
  5. ソースURLが禁止パターンに該当しないか

1つでも不合格 → REJECT. 例外なし。
"""
import json
import re
import ssl
import sys
import time
import urllib.request
from datetime import datetime, timezone

from config import (
    TRUSTED_SOURCES,
    FORBIDDEN_IMAGE_PATTERNS,
    FORBIDDEN_SOURCE_PATTERNS,
    QUARANTINE_DIR,
    KNOWLEDGE_PATH,
)

ctx = ssl.create_default_context()


def fetch_json(url, retries=2):
    """Fetch JSON from URL with retries."""
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


def identify_source(asset):
    """Identify which trusted source this asset belongs to."""
    asset_id = asset.get("id", "")
    source_url = asset.get("source_url", "")

    for tier_name, tier_sources in TRUSTED_SOURCES.items():
        if tier_name.startswith("tier_"):
            for key, src in tier_sources.items():
                if isinstance(src, dict) and "id_prefix" in src:
                    if asset_id.startswith(src["id_prefix"]):
                        return tier_name, key, src
                elif isinstance(src, dict) and "domain" in src:
                    if src["domain"] in source_url:
                        return tier_name, key, src

    return None, None, None


def verify_source_exists(asset, source_key, source_config):
    """Verify the object actually exists in the source API."""
    asset_id = asset["id"]
    prefix = source_config.get("id_prefix", "")
    obj_id = asset_id.replace(prefix, "")

    if source_key == "met":
        api = fetch_json(
            f"{source_config['api_base']}/objects/{obj_id}"
        )
        if "_error" in api:
            return False, f"Met API error: {api['_error']}"
        if not api.get("objectID"):
            return False, "Object does not exist in Met API"
        return True, "Object confirmed in Met API"

    elif source_key == "aic":
        api = fetch_json(
            f"{source_config['api_base']}/artworks/{obj_id}?fields=id,title,is_public_domain,image_id"
        )
        if "_error" in api:
            return False, f"AIC API error: {api['_error']}"
        data = api.get("data", {})
        if not data.get("id"):
            return False, "Object does not exist in AIC API"
        return True, "Object confirmed in AIC API"

    elif source_key == "va":
        api = fetch_json(
            f"{source_config['api_base']}/museumobject/{obj_id}"
        )
        if "_error" in api:
            return False, f"V&A API error: {api['_error']}"
        if not api.get("record"):
            return False, "Object does not exist in V&A API"
        return True, "Object confirmed in V&A API"

    return False, f"No verification method for source: {source_key}"


def check_forbidden_patterns(asset):
    """Check for forbidden image and source URL patterns."""
    issues = []
    image = asset.get("image", "").lower()
    source_url = asset.get("source_url", "").lower()

    for pattern in FORBIDDEN_IMAGE_PATTERNS:
        if pattern in image:
            issues.append(f"Forbidden image pattern: '{pattern}'")

    for pattern in FORBIDDEN_SOURCE_PATTERNS:
        if pattern in source_url:
            issues.append(f"Forbidden source pattern: '{pattern}'")

    return issues


def verify_license(asset, source_key, source_config):
    """Verify license is consistent with source."""
    our_license = asset.get("license", "")
    expected = source_config.get("our_license", "")

    if expected and our_license != expected:
        return False, f"License mismatch: ours='{our_license}', expected='{expected}'"
    return True, "License consistent"


def run_alpha(asset):
    """
    Run CHECKPOINT ALPHA on a single asset.
    Returns (verdict, details) where verdict is PASS/REJECT.
    """
    results = {
        "asset_id": asset["id"],
        "checkpoint": "ALPHA",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": [],
        "verdict": "PASS",
    }

    # CHECK 1: Source identification
    tier, source_key, source_config = identify_source(asset)
    if not tier:
        results["checks"].append({
            "check": "source_identification",
            "result": "REJECT",
            "reason": f"Source not in TRUSTED_SOURCES whitelist. ID: {asset['id']}, URL: {asset.get('source_url', '')}",
        })
        results["verdict"] = "REJECT"
        return results

    results["checks"].append({
        "check": "source_identification",
        "result": "PASS",
        "reason": f"Source: {source_key} ({tier})",
    })

    # CHECK 2: Forbidden patterns
    forbidden = check_forbidden_patterns(asset)
    if forbidden:
        for issue in forbidden:
            results["checks"].append({
                "check": "forbidden_patterns",
                "result": "REJECT",
                "reason": issue,
            })
        results["verdict"] = "REJECT"
        return results

    results["checks"].append({
        "check": "forbidden_patterns",
        "result": "PASS",
        "reason": "No forbidden patterns detected",
    })

    # CHECK 3: Source API existence (Tier 1 only)
    if tier == "tier_1" and "api_base" in source_config:
        exists, msg = verify_source_exists(asset, source_key, source_config)
        if not exists:
            results["checks"].append({
                "check": "source_exists",
                "result": "REJECT",
                "reason": msg,
            })
            results["verdict"] = "REJECT"
            return results

        results["checks"].append({
            "check": "source_exists",
            "result": "PASS",
            "reason": msg,
        })

    # CHECK 4: License verification
    if "our_license" in source_config:
        lic_ok, lic_msg = verify_license(asset, source_key, source_config)
        if not lic_ok:
            results["checks"].append({
                "check": "license",
                "result": "REJECT",
                "reason": lic_msg,
            })
            results["verdict"] = "REJECT"
            return results

        results["checks"].append({
            "check": "license",
            "result": "PASS",
            "reason": lic_msg,
        })

    return results


def run_alpha_batch(assets):
    """Run CHECKPOINT ALPHA on all assets."""
    print("=" * 70)
    print("CHECKPOINT ALPHA — Source Authentication Gate")
    print("=" * 70)

    passed = 0
    rejected = 0
    all_results = []

    for i, asset in enumerate(assets):
        result = run_alpha(asset)
        all_results.append(result)

        verdict = result["verdict"]
        if verdict == "PASS":
            passed += 1
            print(f"  [{i+1:02d}] {asset['id']:25s} ✅ PASS")
        else:
            rejected += 1
            print(f"  [{i+1:02d}] {asset['id']:25s} ❌ REJECT")
            for check in result["checks"]:
                if check["result"] == "REJECT":
                    print(f"       → {check['reason']}")

        time.sleep(0.3)

    print(f"\n{'=' * 70}")
    print(f"ALPHA RESULTS: {passed} PASS / {rejected} REJECT / {len(assets)} total")

    if rejected > 0:
        print(f"❌ {rejected} asset(s) REJECTED at source authentication")
        sys.exit(1)
    else:
        print(f"✅ All {passed} assets passed source authentication")

    return all_results


if __name__ == "__main__":
    from config import ASSETS_PATH

    with open(ASSETS_PATH) as f:
        assets = json.load(f)["assets"]

    run_alpha_batch(assets)
