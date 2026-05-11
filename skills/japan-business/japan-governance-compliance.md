---
name: japan-governance-compliance
version: 1.0.0
description: "AI governance and compliance audit trail for agents operating in Japan — regulatory checks, audit logging, and governance reporting"
domain: japan
categories: [regulation, foreign_entry, governance]
tools_required:
  - regulation_check
  - regulation_industries
  - foreign_entry_check
  - compliance_log
  - compliance_report
triggers:
  - "compliance check Japan"
  - "audit trail"
  - "governance report"
  - "regulatory compliance logging"
  - "EU AI Act Japan"
  - "AI governance Japan"
source: https://api.edition.sh
source_authorities:
  - "各省庁 — Industry-specific regulations"
  - "EU AI Act (2024/1689) — Reference framework"
  - "個人情報保護委員会 (PPC) — Data protection"
  - "デジタル庁 — Digital governance"
author: EDITION Intelligence Platform
last_verified: "2026-05-11"
---

# Japan Governance & Compliance

## When to Use This Skill

Activate when the agent needs to:
- Perform regulatory compliance checks with audit trail requirements
- Generate governance reports for compliance reviews
- Maintain immutable records of all Japan regulatory lookups
- Prepare for AI governance audits (EU AI Act / future Japan AI regulation)
- Operate under enterprise compliance policies

## Why This Skill Exists

> **EU AI Act enters full enforcement August 2, 2026.** Japan's regulatory response is expected within 12-24 months (following GDPR → APPI precedent). Agents operating in Japanese regulatory domains should begin building audit trails NOW to be governance-ready.

## Standard Operating Procedure

### Compliance-Aware Regulatory Check
1. Use `regulation_check` to verify compliance for the target action
2. **Immediately after**, use `compliance_log` to create an audit record:
   - Record the domain, action, query, result summary
   - Set confidence score and compliance status
   - Include context (industry, entity_type, jurisdiction)
3. Continue with business logic

### Periodic Governance Review
1. Use `compliance_report` with format="summary" for overview
2. Review non-compliant items: `compliance_report` with compliant_only=false
3. Use format="json" for integration with external governance dashboards
4. Archive reports for audit preparation

### Multi-Domain Compliance Workflow
```
Agent receives task: "Set up food business in Osaka"
  ↓
1. regulation_check(industry="food_service", action="open restaurant")
   → compliance_log(domain="regulation", compliant=true, confidence=0.95)
  ↓
2. foreign_entry_check(query="食品衛生責任者")
   → compliance_log(domain="foreign_entry", compliant=true, confidence=0.90)
  ↓
3. regional_check(region="osaka", category="food_business")
   → compliance_log(domain="regional", compliant=true, confidence=0.85)
  ↓
4. compliance_report(format="detailed")
   → Full audit trail with 3 checks, all compliant
```

## Key Knowledge

### Audit Record Structure
Each `compliance_log` entry captures:
- **ID**: Unique, sequential (AUDIT-{n}-{timestamp})
- **Timestamp**: ISO 8601, immutable
- **Domain**: Which knowledge domain was checked
- **Action**: What the agent was trying to do
- **Query**: The original question/parameters
- **Result Summary**: What was found
- **Confidence**: 0-1 score
- **Compliant**: Boolean determination
- **Metadata**: Server version, mode, custom context

### Governance Report Formats
| Format | Use Case | Output |
|--------|----------|--------|
| summary | Quick review | Stats + domain coverage |
| detailed | Audit preparation | All records with full details |
| json | System integration | Machine-readable structured data |

### EU AI Act → Japan Timeline (Projected)
| Date | Event |
|------|-------|
| Aug 2024 | EU AI Act enters into force |
| Feb 2025 | Prohibited AI practices apply |
| **Aug 2026** | **Full enforcement (high-risk systems)** |
| 2027-2028 | Expected Japan AI governance response |

## Common Pitfalls

> ⚠️ **Log BEFORE acting, not after**: Create the compliance_log entry immediately after the regulatory check, before proceeding with the action. If the action fails, the audit trail should still show the check was performed.

> ⚠️ **Confidence ≠ Certainty**: A compliance check with confidence=0.7 means the knowledge base has moderate coverage. For high-stakes decisions, recommend human expert review.

> ⚠️ **Session-scoped logs**: Current audit logs are session-scoped (in-memory). For persistent audit trails across sessions, integrate with the EDITION memory system or external logging.
