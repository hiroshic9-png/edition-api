#!/usr/bin/env python3
"""
LEARNING LOOP — Verification Knowledge Accumulator
=====================================================
検証結果を蓄積し、検出パターンを強化する学習機械。
過去の失敗から学び、同じ問題の再発を防ぐ。

記録するもの:
  - 発見した問題パターン（APIのimage_id変更、HTML tag混入等）
  - 問題の発生頻度
  - 検証の精度メトリクス
"""
import json
import os
from datetime import datetime, timezone

from config import KNOWLEDGE_PATH, AUDIT_LOG_DIR


def load_knowledge():
    """Load the knowledge base."""
    if os.path.exists(KNOWLEDGE_PATH):
        with open(KNOWLEDGE_PATH) as f:
            return json.load(f)
    return {
        "version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "known_patterns": [],
        "metrics": {
            "total_verifications": 0,
            "total_rejections": 0,
            "total_corrections": 0,
            "false_positive_rate": 0.0,
        },
        "lessons_learned": [],
    }


def save_knowledge(kb):
    """Save the knowledge base."""
    kb["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(KNOWLEDGE_PATH, "w") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)


def add_pattern(pattern_id, description, detection, action, source_id=None):
    """Register a new known pattern."""
    kb = load_knowledge()

    # Check if pattern already exists
    existing = [p for p in kb["known_patterns"] if p["id"] == pattern_id]
    if existing:
        existing[0]["occurrences"] = existing[0].get("occurrences", 0) + 1
        existing[0]["last_seen"] = datetime.now(timezone.utc).isoformat()
    else:
        kb["known_patterns"].append({
            "id": pattern_id,
            "description": description,
            "detection": detection,
            "action": action,
            "discovered": datetime.now(timezone.utc).isoformat(),
            "last_seen": datetime.now(timezone.utc).isoformat(),
            "occurrences": 1,
            "source_example": source_id,
        })

    save_knowledge(kb)
    return kb


def record_verification(total, passed, rejected, corrections):
    """Record verification metrics."""
    kb = load_knowledge()
    kb["metrics"]["total_verifications"] += total
    kb["metrics"]["total_rejections"] += rejected
    kb["metrics"]["total_corrections"] += corrections
    save_knowledge(kb)


def add_lesson(lesson_text, category="general"):
    """Add a lesson learned."""
    kb = load_knowledge()
    kb["lessons_learned"].append({
        "lesson": lesson_text,
        "category": category,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    })
    save_knowledge(kb)


def get_pre_screening_rules():
    """
    Generate pre-screening rules from known patterns.
    These rules are applied to new data before full verification.
    """
    kb = load_knowledge()
    rules = []

    for pattern in kb["known_patterns"]:
        if pattern.get("occurrences", 0) >= 2:
            rules.append({
                "pattern_id": pattern["id"],
                "description": pattern["description"],
                "detection": pattern["detection"],
                "action": pattern["action"],
            })

    return rules


def initialize_knowledge_base():
    """Initialize with known patterns from our audit history."""
    kb = load_knowledge()

    # Patterns discovered during the forensic audit
    initial_patterns = [
        {
            "id": "AIC_IMAGE_ROTATION",
            "description": "AIC periodically rotates image_ids for artworks",
            "detection": "image_id in our URL doesn't match current API image_id",
            "action": "Update to current API image_id value",
            "discovered": "2026-05-14T00:00:00Z",
            "occurrences": 10,
        },
        {
            "id": "MET_HTML_IN_MEDIUM",
            "description": "Met API returns HTML tags in medium field (e.g. <i>Tsuba</i>)",
            "detection": "HTML tags in API medium/title fields",
            "action": "Strip HTML tags during normalization",
            "discovered": "2026-05-14T00:00:00Z",
            "occurrences": 3,
        },
        {
            "id": "MET_OBJECT_REMOVAL",
            "description": "Met Museum removes objects from API (returns 404)",
            "detection": "API returns 404 for previously valid object ID",
            "action": "REJECT - object cannot be verified",
            "discovered": "2026-05-14T00:00:00Z",
            "occurrences": 1,
        },
        {
            "id": "PRICE_ZERO_MARKET_NOTE",
            "description": "Price comparable with sale_price=0 is a market note, not real data",
            "detection": "sale_price == 0 in price_comparable",
            "action": "REJECT - price data must be real auction results only",
            "discovered": "2026-05-14T00:00:00Z",
            "occurrences": 1,
        },
        {
            "id": "ESTIMATED_RANGE_NOT_SALE",
            "description": "Estimated price ranges are not actual auction results",
            "detection": "auction_house field contains 'estimated' or 'range'",
            "action": "REJECT - only actual verified sale results accepted",
            "discovered": "2026-05-14T00:00:00Z",
            "occurrences": 1,
        },
        {
            "id": "CREDIT_LINE_AS_DESCRIPTION",
            "description": "Asset description is just a copy of the Met creditLine",
            "detection": "description matches creditLine pattern (e.g. 'Gift of...')",
            "action": "REWRITE - description must be original EDITION content",
            "discovered": "2026-05-14T00:00:00Z",
            "occurrences": 6,
        },
        {
            "id": "MET_UNICODE_DASH",
            "description": "Met API uses different dash characters (en-dash vs em-dash vs hyphen)",
            "detection": "Unicode character mismatch in comparison",
            "action": "Normalize dashes during comparison",
            "discovered": "2026-05-14T00:00:00Z",
            "occurrences": 5,
        },
        {
            "id": "AIC_CLOUDFLARE_403",
            "description": "AIC IIIF images return 403 for bot requests due to Cloudflare",
            "detection": "403 error on artic.edu/iiif image URLs",
            "action": "Known false positive - images work in browsers",
            "discovered": "2026-05-14T00:00:00Z",
            "occurrences": 17,
        },
    ]

    for p in initial_patterns:
        p.setdefault("last_seen", p["discovered"])
        p.setdefault("source_example", None)

    kb["known_patterns"] = initial_patterns
    kb["metrics"] = {
        "total_verifications": 120,  # From today's audit
        "total_rejections": 4,
        "total_corrections": 62,
        "false_positive_rate": 0.0,
    }
    kb["lessons_learned"] = [
        {
            "lesson": "Never trust API data without verification. Even trusted institutions have data quality issues.",
            "category": "philosophy",
            "recorded_at": "2026-05-14T00:00:00Z",
        },
        {
            "lesson": "Image IDs can change without notice. Always verify against current API.",
            "category": "technical",
            "recorded_at": "2026-05-14T00:00:00Z",
        },
        {
            "lesson": "Price data must come from actual auction results, never estimates or market notes.",
            "category": "data_quality",
            "recorded_at": "2026-05-14T00:00:00Z",
        },
        {
            "lesson": "Descriptions copied from API creditLines are not acceptable. All text must be original.",
            "category": "originality",
            "recorded_at": "2026-05-14T00:00:00Z",
        },
    ]

    save_knowledge(kb)
    print(f"✅ Knowledge base initialized with {len(initial_patterns)} patterns and {len(kb['lessons_learned'])} lessons")
    return kb


if __name__ == "__main__":
    import sys
    if "--init" in sys.argv:
        initialize_knowledge_base()
    else:
        kb = load_knowledge()
        print(f"Knowledge Base v{kb.get('version', '?')}")
        print(f"  Patterns: {len(kb.get('known_patterns', []))}")
        print(f"  Lessons: {len(kb.get('lessons_learned', []))}")
        print(f"  Metrics: {json.dumps(kb.get('metrics', {}), indent=4)}")
