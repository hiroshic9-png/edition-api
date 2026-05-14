#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════
EDITION Content Audit Pipeline — 品質パトロール
═══════════════════════════════════════════════════════════

Automated audit system that patrols all site content for:
  1. Category misclassification (medium vs category mismatch)
  2. Missing/broken images
  3. Incomplete metadata (empty fields)
  4. Duplicate entries
  5. Source URL validity
  6. Data consistency between assets.json and categories.json

Run modes:
  python audit_pipeline.py              # Full audit
  python audit_pipeline.py --fix        # Audit + auto-fix where possible
  python audit_pipeline.py --json       # Output as JSON (for CI/CD)

Design: Extensible rule engine. Each rule is a function that
returns (severity, message) tuples. New rules can be added
without modifying the core loop.
"""

import json
import sys
import os
import re
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from collections import Counter

# ── Configuration ──
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
ASSETS_FILE = DATA_DIR / "assets.json"
CATEGORIES_FILE = DATA_DIR / "categories.json"
AUDIT_RESULTS_FILE = DATA_DIR / "audit_results.json"

# Severity levels
CRITICAL = "CRITICAL"  # Must fix before deploy
WARNING = "WARNING"    # Should fix soon
INFO = "INFO"          # Suggestion for improvement


# ══════════════════════════════════════════════════════════
# Classification Rules — Medium vs Category mapping
# ══════════════════════════════════════════════════════════

CATEGORY_MEDIUM_RULES = {
    "swords": {
        "expected_keywords": [
            "steel", "iron", "blade", "sword", "katana", "wakizashi",
            "tantō", "tanto", "armor", "lacquer", "shakudō", "shibuichi",
            "helmet", "kabuto", "gusoku", "tsuba",
        ],
        "forbidden_keywords": [
            "hanging scroll", "woodblock print", "ink on paper",
            "album", "book", "embroidery on silk", "stoneware",
            "porcelain", "ivory", "wood carving",
        ],
    },
    "ceramics": {
        "expected_keywords": [
            "stoneware", "porcelain", "earthenware", "ceramic", "glaze",
            "raku", "seto", "oribe", "shino", "karatsu", "bizen",
            "arita", "imari", "kutani", "chawan", "tea bowl",
        ],
        "forbidden_keywords": [
            "steel", "blade", "hanging scroll", "woodblock print",
            "silk", "ivory", "lacquer on wood",
        ],
    },
    "ukiyoe": {
        "expected_keywords": [
            "woodblock print", "nishiki-e", "ink and color on paper",
            "ukiyo-e", "print", "tan-e", "benizuri-e",
        ],
        "forbidden_keywords": [
            "steel", "stoneware", "silk embroidery", "lacquer",
            "ivory", "bronze",
        ],
    },
    "painting": {
        "expected_keywords": [
            "ink", "color on paper", "color on silk", "scroll",
            "screen", "byōbu", "kakemono", "emakimono", "album",
            "painting", "gold leaf",
        ],
        "forbidden_keywords": [
            "steel", "blade", "stoneware", "woodblock print",
        ],
    },
    "lacquerware": {
        "expected_keywords": [
            "lacquer", "maki-e", "urushi", "gold powder", "inrō",
            "suzuribako", "jubako", "nashiji",
        ],
        "forbidden_keywords": [
            "steel", "blade", "stoneware", "woodblock print",
            "silk embroidery",
        ],
    },
    "netsuke": {
        "expected_keywords": [
            "ivory", "wood", "boxwood", "horn", "netsuke",
            "ojime", "stag antler", "bone",
        ],
        "forbidden_keywords": [
            "steel", "blade", "stoneware", "hanging scroll",
            "lacquer",
        ],
    },
    "textiles": {
        "expected_keywords": [
            "silk", "cotton", "embroidery", "woven", "dyed",
            "kimono", "kosode", "bingata", "shibori", "robe",
            "noh costume", "karaori", "nuihaku", "textile",
            "fabric", "thread", "weave",
        ],
        "forbidden_keywords": [
            "steel", "blade", "stoneware", "woodblock-printed book",
            "hanging scroll, mounted as panel; ink",
        ],
    },
    "metalwork": {
        "expected_keywords": [
            "iron", "bronze", "copper", "gold", "silver",
            "shakudō", "shibuichi", "tsuba", "kanzashi",
            "metal", "alloy", "inlay",
        ],
        "forbidden_keywords": [
            "hanging scroll", "woodblock print", "stoneware",
            "silk embroidery",
        ],
    },
    "sculpture": {
        "expected_keywords": [
            "wood", "cypress", "hinoki", "bronze", "gilt",
            "lacquer", "sculpture", "figure", "statue",
            "buddha", "bodhisattva", "carved",
        ],
        "forbidden_keywords": [
            "steel blade", "stoneware", "woodblock print",
        ],
    },
    "bonsai": {
        "expected_keywords": [
            "bonsai", "tree", "pine", "maple", "pot", "container",
            "stone", "suiseki",
        ],
        "forbidden_keywords": [],
    },
    "architecture": {
        "expected_keywords": [
            "wood", "timber", "screen", "panel", "fusuma", "ranma",
            "shoji", "tansu", "chest", "architectural",
        ],
        "forbidden_keywords": [],
    },
    "contemporary": {
        "expected_keywords": [],  # Contemporary is broad
        "forbidden_keywords": [],
    },
}


# ══════════════════════════════════════════════════════════
# Audit Rules
# ══════════════════════════════════════════════════════════

class AuditResult:
    def __init__(self, severity: str, rule: str, item_id: str, 
                 category: str, message: str, auto_fixable: bool = False):
        self.severity = severity
        self.rule = rule
        self.item_id = item_id
        self.category = category
        self.message = message
        self.auto_fixable = auto_fixable
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "severity": self.severity,
            "rule": self.rule,
            "item_id": self.item_id,
            "category": self.category,
            "message": self.message,
            "auto_fixable": self.auto_fixable,
            "timestamp": self.timestamp,
        }

    def __str__(self):
        icon = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "🔵"}[self.severity]
        return f"  {icon} [{self.severity}] {self.rule}: [{self.category}] {self.item_id} — {self.message}"


def rule_category_mismatch(assets: List[Dict]) -> List[AuditResult]:
    """Check if asset medium matches its assigned category."""
    results = []
    for asset in assets:
        cat = asset.get("category", "")
        medium = asset.get("medium", "").lower()
        rules = CATEGORY_MEDIUM_RULES.get(cat, {})

        # Check forbidden keywords
        for keyword in rules.get("forbidden_keywords", []):
            if keyword.lower() in medium:
                results.append(AuditResult(
                    CRITICAL,
                    "CATEGORY_MISMATCH",
                    asset.get("id", "?"),
                    cat,
                    f"Medium '{asset.get('medium', '')}' contains forbidden keyword '{keyword}' for category '{cat}'",
                ))
                break

        # Check if at least one expected keyword matches
        expected = rules.get("expected_keywords", [])
        if expected and not any(kw.lower() in medium for kw in expected):
            results.append(AuditResult(
                WARNING,
                "WEAK_CATEGORY_MATCH",
                asset.get("id", "?"),
                cat,
                f"Medium '{asset.get('medium', '')}' has no expected keywords for category '{cat}'",
            ))

    return results


def rule_missing_image(assets: List[Dict]) -> List[AuditResult]:
    """Check for missing or empty image URLs."""
    results = []
    for asset in assets:
        img = asset.get("image", "")
        if not img or img.strip() == "":
            results.append(AuditResult(
                CRITICAL,
                "MISSING_IMAGE",
                asset.get("id", "?"),
                asset.get("category", "?"),
                "Image URL is empty",
            ))
    return results


def rule_incomplete_metadata(assets: List[Dict]) -> List[AuditResult]:
    """Check for assets with incomplete metadata."""
    required_fields = ["id", "category", "title_en", "medium", "image", "source_url"]
    recommended_fields = ["description", "significance", "period", "era"]
    results = []

    for asset in assets:
        # Required fields
        for field in required_fields:
            val = asset.get(field, "")
            if not val or str(val).strip() == "":
                results.append(AuditResult(
                    WARNING,
                    "MISSING_REQUIRED_FIELD",
                    asset.get("id", "?"),
                    asset.get("category", "?"),
                    f"Required field '{field}' is missing or empty",
                ))

        # Recommended fields — only INFO
        missing_recommended = [f for f in recommended_fields 
                                if not asset.get(f, "").strip()]
        if len(missing_recommended) >= 3:
            results.append(AuditResult(
                INFO,
                "SPARSE_METADATA",
                asset.get("id", "?"),
                asset.get("category", "?"),
                f"Missing {len(missing_recommended)} recommended fields: {', '.join(missing_recommended)}",
            ))

    return results


def rule_duplicate_ids(assets: List[Dict]) -> List[AuditResult]:
    """Check for duplicate asset IDs."""
    results = []
    ids = [a.get("id", "") for a in assets]
    dupes = [id for id, count in Counter(ids).items() if count > 1]
    for dupe in dupes:
        results.append(AuditResult(
            CRITICAL,
            "DUPLICATE_ID",
            dupe,
            "multiple",
            f"Asset ID '{dupe}' appears multiple times",
        ))
    return results


def rule_category_coverage(assets: List[Dict], categories: List[Dict]) -> List[AuditResult]:
    """Check that all categories have sufficient assets."""
    results = []
    cat_slugs = {c["slug"] for c in categories}
    asset_cats = Counter(a.get("category", "") for a in assets)

    for slug in cat_slugs:
        count = asset_cats.get(slug, 0)
        if count == 0:
            results.append(AuditResult(
                CRITICAL,
                "EMPTY_CATEGORY",
                slug,
                slug,
                f"Category '{slug}' has no assets",
            ))
        elif count < 2:
            results.append(AuditResult(
                WARNING,
                "LOW_ASSET_COUNT",
                slug,
                slug,
                f"Category '{slug}' has only {count} asset(s) — recommend minimum 3",
            ))

    # Check for assets in non-existent categories
    for cat in asset_cats:
        if cat not in cat_slugs:
            results.append(AuditResult(
                CRITICAL,
                "ORPHAN_CATEGORY",
                cat,
                cat,
                f"Assets reference category '{cat}' which doesn't exist in categories.json",
            ))

    return results


def rule_category_article_depth(categories: List[Dict]) -> List[AuditResult]:
    """Check that category articles have sufficient depth."""
    results = []
    for cat in categories:
        article = cat.get("article", {})
        sections = article.get("sections", [])
        if len(sections) < 3:
            results.append(AuditResult(
                INFO,
                "SHALLOW_ARTICLE",
                cat["slug"],
                cat["slug"],
                f"Category article has only {len(sections)} section(s) — recommend 3-5 for authority",
            ))
        # Check section body length
        for section in sections:
            body = section.get("body", "")
            if len(body) < 200:
                results.append(AuditResult(
                    INFO,
                    "SHORT_SECTION",
                    cat["slug"],
                    cat["slug"],
                    f"Section '{section.get('title', '?')}' is only {len(body)} chars — recommend 300+",
                ))
    return results


def rule_html_in_json(assets: List[Dict]) -> List[AuditResult]:
    """Check for raw HTML tags in JSON data (indicates dirty data)."""
    results = []
    html_pattern = re.compile(r'<[^>]+>')
    for asset in assets:
        for key in ["title_en", "title_jp", "medium", "description", "significance"]:
            val = asset.get(key, "")
            if html_pattern.search(val):
                results.append(AuditResult(
                    WARNING,
                    "HTML_IN_DATA",
                    asset.get("id", "?"),
                    asset.get("category", "?"),
                    f"Field '{key}' contains HTML tags: {html_pattern.findall(val)[:3]}",
                    auto_fixable=True,
                ))
    return results


def rule_image_url_check(assets: List[Dict], check_http: bool = False) -> List[AuditResult]:
    """Validate image URL format and optionally check HTTP status."""
    results = []
    for asset in assets:
        img = asset.get("image", "")
        if not img:
            continue
        
        # Skip relative paths (local images served from site)
        if img.startswith("/"):
            continue

        if not img.startswith("https://"):
            results.append(AuditResult(
                WARNING,
                "INSECURE_IMAGE_URL",
                asset.get("id", "?"),
                asset.get("category", "?"),
                f"Image URL uses HTTP instead of HTTPS",
            ))

        if check_http:
            try:
                req = urllib.request.Request(img, method="HEAD")
                req.add_header("User-Agent", "EDITION-Audit/1.0")
                resp = urllib.request.urlopen(req, timeout=5)
                if resp.status != 200:
                    results.append(AuditResult(
                        CRITICAL,
                        "BROKEN_IMAGE_URL",
                        asset.get("id", "?"),
                        asset.get("category", "?"),
                        f"Image URL returned HTTP {resp.status}",
                    ))
            except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
                results.append(AuditResult(
                    CRITICAL,
                    "BROKEN_IMAGE_URL",
                    asset.get("id", "?"),
                    asset.get("category", "?"),
                    f"Image URL check failed: {str(e)[:80]}",
                ))
    return results


def rule_price_db_consistency(check_prices: bool = True) -> List[AuditResult]:
    """Check price_intelligence.json for consistency issues."""
    results = []
    price_file = DATA_DIR / "price_intelligence.json"
    if not price_file.exists():
        results.append(AuditResult(
            WARNING, "NO_PRICE_DATA", "price_db", "system",
            "price_intelligence.json not found — run export_prices.py",
        ))
        return results

    with open(price_file) as f:
        pd = json.load(f)

    valid_cats = {
        "swords", "ceramics", "ukiyoe", "painting", "lacquerware",
        "netsuke", "textiles", "metalwork", "sculpture", "bonsai",
        "architecture", "contemporary",
    }
    valid_currencies = {"JPY", "GBP", "USD", "EUR", "CHF", "HKD", "CNY"}

    for r in pd.get("results", []):
        rid = r.get("id", "?")
        cat = r.get("asset_category", "")
        # Category validation
        if cat not in valid_cats:
            results.append(AuditResult(
                CRITICAL, "INVALID_PRICE_CATEGORY", rid, cat,
                f"Price record uses unknown category '{cat}'",
            ))
        # Currency validation
        cur = r.get("currency", "")
        if cur not in valid_currencies:
            results.append(AuditResult(
                WARNING, "INVALID_CURRENCY", rid, cat,
                f"Price record uses unknown currency '{cur}'",
            ))
        # USD sanity check
        usd = r.get("usd_equivalent", 0)
        hammer = r.get("hammer_price", 0)
        if usd and hammer:
            ratio = usd / hammer if hammer > 0 else 0
            # JPY: ~0.007, GBP: ~1.25, USD: ~1.0
            if cur == "USD" and abs(ratio - 1.0) > 0.5:
                results.append(AuditResult(
                    WARNING, "USD_CONVERSION_ANOMALY", rid, cat,
                    f"USD record: hammer={hammer}, usd_equiv={usd}, ratio={ratio:.2f} (expected ~1.0)",
                ))
            elif cur == "JPY" and (ratio > 0.02 or ratio < 0.003):
                results.append(AuditResult(
                    WARNING, "USD_CONVERSION_ANOMALY", rid, cat,
                    f"JPY record: hammer={hammer}, usd_equiv={usd}, ratio={ratio:.4f} (expected ~0.007)",
                ))
        # Missing title
        if not r.get("title", "").strip():
            results.append(AuditResult(
                WARNING, "MISSING_PRICE_TITLE", rid, cat,
                "Price record has no title",
            ))

    return results


# ══════════════════════════════════════════════════════════
# Pipeline Runner
# ══════════════════════════════════════════════════════════

def run_audit(check_images: bool = False) -> List[AuditResult]:
    """Run the full audit pipeline."""
    # Load data
    with open(ASSETS_FILE) as f:
        assets_data = json.load(f)
    assets = assets_data.get("assets", [])

    with open(CATEGORIES_FILE) as f:
        categories_data = json.load(f)
    categories = categories_data.get("categories", [])

    # Run all rules
    results = []
    results.extend(rule_category_mismatch(assets))
    results.extend(rule_missing_image(assets))
    results.extend(rule_incomplete_metadata(assets))
    results.extend(rule_duplicate_ids(assets))
    results.extend(rule_category_coverage(assets, categories))
    results.extend(rule_category_article_depth(categories))
    results.extend(rule_html_in_json(assets))
    results.extend(rule_price_db_consistency())
    if check_images:
        results.extend(rule_image_url_check(assets, check_http=True))
    else:
        results.extend(rule_image_url_check(assets, check_http=False))

    return results


def print_report(results: List[AuditResult]):
    """Print a formatted audit report."""
    print("═" * 65)
    print("  EDITION Content Audit Report")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 65)

    # Sort by severity
    severity_order = {CRITICAL: 0, WARNING: 1, INFO: 2}
    results.sort(key=lambda r: severity_order.get(r.severity, 99))

    counts = Counter(r.severity for r in results)
    print(f"\n  Summary: 🔴 {counts.get(CRITICAL, 0)} Critical | "
          f"🟡 {counts.get(WARNING, 0)} Warning | "
          f"🔵 {counts.get(INFO, 0)} Info\n")

    if not results:
        print("  ✅ All checks passed — no issues found.\n")
        return

    # Group by rule
    current_rule = None
    for r in results:
        if r.rule != current_rule:
            current_rule = r.rule
            print(f"\n  ── {current_rule} ──")
        print(r)

    # Verdict
    print("\n" + "─" * 65)
    if counts.get(CRITICAL, 0) > 0:
        print("  ❌ AUDIT FAILED — Critical issues must be resolved before deploy")
    elif counts.get(WARNING, 0) > 0:
        print("  ⚠️  AUDIT PASSED WITH WARNINGS — Review recommended")
    else:
        print("  ✅ AUDIT PASSED — Only informational items")
    print("─" * 65)


def save_results(results: List[AuditResult]):
    """Save audit results to JSON."""
    output = {
        "audit_timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(results),
            "critical": sum(1 for r in results if r.severity == CRITICAL),
            "warning": sum(1 for r in results if r.severity == WARNING),
            "info": sum(1 for r in results if r.severity == INFO),
        },
        "results": [r.to_dict() for r in results],
    }
    with open(AUDIT_RESULTS_FILE, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved to: {AUDIT_RESULTS_FILE}")


# ══════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    check_images = "--images" in sys.argv
    output_json = "--json" in sys.argv

    results = run_audit(check_images=check_images)

    if output_json:
        save_results(results)
    else:
        print_report(results)
        save_results(results)
