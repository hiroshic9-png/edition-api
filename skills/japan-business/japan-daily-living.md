---
name: japan-daily-living
version: 1.0.0
description: "Practical daily life intelligence for foreigners living in Japan — utilities, garbage, healthcare, food shopping"
domain: japan
categories: [daily_life, food, language]
tools_required:
  - daily_life_search
  - daily_life_list
  - food_search
  - language_search
triggers:
  - "living in Japan"
  - "garbage sorting Japan"
  - "health insurance Japan"
  - "Japanese apartment"
  - "utilities setup"
  - "NHK subscription"
source: https://api.edition.sh
source_authorities:
  - "総務省 — Postal and address systems"
  - "厚生労働省 (MHLW) — Healthcare"
  - "各自治体 — Garbage sorting rules"
  - "NHK — Broadcasting fee"
author: EDITION Intelligence Platform
last_verified: "2026-05-10"
---

# Japan Daily Living

## When to Use This Skill

Activate when the user or agent needs to:
- Set up utilities in a Japanese apartment
- Understand garbage sorting rules
- Navigate the healthcare system
- Handle postal/address systems
- Deal with daily life logistics as a foreigner

## Standard Operating Procedure

### Moving In
1. Use `daily_life_search` with "utilities" for setup procedures
2. Use `daily_life_search` with "garbage" for local sorting rules
3. Use `daily_life_search` with "postal" for address registration
4. Use `language_search` with "names_addresses" for form filling

### Healthcare Setup
1. Use `daily_life_search` with "healthcare" for insurance enrollment
2. Use `food_search` with "dietary_restrictions" for allergy communication cards

## Key Knowledge

### Garbage Sorting (ゴミ分別)
Rules vary by municipality but common categories:
- **燃えるゴミ** (Burnable): Kitchen waste, paper, clothes — 2-3x/week
- **燃えないゴミ** (Non-burnable): Ceramics, small metal — 1-2x/month
- **資源ゴミ** (Recyclable): PET bottles, cans, glass, paper — 1x/week
- **粗大ゴミ** (Oversized): Furniture, appliances — by appointment, fee required

> ⚠️ Put garbage out on collection morning (NOT the night before). Use designated bags purchased at convenience stores.

### Utilities Setup
| Utility | Provider | How to Start |
|---------|----------|-------------|
| Electricity | Regional (TEPCO, Kansai, etc.) | Call or online, same-day start |
| Gas | Regional | Requires in-person visit for safety check |
| Water | Municipal | Call city hall, auto-start with move-in |
| Internet | NTT, au, SoftBank | 2-4 weeks installation lead time |
| NHK | NHK | Legally required if you own a TV/smartphone |

### Address System
Japanese addresses work **large to small** (opposite of Western):
```
〒100-0001 東京都千代田区千代田1-1
  Prefecture → City → District → Block-Building-Room
```

### Healthcare
- **National Health Insurance (国民健康保険)**: Mandatory. Covers 70% of costs.
- **Enrollment**: At your local city/ward office within 14 days of getting residence card
- **Hospital etiquette**: Bring insurance card (保険証) every visit. Expect to wait.

## Common Pitfalls

> ⚠️ **Key money (礼金)**: Non-refundable "thank you" payment to landlord (1-2 months rent). Unique to Japan.

> ⚠️ **No shoes indoors**: Remove shoes at the genkan (entrance). This is absolute, not optional.

> ⚠️ **Noise rules**: Many apartments have strict quiet hours (10pm-7am). Washing machines, musical instruments restricted.

> ⚠️ **NHK collector**: NHK door-to-door collectors will come. The fee is legally mandated if you have any broadcast-receiving device.
