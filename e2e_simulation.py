#!/usr/bin/env python3
"""E2E Simulation: Foreign AI agent opens a restaurant in Tokyo.

This script simulates the full journey of an AI agent using EDITION's APIs
to navigate the process of opening a restaurant in Japan.
It records every API call, what was useful, and what was missing.
"""
import json
import requests
import sys
from datetime import datetime

BASE = "http://localhost:8001"
RESULTS = []

def call_api(method, path, body=None, description=""):
    """Call an API and record the result."""
    url = f"{BASE}{path}"
    try:
        if method == "GET":
            r = requests.get(url, timeout=10)
        else:
            r = requests.post(url, json=body, timeout=10)
        data = r.json()
        success = r.status_code == 200
    except Exception as e:
        data = {"error": str(e)}
        success = False

    result = {
        "step": description,
        "method": method,
        "path": path,
        "body": body,
        "status": "OK" if success else "FAIL",
        "response_keys": list(data.keys()) if isinstance(data, dict) else "list",
        "useful_fields": [],
        "gaps": [],
    }
    RESULTS.append(result)
    return data, success, result


def simulate():
    print("=" * 70)
    print("E2E SIMULATION: Foreign AI Agent Opens a Restaurant in Tokyo")
    print("=" * 70)

    # ── STEP 0: Agent discovers what industries EDITION knows about ──
    print("\n[STEP 0] Discovering available industries...")
    data, ok, r = call_api("GET", "/api/v1/regulation/industries", description="0. 対応業種の確認")
    if ok:
        industries = data.get("industries", [])
        print(f"  → {len(industries)} industries available")
        r["useful_fields"] = ["industries list"]
        if "飲食店" not in [i.get("name", i) if isinstance(i, dict) else i for i in industries]:
            r["gaps"].append("飲食店が一覧に含まれていない")
    else:
        r["gaps"].append("業種一覧APIが機能しない")

    # ── STEP 1: Get regulation info for restaurant industry ──
    print("\n[STEP 1] Checking restaurant industry regulations...")
    data, ok, r = call_api("POST", "/api/v1/regulation/check",
                           body={"industry": "飲食店", "business_type": "レストラン"},
                           description="1. 飲食店の規制情報取得")
    if ok:
        r["useful_fields"] = [k for k in data.keys() if data.get(k)]
        # Check for procedures
        if "procedures" in data:
            steps = data["procedures"]
            print(f"  → {len(steps)} procedural steps found")
            r["useful_fields"].append(f"procedures ({len(steps)} steps)")
        else:
            r["gaps"].append("手続きステップ(procedures)が返されない")

        # Check what's missing for a foreigner
        if "foreign_company_notes" in data:
            print(f"  → Foreign notes: {data['foreign_company_notes'][:80]}...")
            r["useful_fields"].append("foreign_company_notes")
        else:
            r["gaps"].append("外国人向けの注意事項がない")
    else:
        r["gaps"].append("飲食店の規制情報が取得できない")

    # ── STEP 2: Check business protocols (nemawashi for lease negotiation) ──
    print("\n[STEP 2] Learning business protocols for lease negotiation...")
    data, ok, r = call_api("POST", "/api/v1/protocol/check",
                           body={"query": "不動産 賃貸 契約 交渉"},
                           description="2. 物件契約の商慣習確認")
    if ok:
        if data.get("matched_protocol"):
            print(f"  → Matched: {data.get('name_ja', 'N/A')}")
            r["useful_fields"] = ["matched_protocol", "name_ja"]
        else:
            print(f"  → No match for real estate negotiation")
            r["gaps"].append("不動産契約交渉に関するプロトコルがマッチしない")
    r["gaps"].append("物件探し（不動産仲介の利用方法、敷金・礼金・保証金の説明）が欠落")

    # ── STEP 3: Check regional differences for Tokyo ──
    print("\n[STEP 3] Checking Tokyo-specific regulations...")
    data, ok, r = call_api("POST", "/api/v1/regional/check",
                           body={"query": "東京 飲食店 条例"},
                           description="3. 東京の地域規制確認")
    if ok:
        if data.get("matched_category"):
            print(f"  → Matched category: {data.get('category_id')}")
            r["useful_fields"] = ["matched_category", "regions"]
        else:
            r["gaps"].append("東京+飲食店の組み合わせにマッチしない")
    r["gaps"].append("東京都の飲食店特有の条例（深夜営業、路上看板等）の詳細がない")

    # ── STEP 4: Check calendar for optimal timing ──
    print("\n[STEP 4] Checking business calendar for opening timing...")
    data, ok, r = call_api("POST", "/api/v1/calendar/check",
                           body={"query": "開業 タイミング 時期 いつ"},
                           description="4. 開業の最適タイミング確認")
    if ok:
        if data.get("matched_category"):
            cat = data.get("category_id")
            print(f"  → Matched: {cat}")
            r["useful_fields"] = ["seasonal_business monthly_guide"]
            if cat == "seasonal_business":
                guide = data.get("monthly_guide", {})
                print(f"  → {len(guide)} months of guidance")
        else:
            r["gaps"].append("開業タイミングの質問にマッチしない")
    r["gaps"].append("飲食店特有の季節性（忘年会シーズンに開業すべきか等）の判断材料がない")

    # ── STEP 5: Check organization structure (finding suppliers) ──
    print("\n[STEP 5] Understanding supplier/payment practices...")
    data, ok, r = call_api("POST", "/api/v1/organization/check",
                           body={"query": "支払い 仕入先 請求書"},
                           description="5. 仕入先との支払慣行確認")
    if ok:
        if data.get("matched_category"):
            print(f"  → Matched: {data.get('category_id')}")
            r["useful_fields"] = ["payment_methods", "standard_terms"]
        else:
            r["gaps"].append("支払い慣行にマッチしない")
    r["gaps"].append("飲食店の仕入れ（食品卸の見つけ方、現金取引の割合等）の業種特化情報がない")

    # ── STEP 6: Check meishi protocol for meeting health inspector ──
    print("\n[STEP 6] Preparing for meetings (business card protocol)...")
    data, ok, r = call_api("GET", "/api/v1/protocol/meishi",
                           description="6. 名刺交換プロトコル確認")
    if ok:
        if data.get("protocol"):
            steps = data.get("protocol", [])
            print(f"  → {len(steps)} protocol steps")
            r["useful_fields"] = ["protocol steps", "taboos", "modern_notes"]
        else:
            r["gaps"].append("名刺プロトコルの詳細が取得できない")

    # ── STEP 7: Cross-domain query (the real test) ──
    print("\n[STEP 7] Cross-domain query: '大阪で飲食店を開業する手順と地域の注意点'")
    # Try regulation
    data1, ok1, _ = call_api("POST", "/api/v1/regulation/check",
                             body={"industry": "飲食店"},
                             description="7a. 飲食店規制（横断テスト）")
    # Try regional
    data2, ok2, _ = call_api("POST", "/api/v1/regional/check",
                             body={"query": "大阪 飲食店"},
                             description="7b. 大阪地域情報（横断テスト）")
    # Try calendar
    data3, ok3, _ = call_api("POST", "/api/v1/calendar/check",
                             body={"query": "開業"},
                             description="7c. 開業カレンダー（横断テスト）")

    r = {"step": "7. ドメイン横断クエリ", "method": "MULTI", "path": "cross-domain",
         "body": "大阪で飲食店を開業する手順と地域の注意点", "status": "PARTIAL",
         "response_keys": [], "useful_fields": [], "gaps": []}

    if ok1 and ok2 and ok3:
        r["useful_fields"] = ["regulation OK", "regional OK", "calendar OK"]
        r["status"] = "OK (but manual orchestration required)"
    r["gaps"] = [
        "横断検索API（/search）が存在しない — エージェントが3回APIを叩く必要がある",
        "3つのレスポンスを統合する責任がエージェント側にある",
        "大阪の飲食店特有の情報（客引き規制条例等）が自動で紐づかない",
    ]
    RESULTS.append(r)

    # ── STEP 8: Check what's completely missing ──
    print("\n[STEP 8] Identifying completely missing capabilities...")
    missing = {
        "step": "8. 完全に欠落している機能",
        "method": "N/A", "path": "N/A", "body": None,
        "status": "ANALYSIS",
        "response_keys": [],
        "useful_fields": [],
        "gaps": [
            "法人設立の手続き（会社設立 → 定款認証 → 登記）が規制KBに含まれていない",
            "ビザ・在留資格（経営管理ビザ）の取得手続きが欠落",
            "銀行口座開設の手続き・必要書類（外国人は困難）が欠落",
            "税務署・都道府県への開業届出の詳細が手続きステップに含まれていない（Step 6に概要のみ）",
            "物件探しのプロセス（不動産仲介、居抜き物件、敷金礼金の概念）が欠落",
            "従業員の採用・労務管理（雇用契約、就業規則、36協定等）の知識が欠落",
            "多言語対応なし — APIレスポンスは全て日本語。英語UIなしで外国エージェントが使いにくい",
            "コスト総額のシミュレーション機能がない（資本金 + 物件 + 設備 + 許認可 = 合計いくら？）",
        ],
    }
    RESULTS.append(missing)

    # ── Report ──
    print("\n" + "=" * 70)
    print("SIMULATION REPORT")
    print("=" * 70)

    total_gaps = 0
    total_useful = 0
    for r in RESULTS:
        gaps = len(r["gaps"])
        useful = len(r["useful_fields"])
        total_gaps += gaps
        total_useful += useful
        status_icon = "✅" if r["status"] == "OK" else "⚠️" if "PARTIAL" in str(r["status"]) else "📊" if r["status"] == "ANALYSIS" else "❌"
        print(f"\n{status_icon} {r['step']}")
        if r["useful_fields"]:
            print(f"   有用: {', '.join(r['useful_fields'])}")
        if r["gaps"]:
            for g in r["gaps"]:
                print(f"   🔴 GAP: {g}")

    print(f"\n{'=' * 70}")
    print(f"SUMMARY: {total_useful} useful fields / {total_gaps} gaps identified")
    print(f"{'=' * 70}")

    return RESULTS


if __name__ == "__main__":
    results = simulate()
    # Save to JSON
    out_path = "/Users/hiroshisato/.gemini/antigravity/scratch/japan-ops-mvp/e2e_simulation_report.json"
    with open(out_path, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nFull report saved to: {out_path}")
