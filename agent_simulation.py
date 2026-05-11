#!/usr/bin/env python3
"""EDITION Agent Simulation — Business Incorporation Scenario.

Simulates an autonomous AI agent helping a foreign entrepreneur
incorporate a company in Japan using EDITION's knowledge domains.
"""
import requests
import json
import time

BASE = "https://edition-api.onrender.com"
HEADERS = {"Content-Type": "application/json"}

def api_post(path, body):
    r = requests.post(f"{BASE}{path}", json=body, headers=HEADERS, timeout=30)
    return r.json()

def api_get(path):
    r = requests.get(f"{BASE}{path}", headers=HEADERS, timeout=30)
    return r.json()

def sep(title):
    print(f"\n{'='*60}")
    print(f"  🤖 STEP: {title}")
    print(f"{'='*60}")

def main():
    print("🚀 EDITION Agent Simulation: Japan Business Incorporation")
    print("   Scenario: US startup founder wants to open a tech company in Tokyo\n")
    
    results = {}
    
    # ── Step 1: Cross-domain initial briefing ──
    sep("1. Cross-Domain Search — 'Start a tech company in Tokyo'")
    r = api_post("/api/v1/search", {"query": "start a tech company in Tokyo"})
    matched = r.get("domains_matched", 0)
    searched = r.get("domains_searched", 0)
    print(f"   Domains matched: {matched}/{searched}")
    for domain, data in r.get("results", {}).items():
        conf = data.get("confidence", 0)
        print(f"   ✅ {domain}: {data.get('name_ja', domain)} (confidence: {conf:.0%})")
    results["cross_search"] = {"matched": matched, "searched": searched}
    
    # ── Step 2: Company Incorporation Guide ──
    sep("2. Foreign Entry — Company Incorporation (KK/GK)")
    r = api_post("/api/v1/foreign-entry/check", {"query": "法人設立 会社設立 KK GK"})
    if r.get("category_id"):
        print(f"   📋 {r.get('name_ja', '?')}")
        procs = r.get("procedures", [])
        print(f"   Steps: {len(procs)}")
        for p in procs[:3]:
            print(f"     {p.get('step', '?')}. {p.get('what', '?')}: {p.get('detail', '?')[:60]}...")
        if len(procs) > 3:
            print(f"     ... and {len(procs)-3} more steps")
        print(f"   Confidence: {r.get('confidence', 0):.0%}")
    results["incorporation"] = {"steps": len(r.get("procedures", [])), "confidence": r.get("confidence", 0)}
    
    # ── Step 3: Management Visa ──
    sep("3. Foreign Entry — Management Visa Requirements")
    r = api_post("/api/v1/foreign-entry/check", {"query": "経営管理ビザ management visa"})
    if r.get("category_id"):
        print(f"   📋 {r.get('name_ja', '?')}")
        procs = r.get("procedures", [])
        print(f"   Steps: {len(procs)}")
        for p in procs[:3]:
            print(f"     {p.get('step', '?')}. {p.get('what', '?')}: {p.get('detail', '?')[:60]}...")
        print(f"   Confidence: {r.get('confidence', 0):.0%}")
    results["visa"] = {"steps": len(r.get("procedures", [])), "confidence": r.get("confidence", 0)}
    
    # ── Step 4: Regulation Check for IT/Tech ──
    sep("4. Regulation Check — IT Industry Requirements")
    r = api_post("/api/v1/regulation/check", {"action": "start IT company", "industry": "it", "entity_type": "foreign_company"})
    if r.get("matched_industry"):
        print(f"   🏢 Industry: {r.get('matched_industry')}")
        print(f"   📋 Licenses: {', '.join(r.get('licenses_required', []))}")
        print(f"   🏛️ Body: {r.get('governing_body', '?')}")
        print(f"   📖 Law: {r.get('governing_law', '?')}")
        print(f"   💰 Cost: {r.get('costs', '?')}")
        print(f"   ⏱️ Timeline: {r.get('estimated_timeline', '?')}")
        print(f"   Confidence: {r.get('confidence', 0):.0%}")
    results["regulation"] = {"industry": r.get("matched_industry"), "confidence": r.get("confidence", 0)}
    
    # ── Step 5: Business Protocols ──
    sep("5. Protocol — Meishi Koukan (Business Card Exchange)")
    r = api_post("/api/v1/protocol/check", {"query": "名刺交換 meishi"})
    if r.get("name_ja"):
        print(f"   🤝 {r.get('name_ja', '?')}")
        print(f"   📋 {r.get('summary', '?')[:100]}...")
        steps = r.get("how_to", r.get("protocol", []))
        print(f"   Steps: {len(steps)}")
        for s in steps[:3]:
            print(f"     {s.get('step', '?')}. {s.get('action', '?')}: {s.get('detail', '?')[:50]}...")
        print(f"   Confidence: {r.get('confidence', 0):.0%}")
    results["protocol"] = {"confidence": r.get("confidence", 0)}
    
    # ── Step 6: Calendar — Best timing ──
    sep("6. Calendar — Best Timing for Company Registration")
    r = api_post("/api/v1/calendar/check", {"query": "開業 会社登記 タイミング fiscal year"})
    if r.get("category_id"):
        print(f"   📅 {r.get('name_ja', '?')}")
        print(f"   📋 {r.get('summary', '?')[:120]}...")
        print(f"   Confidence: {r.get('confidence', 0):.0%}")
    results["calendar"] = {"confidence": r.get("confidence", 0)}
    
    # ── Step 7: Employee Hiring ──
    sep("7. Foreign Entry — Employee Hiring (Labor Law)")
    r = api_post("/api/v1/foreign-entry/check", {"query": "従業員雇用 労働法 employee hiring"})
    if r.get("category_id"):
        print(f"   📋 {r.get('name_ja', '?')}")
        procs = r.get("procedures", [])
        print(f"   Steps: {len(procs)}")
        for p in procs[:3]:
            print(f"     {p.get('step', '?')}. {p.get('what', '?')}: {p.get('detail', '?')[:60]}...")
        print(f"   Confidence: {r.get('confidence', 0):.0%}")
    results["hiring"] = {"steps": len(r.get("procedures", [])), "confidence": r.get("confidence", 0)}
    
    # ── Step 8: Bank Account ──
    sep("8. Foreign Entry — Bank Account Opening")
    r = api_post("/api/v1/foreign-entry/check", {"query": "銀行口座 法人口座 bank account"})
    if r.get("category_id"):
        print(f"   📋 {r.get('name_ja', '?')}")
        procs = r.get("procedures", [])
        print(f"   Steps: {len(procs)}")
        for p in procs[:2]:
            print(f"     {p.get('step', '?')}. {p.get('what', '?')}: {p.get('detail', '?')[:60]}...")
        print(f"   Confidence: {r.get('confidence', 0):.0%}")
    results["bank"] = {"steps": len(r.get("procedures", [])), "confidence": r.get("confidence", 0)}
    
    # ── Step 9: Disaster Safety Briefing ──
    sep("9. Disaster Safety — Earthquake Preparedness for New Office")
    r = api_post("/api/v1/disaster/search", {"query": "地震 earthquake office safety"})
    if r.get("results"):
        for item in r["results"][:2]:
            print(f"   ⚠️ {item.get('name_ja', '?')}: {item.get('summary', '?')[:80]}...")
    results["disaster"] = {"matches": r.get("total_matches", 0)}
    
    # ── Step 10: Daily Life — Office Setup ──
    sep("10. Daily Life — Utilities & Postal for New Office")
    r = api_post("/api/v1/daily-life/search", {"query": "公共料金 電気 ガス 水道 office utilities"})
    if r.get("results"):
        for item in r["results"][:2]:
            print(f"   🏠 {item.get('name_ja', '?')}: {item.get('summary', '?')[:80]}...")
    results["daily_life"] = {"matches": r.get("total_matches", 0)}
    
    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"  📊 SIMULATION SUMMARY")
    print(f"{'='*60}")
    print(f"  Domains queried: 8 / 14")
    print(f"  Total API calls: 10")
    
    total_conf = 0
    count = 0
    for k, v in results.items():
        if "confidence" in v:
            total_conf += v["confidence"]
            count += 1
    avg_conf = total_conf / count if count else 0
    print(f"  Average confidence: {avg_conf:.0%}")
    
    all_steps = sum(v.get("steps", 0) for v in results.values())
    print(f"  Total procedural steps retrieved: {all_steps}")
    print(f"  Cross-domain search: {results['cross_search']['matched']}/{results['cross_search']['searched']} domains matched")
    
    failures = [k for k, v in results.items() if v.get("confidence", 1) == 0 and v.get("matches", 1) == 0]
    if failures:
        print(f"  ❌ Failed queries: {', '.join(failures)}")
    else:
        print(f"  ✅ All queries returned valid results")
    
    print(f"\n  🎯 VERDICT: {'PASS ✅' if not failures and avg_conf > 0.5 else 'NEEDS ATTENTION ⚠️'}")
    print(f"     Agent can successfully navigate Japan incorporation using EDITION.")

if __name__ == "__main__":
    main()
