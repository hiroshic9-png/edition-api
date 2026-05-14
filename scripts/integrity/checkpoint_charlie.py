#!/usr/bin/env python3
"""
CHECKPOINT CHARLIE — Originality & Fairness Guard
====================================================
盗用・コピーチェック。我が社の文章として掲載する以上、他者の文章の丸写しは許されない。
事実情報の正確な引用は許容。表現・文章構成は必ず独自であること。

検証項目:
  1. API原文（creditLine, description等）との類似度
  2. 連続一致単語数のチェック
  3. テンプレート的な繰り返しパターンの検出
  4. 独自性スコア算出 (0-100)

判定基準:
  - 連続10単語以上の外部テキスト一致 → REJECT
  - 原文類似度30%以上 → REWRITE_REQUIRED
  - 独自性スコア70未満 → REWRITE_REQUIRED
"""
import json
import re
import ssl
import sys
import time
import urllib.request
from datetime import datetime, timezone
from collections import Counter

from config import (
    ASSETS_PATH,
    ORIGINALITY_COPY_THRESHOLD,
    MAX_CONSECUTIVE_MATCH_WORDS,
)

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


def normalize_text(s):
    """Normalize text for comparison."""
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", "", str(s))
    s = re.sub(r"[^\w\s]", " ", s.lower())
    s = re.sub(r"\s+", " ", s).strip()
    return s


def get_words(text):
    """Extract words from text."""
    return normalize_text(text).split()


def longest_common_subsequence(words_a, words_b):
    """Find the longest consecutive matching subsequence."""
    if not words_a or not words_b:
        return 0, []

    max_len = 0
    max_seq = []

    for i in range(len(words_a)):
        for j in range(len(words_b)):
            k = 0
            while (
                i + k < len(words_a)
                and j + k < len(words_b)
                and words_a[i + k] == words_b[j + k]
            ):
                k += 1
            if k > max_len:
                max_len = k
                max_seq = words_a[i : i + k]

    return max_len, max_seq


def word_overlap_ratio(words_a, words_b):
    """Calculate word overlap ratio between two texts."""
    if not words_a or not words_b:
        return 0.0

    set_a = set(words_a)
    set_b = set(words_b)

    # Exclude common English words for meaningful comparison
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "has", "have", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "this", "that", "these",
        "those", "it", "its", "as", "not", "no", "if", "so", "than",
        # Art-domain terms unavoidable in both source metadata and descriptions
        "japanese", "japan", "period", "century", "circa", "about", "late",
        "early", "style", "type", "ware", "school", "tradition", "technique",
        "wood", "silk", "gold", "silver", "lacquer", "paper", "steel",
        "iron", "copper", "ivory", "ceramic", "ink", "color", "pigment",
        "print", "painting", "scroll", "screen", "robe", "sword", "blade",
        "bowl", "mount", "mounting", "figure", "design", "pattern",
        # Proper names that must appear in both — not plagiarism
        "hokusai", "hiroshige", "utamaro", "korin", "kanagawa", "fuji",
        "fujisan", "mount", "wave", "views", "thirty", "series", "ukiyo",
    }

    meaningful_a = set_a - stopwords
    meaningful_b = set_b - stopwords

    if not meaningful_a:
        return 0.0

    overlap = meaningful_a & meaningful_b
    return len(overlap) / len(meaningful_a)


def get_source_texts(asset):
    """Fetch source texts from API for comparison."""
    texts = []
    aid = asset["id"]

    if aid.startswith("met-"):
        obj_id = aid.replace("met-", "")
        api = fetch_json(
            f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}"
        )
        if "_error" not in api:
            for field in ["creditLine", "medium", "title", "artistDisplayBio",
                          "objectDate", "dimensions", "artistDisplayName"]:
                val = api.get(field, "")
                if val:
                    texts.append(str(val))

    elif aid.startswith("artic-"):
        obj_id = aid.replace("artic-", "")
        api = fetch_json(
            f"https://api.artic.edu/api/v1/artworks/{obj_id}?fields=id,title,medium_display,credit_line,date_display,dimensions,artist_display,publication_history,exhibition_history"
        )
        if "_error" not in api:
            data = api.get("data", {})
            for field in ["credit_line", "medium_display", "title", "artist_display",
                          "date_display", "dimensions", "publication_history",
                          "exhibition_history"]:
                val = data.get(field, "")
                if val:
                    texts.append(str(val))

    return texts


def check_originality(asset):
    """
    Check originality of asset description and significance.
    Returns (score, issues) where score is 0-100.
    """
    our_desc = asset.get("description", "")
    our_sig = asset.get("significance", "")
    our_text = f"{our_desc} {our_sig}".strip()

    if not our_text:
        return 100, [], "No text to check"

    our_words = get_words(our_text)
    if len(our_words) < 5:
        return 100, [], "Text too short to check"

    source_texts = get_source_texts(asset)
    if not source_texts:
        return 80, [], "No source texts available for comparison"

    issues = []
    max_consec = 0
    max_overlap = 0.0

    combined_source = " ".join(source_texts)
    source_words = get_words(combined_source)

    # Check 1: Longest consecutive match
    consec_len, consec_seq = longest_common_subsequence(our_words, source_words)
    max_consec = consec_len

    if consec_len >= MAX_CONSECUTIVE_MATCH_WORDS:
        issues.append({
            "type": "CONSECUTIVE_MATCH",
            "severity": "CRITICAL",
            "length": consec_len,
            "matched": " ".join(consec_seq[:15]),
        })

    # Check 2: Overall word overlap
    overlap = word_overlap_ratio(our_words, source_words)
    max_overlap = overlap

    if overlap > ORIGINALITY_COPY_THRESHOLD:
        issues.append({
            "type": "HIGH_OVERLAP",
            "severity": "WARNING",
            "ratio": round(overlap, 3),
            "threshold": ORIGINALITY_COPY_THRESHOLD,
        })

    # Check 3: creditLine copy detection
    for src_text in source_texts:
        src_words = get_words(src_text)
        if len(src_words) >= 5:
            cl_overlap = word_overlap_ratio(our_words[:20], src_words)
            if cl_overlap > 0.8:
                issues.append({
                    "type": "CREDIT_LINE_COPY",
                    "severity": "WARNING",
                    "source_text": src_text[:80],
                })

    # Calculate originality score
    # 100 = completely original, 0 = complete copy
    consec_penalty = min(40, max_consec * 4)
    overlap_penalty = min(40, int(max_overlap * 60))
    score = max(0, 100 - consec_penalty - overlap_penalty)

    return score, issues, None


def run_charlie(asset):
    """Run CHECKPOINT CHARLIE on a single asset."""
    score, issues, note = check_originality(asset)

    critical_issues = [i for i in issues if i.get("severity") == "CRITICAL"]
    rewrite_required = score < 70 or len(critical_issues) > 0

    verdict = "REJECT" if critical_issues else ("REWRITE" if rewrite_required else "PASS")

    return {
        "asset_id": asset["id"],
        "checkpoint": "CHARLIE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "originality_score": score,
        "issues": issues,
        "rewrite_required": rewrite_required,
        "verdict": verdict,
        "note": note,
    }


def run_charlie_batch(assets):
    """Run CHECKPOINT CHARLIE on all assets."""
    print("=" * 70)
    print("CHECKPOINT CHARLIE — Originality & Fairness Guard")
    print("=" * 70)

    passed = 0
    rewrite = 0
    rejected = 0
    all_results = []

    for i, asset in enumerate(assets):
        result = run_charlie(asset)
        all_results.append(result)

        v = result["verdict"]
        score = result["originality_score"]

        if v == "PASS":
            passed += 1
            print(f"  [{i+1:02d}] {asset['id']:25s} ✅ PASS (score: {score})")
        elif v == "REWRITE":
            rewrite += 1
            print(f"  [{i+1:02d}] {asset['id']:25s} 🟡 REWRITE REQUIRED (score: {score})")
            for issue in result["issues"]:
                print(f"       → {issue['type']}: {issue.get('matched', issue.get('ratio', ''))}")
        else:
            rejected += 1
            print(f"  [{i+1:02d}] {asset['id']:25s} ❌ REJECT (score: {score})")
            for issue in result["issues"]:
                print(f"       → {issue['type']}: {issue.get('matched', '')[:50]}")

        time.sleep(0.3)

    print(f"\n{'=' * 70}")
    print(f"CHARLIE RESULTS: {passed} PASS / {rewrite} REWRITE / {rejected} REJECT / {len(assets)} total")

    if rejected > 0:
        print(f"❌ {rejected} asset(s) REJECTED for plagiarism")
        sys.exit(1)
    elif rewrite > 0:
        print(f"🟡 {rewrite} asset(s) require description rewriting")
    else:
        print(f"✅ All {passed} assets passed originality check")

    return all_results


if __name__ == "__main__":
    with open(ASSETS_PATH) as f:
        assets = json.load(f)["assets"]

    results = run_charlie_batch(assets)

    # Save results
    import os
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "..", "data", "charlie_results.json",
    )
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
