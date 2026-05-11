---
name: japan-market-entry
version: 1.0.0
description: "Complete operational guide for foreign companies entering the Japanese market — from incorporation to hiring"
domain: japan
categories: [regulation, foreign_entry, organization]
tools_required:
  - regulation_check
  - regulation_industries
  - foreign_entry_check
  - foreign_entry_list
  - organization_check
  - calendar_check
triggers:
  - "start a business in Japan"
  - "incorporate in Japan"
  - "Japanese company formation"
  - "work visa Japan"
  - "open office Tokyo"
  - "KK GK incorporation"
  - "Japan market entry"
source: https://api.edition.sh
source_authorities:
  - "法務省 (MOJ) — Corporate registration"
  - "入管庁 (ISA) — Visa and immigration"
  - "国税庁 (NTA) — Tax registration"
  - "厚生労働省 (MHLW) — Labor law"
  - "JETRO — Foreign investment guidance"
author: EDITION Intelligence Platform
last_verified: "2026-05-10"
---

# Japan Market Entry

## When to Use This Skill

Activate when the user or agent needs to:
- Establish a legal entity in Japan (KK or GK)
- Obtain a management visa (経営管理ビザ)
- Open a corporate bank account
- Hire employees under Japanese labor law
- Navigate tax registration and compliance
- Find commercial real estate

## Standard Operating Procedure

### Step 1: Determine Company Type
Use `foreign_entry_check` with query "法人設立" to get incorporation procedures.

**Key Decision**: KK (株式会社) vs GK (合同会社)
- **KK**: Higher credibility, required for certain licenses. Capital ¥1+, but ¥5M+ recommended for visa.
- **GK**: Simpler governance, lower costs. Similar to US LLC.

### Step 2: Check Industry Regulations
Use `regulation_check` with the target industry to identify required licenses.

**Critical**: Some industries require licenses BEFORE incorporation:
- Food service → 食品衛生責任者 + 営業許可
- Real estate → 宅地建物取引業免許
- Finance → 各種金融ライセンス

### Step 3: Incorporation Procedure
Execute `foreign_entry_check` for each sub-step:
1. Define articles of incorporation (定款)
2. Notarize at local notary office (公証役場)
3. Deposit capital (資本金払込)
4. Register at Legal Affairs Bureau (法務局)
5. Obtain company seal certificate (印鑑証明書)

### Step 4: Post-Incorporation Filings
Use `regulation_check` to verify required registrations:
- Tax office (税務署) — 法人設立届出書 within 2 months
- Prefectural/municipal tax — 事業開始届
- Social insurance — 社会保険適用届 within 5 days of hiring

### Step 5: Visa Application
Use `foreign_entry_check` with query "経営管理ビザ":
- Capital requirement: ¥5,000,000+ or 2+ full-time employees
- Physical office required (virtual office NOT accepted)
- Processing time: 1-3 months

### Step 6: Banking
Use `foreign_entry_check` with query "銀行口座":
- Major banks (MUFG, SMBC, Mizuho) require 6+ months of business history
- Neo-banks (GMO Aozora, PayPay Bank) may accept new companies
- Required: 登記簿謄本, 印鑑証明, 定款, representative's residence card

### Step 7: Check Calendar Timing
Use `calendar_check` to optimize timing:
- Fiscal year typically starts April 1
- Avoid Golden Week (late April–early May) for government filings
- Year-end (December) slowdowns for banking approvals

## Key Knowledge — Agent Must Know

### The Hanko (印鑑) System
Japan uses registered seals instead of signatures for legal documents. Three types:
- **実印 (Jitsuin)**: Registered with city hall, used for contracts
- **銀行印 (Ginko-in)**: Registered with bank, for financial transactions
- **認印 (Mitome-in)**: Everyday use, not legally binding

### Capital Requirements Reality
While legally ¥1 is sufficient, practical minimums:
- For visa: ¥5,000,000
- For bank account credibility: ¥3,000,000+
- For client trust: ¥10,000,000+ (especially for B2B)

### Timeline (Realistic)
| Step | Duration |
|------|----------|
| Preparation | 2-4 weeks |
| Incorporation registration | 1-2 weeks |
| Tax/insurance filings | 1-2 weeks |
| Visa application | 1-3 months |
| Bank account | 2-8 weeks |
| **Total** | **3-6 months** |

## Common Pitfalls

> ⚠️ **Virtual office trap**: Immigration rejects management visa applications with virtual office addresses. Physical office lease required.

> ⚠️ **Seal ordering lead time**: Custom company seals take 1-2 weeks. Order immediately after deciding company name.

> ⚠️ **Representative director residency**: At least one representative director must reside in Japan as of recent reforms (previously required for all directors).

## Confidence & Disclaimer
- Source verification: All procedures verified against 法務省, 入管庁, JETRO official publications
- Last verified: 2026-05-10
- ⚠️ This is operational guidance, not legal advice. Consult a 司法書士 (judicial scrivener) or 行政書士 (administrative scrivener) for specific cases.
