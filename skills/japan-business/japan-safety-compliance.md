---
name: japan-safety-compliance
version: 1.0.0
description: "Disaster preparedness and regulatory compliance — earthquakes, typhoons, emergency procedures, and industry regulations"
domain: japan
categories: [disaster, regulation]
tools_required:
  - disaster_search
  - disaster_list
  - regulation_check
  - regulation_industries
  - regulation_tourist
triggers:
  - "earthquake Japan"
  - "typhoon warning"
  - "emergency contacts Japan"
  - "business compliance Japan"
  - "safety regulations"
  - "disaster preparedness"
source: https://api.edition.sh
source_authorities:
  - "気象庁 (JMA) — Earthquake and weather warnings"
  - "消防庁 — Fire and disaster management"
  - "内閣府防災 — Disaster prevention policy"
  - "各省庁 — Industry-specific regulations"
author: EDITION Intelligence Platform
last_verified: "2026-05-10"
---

# Japan Safety & Compliance

## When to Use This Skill

Activate when the agent needs to:
- Respond to earthquake, typhoon, or tsunami alerts
- Provide emergency procedures for someone in Japan
- Check business regulatory compliance requirements
- Verify required permits and licenses for specific industries
- Prepare disaster readiness plans

## Standard Operating Procedure

### Earthquake Response (Priority: LIFE SAFETY)
1. Use `disaster_search` with "earthquake" for immediate guidance
2. Assess shindo (震度) level from alert
3. Provide appropriate action based on severity

### Typhoon Preparation
1. Use `disaster_search` with "typhoon" for warning levels
2. Check 計画運休 (planned service suspensions) for transportation
3. Advise on supplies and shelter

### Business Compliance Check
1. Use `regulation_industries` to list all covered industries
2. Use `regulation_check` with specific industry and action
3. Cross-reference with `disaster_search` for workplace safety requirements

## Key Knowledge

### Shindo Scale (震度) — Japan's Unique Intensity Scale
NOT the same as Richter magnitude. Shindo measures local shaking intensity:

| Shindo | Feeling | Action Required |
|--------|---------|----------------|
| 0-2 | Slight to light | None |
| 3 | Moderate shaking | Be aware |
| 4 | Strong shaking | Hold on to furniture |
| 5弱 | Very strong | Drop, Cover, Hold On |
| 5強 | Intense | Evacuation may be needed |
| 6弱 | Violent | Difficult to stand, evacuate |
| 6強 | Devastating | Crawl to safety |
| 7 | Extreme | Maximum emergency |

### Earthquake Early Warning (緊急地震速報)
- Alerts arrive **seconds before** shaking
- Delivered via: TV, radio, smartphone (even tourist phones)
- Sound: Distinctive alarm tone — learn to recognize it
- Action: You have 5-30 seconds. Drop under desk/table immediately

### Typhoon Warning Levels (5段階警戒レベル)
| Level | Color | Meaning | Action |
|-------|-------|---------|--------|
| 1 | White | Early advisory | Be aware |
| 2 | Yellow | Flood/landslide watch | Prepare evacuation |
| 3 | Red | Elderly evacuation | Elderly/disabled evacuate |
| 4 | Purple | Evacuation order | Everyone evacuate immediately |
| 5 | Black | Emergency situation | Life-threatening, take best action |

### Emergency Numbers
```
110 — Police (警察)
119 — Fire & Ambulance (消防)
118 — Coast Guard (海上保安)
171 — Disaster Message Dial (災害用伝言ダイヤル)
#7119 — Medical Advice (救急相談)
050-3816-2787 — Japan Visitor Hotline (24h, multilingual)
```

### Disaster Preparedness Kit (防災バッグ)
Recommended by 内閣府:
- Water: 3L per person per day × 3 days
- Food: Non-perishable, 3 days supply
- Flashlight + spare batteries
- Radio (hand-crank preferred)
- First aid kit
- Cash (ATMs won't work during power outage)
- Copies of ID documents
- Phone charger (portable battery)

### Business Regulatory Framework
10 industries with full compliance data:
1. Food Service (食品) — 食品衛生法
2. Real Estate (不動産) — 宅建業法
3. Finance (金融) — 金融商品取引法
4. Healthcare (医療) — 医療法
5. Construction (建設) — 建設業法
6. Education (教育) — 学校教育法
7. Transport (運輸) — 道路運送法
8. Retail (小売) — 大店立地法
9. IT/Telecom (IT) — 電気通信事業法
10. Manufacturing (製造) — 製造物責任法

## Common Pitfalls

> ⚠️ **Don't run outside during earthquake**: Japanese buildings are earthquake-resistant. Inside is usually safer than outside (falling glass/debris).

> ⚠️ **Typhoon = train shutdown**: Major railways announce 計画運休 (planned suspensions) 8-24 hours before typhoon landfall. Check in advance.

> ⚠️ **Evacuation shelters (避難所) have rules**: Remove shoes, maintain quiet hours, follow volunteer staff instructions. Pets may not be allowed inside.

> ⚠️ **Foreign business compliance**: Penalties for regulatory violations can include criminal charges for company representatives, not just fines.
