# EDITION Intelligence Platform — Terms of Service

**Effective Date**: May 12, 2026
**Last Updated**: May 12, 2026

---

## 1. Service Overview

EDITION Intelligence Platform ("the Service") provides structured knowledge about operating in Japan via REST API and MCP (Model Context Protocol) interfaces. The Service is operated by EDITION ("we", "us").

## 2. API Key & Access

- A valid API key is required for authenticated access.
- Free API keys are available via `POST /api/v1/auth/register`.
- You are responsible for keeping your API key confidential.
- One account per individual or organization.
- We reserve the right to revoke keys that violate these terms.

## 3. Plans & Usage Limits

| Plan | Daily Requests | Rate Limit | Domains |
|------|---------------|------------|---------|
| Free | 100/day | 10/min | 8 core domains |
| Pro | 10,000/day | 100/min | All 20 domains |
| Enterprise | Unlimited | Custom | All + SLA |

## 4. Acceptable Use

You may NOT:
- Use the Service for unlawful purposes
- Attempt to circumvent rate limits or access controls
- Resell or redistribute raw API responses without attribution
- Use automated tools to scrape the entire knowledge base

You MAY:
- Use API responses in your products, applications, and AI agents
- Cache responses for reasonable periods (up to 24 hours)
- Reference EDITION as a data source in your outputs

## 5. Data Collection & Analytics

> **Important**: By using the Service, you consent to the following data practices.

### 5.1 What We Collect
- API request metadata: endpoint, timestamp, response time, HTTP status
- Agent identification: user-agent string, inferred agent type
- Usage patterns: query frequency, domain distribution, tool invocation counts

### 5.2 What We Do NOT Collect
- Personal data beyond the email address used for registration
- Content of memory storage (encrypted and isolated per tenant)
- IP addresses (not logged or stored)

### 5.3 How We Use Collected Data
- **Service improvement**: Identify high-demand domains, optimize response quality
- **Aggregated analytics**: Anonymized, aggregated usage statistics may be analyzed to understand market trends in AI agent operations
- **Quality assurance**: Automated quality scoring and freshness monitoring

### 5.4 Data Sharing
- We do NOT sell individual usage data
- Anonymized, aggregated statistics may be published in research or reports
- We may share data with law enforcement if legally required

## 6. Disclaimer

THE SERVICE IS PROVIDED "AS IS". EDITION provides verified, structured knowledge but:
- **This is NOT legal, financial, medical, or tax advice.** Always consult qualified professionals.
- Information is verified against official sources but may become outdated.
- Quality scores and verification dates are provided for transparency.
- We are not liable for decisions made based on our data.

## 7. Service Level

- **Free/Pro**: Best-effort availability. No SLA.
- **Enterprise**: Custom SLA available upon request.
- We may perform maintenance with reasonable notice.

## 8. Changes to Terms

We may update these terms. Continued use after changes constitutes acceptance. Material changes will be communicated via API response headers.

## 9. Contact

- Email: h.sato@c-9.co.jp
- API: https://api.edition.sh
- GitHub: https://github.com/hiroshic9-png/edition-api

---

# EDITION インテリジェンスプラットフォーム — 利用規約

**施行日**: 2026年5月12日

## 1. サービス概要

EDITION Intelligence Platform（以下「本サービス」）は、日本での事業運営に関する構造化された知識をREST APIおよびMCPインターフェースで提供します。

## 2. データ収集・分析への同意

本サービスをご利用いただくことで、以下に同意いただいたものとみなします：
- APIリクエストのメタデータ（エンドポイント、タイムスタンプ、応答時間）の収集
- 匿名化・集計されたデータの分析利用（市場動向の把握、サービス品質向上）
- 個人情報（登録メールアドレス以外）は収集しません
- メモリストレージの内容はテナントごとに暗号化・隔離されています

## 3. 免責事項

本サービスは「現状のまま」提供されます。法的、財務的、医療的、税務的な助言ではありません。重要な判断については必ず専門家にご相談ください。
