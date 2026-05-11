---
name: japan-cultural-context
version: 1.0.0
description: "Deep cultural intelligence for AI agents — implicit communication, hierarchy, decision-making patterns unique to Japan"
domain: japan
categories: [protocol, organization, language]
tools_required:
  - protocol_check
  - protocol_list
  - organization_check
  - language_search
triggers:
  - "Japanese culture business"
  - "implicit communication Japan"
  - "hierarchy Japanese company"
  - "keigo honorific"
  - "reading the air kuuki"
  - "honne tatemae"
source: https://api.edition.sh
source_authorities:
  - "文化庁 — Cultural policy and keigo guidelines"
  - "日本経団連 — Corporate governance"
  - "日本語教育学会 — Linguistic research"
author: EDITION Intelligence Platform
last_verified: "2026-05-10"
---

# Japan Cultural Context

## When to Use This Skill

Activate when the agent needs to:
- Interpret ambiguous Japanese communication
- Understand unstated social rules
- Navigate corporate hierarchy correctly
- Produce culturally appropriate Japanese text
- Advise on gift-giving, apologies, or relationship management

## Why This Skill Exists

> LLMs trained on English-language data fundamentally misunderstand Japanese communication patterns. They treat "前向きに検討します" (we'll consider it positively) as positive — it usually means NO. This skill provides the cultural decoder ring.

## Key Knowledge

### The Communication Iceberg

What is said (建前 tatemae) ≠ What is meant (本音 honne)

| They Say | Surface Meaning | Actual Meaning |
|----------|----------------|----------------|
| 前向きに検討します | We'll consider positively | Polite refusal |
| ちょっと難しいですね | It's a bit difficult | No |
| 考えさせてください | Let me think about it | I need to consult superiors |
| 善処します | We'll do our best | We probably won't |
| 結構です | That's fine / No thank you | Context-dependent (ambiguous) |

### Corporate Hierarchy (役職)
Understanding titles is critical for keigo selection:

```
会長 (Kaichō) — Chairman
  └─ 社長 (Shachō) — President/CEO
      └─ 副社長 (Fuku-shachō) — VP
          └─ 専務 (Senmu) — Senior Managing Director
              └─ 常務 (Jōmu) — Managing Director
                  └─ 部長 (Buchō) — Department Head ★
                      └─ 課長 (Kachō) — Section Chief ★
                          └─ 係長 (Kakarichō) — Team Leader
                              └─ 主任 (Shunin) — Senior Staff
                                  └─ 一般社員 (Ippan shain) — Staff
```
★ = Most common interaction level for business partners

### Decision-Making Pattern
```
Individual idea → Nemawashi (根回し) → Draft proposal
     → Ringi (稟議) circulation → Stamps from all levels
     → Formal meeting (会議) → Ratification (not debate)
     → Implementation
```
**Time to decision**: 2-8 weeks (vs 1-2 days in US startups)
**But**: Once decided, execution is fast and unified

### Apology Culture
Apology level must match the severity:
1. **すみません** — Light (daily use, like "excuse me")
2. **申し訳ございません** — Formal business apology
3. **深くお詫び申し上げます** — Serious incident (press conference level)
4. **弁解の余地もございません** — Maximum severity (admits no excuse)

> ⚠️ In Japan, the one who apologizes first often gains moral standing. Delayed apology is viewed as arrogance.

### Gift-Giving (贈答)
Use `protocol_check` with "zoutou":
- **When**: Mid-year (お中元 July), Year-end (お歳暮 December), after business favors
- **Amount**: ¥3,000-5,000 for general, ¥5,000-10,000 for important relationships
- **Taboo items**: Sets of 4 (四=death), combs (苦死), sharp objects (cutting ties)
- **Wrapping**: Department store wrapping (のし noshi) required

### Keiretsu Networks
Use `organization_check` for corporate group awareness:
- Major groups: Mitsubishi, Mitsui, Sumitomo, Fuyo, Sanwa, DKB
- Cross-shareholding creates implicit loyalty networks
- Vendor selection often influenced by keiretsu membership

## Standard Operating Procedure

### Interpreting Communication
1. Identify the speaker's position using `organization_check`
2. Check keigo level with `language_search` with "keigo"
3. Apply tatemae/honne decoder from key knowledge above
4. Consider the organizational context

### Preparing Business Communication
1. Determine recipient's title and position
2. Select appropriate keigo level (sonkeigo for their actions, kenjōgo for yours)
3. Use cushion words (クッション言葉): 恐れ入りますが、差し支えなければ、お手数ですが
4. End with appropriate closing: よろしくお願いいたします

## Common Pitfalls

> ⚠️ **"Yes" doesn't mean agreement**: はい (hai) often means "I'm listening" or "I understand you spoke," not "I agree."

> ⚠️ **Direct feedback is rude**: Never say "That's wrong." Use "少し違うかもしれません" (It might be slightly different).

> ⚠️ **Age ≈ Authority**: In ambiguous situations, assume the older person has higher status. Offer the higher seat (上座 kamiza).
