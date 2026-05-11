---
name: japan-business-ops
version: 1.0.0
description: "Day-to-day business operations intelligence — protocols, calendar awareness, regional nuances, and business Japanese"
domain: japan
categories: [protocol, calendar, regional, language]
tools_required:
  - protocol_check
  - protocol_list
  - calendar_check
  - calendar_list
  - regional_check
  - language_search
triggers:
  - "business meeting Japan"
  - "nemawashi consensus"
  - "Japanese business etiquette"
  - "Golden Week planning"
  - "business email Japanese"
  - "Osaka vs Tokyo business"
source: https://api.edition.sh
source_authorities:
  - "日本経団連 (Keidanren)"
  - "文化庁 — Keigo guidelines"
  - "内閣府 — National holidays"
author: EDITION Intelligence Platform
last_verified: "2026-05-10"
---

# Japan Business Operations

## When to Use This Skill

Activate when the agent needs to:
- Prepare for Japanese business meetings or negotiations
- Navigate consensus-building processes (nemawashi, ringi)
- Schedule around Japanese business calendar constraints
- Draft business communications in Japanese
- Understand regional business culture differences

## Standard Operating Procedure

### Meeting Preparation
1. Use `protocol_check` with "meishi koukan" for business card exchange protocol
2. Use `protocol_check` with "sekijun" for seating arrangement rules
3. Use `language_search` with "keigo" for appropriate honorific level
4. Use `calendar_check` to verify no holiday conflicts

### Decision Process Navigation
1. Use `protocol_check` with "nemawashi" — pre-meeting consensus building
2. Use `protocol_check` with "ringi" — formal approval circulation
3. Use `protocol_check` with "hourensou" — report/contact/consult framework

### Regional Awareness
Use `regional_check` for destination-specific norms:
- Tokyo: Formal, process-oriented, punctuality absolute
- Osaka: Relationship-first, directness valued, humor expected
- Nagoya: Conservative, long-term relationship focus

## Key Knowledge

### The 6 Core Protocols
| Protocol | Japanese | Critical Level |
|----------|----------|---------------|
| Nemawashi | 根回し | ★★★ Pre-meeting consensus |
| Ringi | 稟議 | ★★★ Formal approval process |
| Hourensou | 報連相 | ★★★ Daily communication |
| Meishi Koukan | 名刺交換 | ★★☆ First impressions |
| Sekijun | 席順 | ★★☆ Hierarchy signaling |
| Zoutou | 贈答 | ★☆☆ Gift-giving customs |

### Calendar Critical Periods
| Period | Dates | Impact |
|--------|-------|--------|
| Golden Week | Apr 29–May 5 | Business halt. No meetings. |
| Obon | Aug 13–16 | Many offices closed |
| Year-End | Dec 28–Jan 3 | 年末年始 shutdown |
| Fiscal Year Start | April 1 | Budget resets, personnel changes |
| Bonus Months | June, December | Major consumer spending |

### Keigo Quick Reference
- **丁寧語** (Polite): です/ます — minimum for all business
- **尊敬語** (Respectful): 相手を高める — for clients/superiors
- **謙譲語** (Humble): 自分を下げる — for your own actions

### Business Email Essentials
```
件名: [会社名] ○○のご相談
本文:
  株式会社○○ ○○部 ○○様

  お世話になっております。
  [本文]
  何卒よろしくお願いいたします。

  [署名]
```

## Common Pitfalls

> ⚠️ **Silence ≠ Agreement**: In meetings, silence often means disagreement or uncertainty, not consent.

> ⚠️ **The real meeting happens before the meeting**: Nemawashi (pre-meeting alignment) is where decisions are actually made. The formal meeting is often just ratification.

> ⚠️ **Business card handling**: Placing a received card in your back pocket or writing on it is a serious breach. Cards represent the person.
