# EDITION Intelligence Platform

[![Glama Score](https://glama.ai/mcp/servers/hiroshic9-png/edition-api/badge)](https://glama.ai/mcp/servers/hiroshic9-png/edition-api)
[![npm](https://img.shields.io/npm/v/edition-mcp-server)](https://www.npmjs.com/package/edition-mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Japan Operations OS for autonomous AI agents.**

14 knowledge domains · 31 MCP tools · 55+ REST endpoints · 2 prompts · 2 resources
Verified ground truth for operating in the Japanese market.

> **Production API:** [api.edition.sh](https://api.edition.sh) — Free beta, no registration required.
>
> **Interactive Demo:** [Tourist Agent Demo](https://hiroshic9-png.github.io/edition-api/demo.html) — Watch 6 domains work together in real-time.

---

## Why EDITION?

AI agents working in Japan hit walls that generic LLMs can't solve:

| Challenge | What goes wrong |
|-----------|----------------|
| **Keigo (敬語)** | 「お持ちすれば喜ばれるかと存じます」 — hidden subject, layered honorifics, uncertainty expression. Generic NLP treats this as noise. |
| **Implicit agreements** | Japanese business communication rarely states things directly. Agents need cultural decoding. |
| **Regulatory maze** | 10+ industries with overlapping national/prefectural regulations, most documentation only in Japanese. |
| **Procedural complexity** | Company incorporation, visa, banking — each requires 5-8 steps with specific documents, deadlines, and costs. |

**EDITION provides verified, structured intelligence** that agents can use as ground truth instead of hallucinating cultural nuances, legal requirements, and procedural details.

---

## 14 Knowledge Domains

| # | Domain | Tools | What it covers |
|---|--------|-------|----------------|
| 1 | **Memory** | `memory_store` `memory_recall` `memory_facts` `memory_context` `memory_extract` | Three-layer persistent memory (Episode/Fact/Context) with Japanese keigo analysis and social hierarchy detection |
| 2 | **Regulation** | `regulation_check` `regulation_industries` `regulation_tourist` | 10 industries (food, real estate, finance, healthcare, construction, education, transport, retail, IT, manufacturing) + tourist compliance |
| 3 | **Protocol** | `protocol_check` `protocol_list` | Nemawashi, ringi, hourensou, meishi koukan, sekijun, zoutou — step-by-step procedures with cultural context |
| 4 | **Calendar** | `calendar_check` `calendar_list` | Fiscal year (April start), Golden Week, Obon, year-end, gift seasons, administrative deadlines |
| 5 | **Regional** | `regional_check` `regional_list` | Tokyo vs Osaka negotiation styles, local subsidies, prefectural regulations, dialect considerations |
| 6 | **Organization** | `organization_check` `organization_list` | Keiretsu networks, corporate hierarchy (bucho/kacho), payment customs (net-60), contract practices |
| 7 | **Foreign Entry** | `foreign_entry_check` `foreign_entry_list` | 6 categories: company incorporation (KK/GK), management visa, bank account, real estate, tax registration, employee hiring |
| 8 | **Travel** | `travel_search` `travel_list` | Shinkansen, IC cards, ryokan etiquette, onsen rules, restaurant ordering, tipping customs |
| 9 | **Entertainment** | `entertainment_search` `entertainment_list` | Oshi-katsu fan culture, anime pilgrimage, live event manners, seasonal festivals |
| 10 | **Daily Life** | `daily_life_search` `daily_life_list` | Postal/address systems, garbage sorting by municipality, utilities (electricity/gas/water/NHK), healthcare navigation |
| 11 | **Language** | `language_search` `language_list` | Keigo honorific system, counter words (josushi), name/address structure, business Japanese templates |
| 12 | **Food Culture** | `food_search` `food_list` | Dining etiquette, cuisine classification, restaurant navigation (shokkenki, izakaya, sushi counter), dietary restrictions (halal, vegetarian, allergies) |
| 13 | **Disaster & Safety** | `disaster_search` `disaster_list` | Earthquake shindo scale & EEW, typhoon warning levels, emergency contacts (110/119/118), preparedness checklists |
| 14 | **Cross-Domain** | `search` | Search all 14 domains simultaneously with a single query |

---

## Quick Start

### Option 1: npx (Recommended for Claude Desktop / Cursor)

```bash
npx -y edition-mcp-server
```

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "edition": {
      "command": "npx",
      "args": ["-y", "edition-mcp-server"],
      "env": {
        "EDITION_API_URL": "https://api.edition.sh",
        "EDITION_API_KEY": "edition_dev_key_for_testing"
      }
    }
  }
}
```

### Option 2: Smithery

```bash
npx -y smithery mcp add hiroshi-c9/edition
```

### Option 3: REST API (Direct)

```bash
# Cross-domain search
curl -X POST https://api.edition.sh/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I start a tech company in Tokyo?"}'

# Regulation check
curl -X POST https://api.edition.sh/api/v1/regulation/check \
  -d '{"action": "open restaurant", "industry": "food_service"}'

# Business protocol
curl -X POST https://api.edition.sh/api/v1/protocol/check \
  -d '{"query": "nemawashi consensus building"}'
```

---

## Memory API — Japanese-aware Persistent Memory

Store episodes, auto-extract structured facts with **keigo analysis, social hierarchy detection, and confidence scoring**.

```
Input:  "佐藤部長にはワインをお持ちすれば喜ばれるかと存じます"

Output:
  Subject:    佐藤 (役職: 部長)
  Predicate:  好む
  Object:     ワイン
  Keigo:      Level 2 (尊敬語)
  Hierarchy:  superior
  Confidence: 0.7 (推測 — not stated as fact)
  Tense:      present
```

Three-layer architecture:
- **Episodes** — raw conversation logs
- **Facts** — structured knowledge (subject→predicate→object triples)
- **Context** — aggregated session summaries per entity/topic

## MCP Capabilities

| Category | Count | Details |
|----------|-------|---------|
| **Tools** | 31 | All with annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`) |
| **Resources** | 2 | `edition://domains` (domain catalog), `edition://quality` (trust scores) |
| **Prompts** | 2 | `japan_business_briefing` (by industry), `japan_travel_guide` (by destination) |

## API Endpoints

### Memory
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/memory/episodes` | Store episode (`auto_extract=true` for auto fact extraction) |
| POST | `/api/v1/memory/recall` | Semantic search across episodes |
| GET | `/api/v1/memory/facts` | List structured facts |
| GET | `/api/v1/memory/context` | Session context summary |
| POST | `/api/v1/memory/extract` | Extract facts from text (`store=true` to persist) |

### Regulation & Compliance
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/regulation/check` | Check regulations (10 industries + tourist) |
| GET | `/api/v1/regulation/industries` | List all regulated industries |
| GET | `/api/v1/regulation/tourist` | Tourist regulation categories |

### Business Intelligence
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/protocol/check` | Search business protocols |
| GET | `/api/v1/protocol/list` | List all protocols |
| POST | `/api/v1/calendar/check` | Search business calendar |
| GET | `/api/v1/calendar/list` | List calendar categories |
| POST | `/api/v1/regional/check` | Search regional differences |
| GET | `/api/v1/regional/list` | List regional categories |
| POST | `/api/v1/organization/check` | Search organizational structures |
| GET | `/api/v1/organization/list` | List organization categories |

### Market Entry
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/foreign-entry/check` | Foreign market entry guides |
| GET | `/api/v1/foreign-entry/list` | List entry categories (6 total) |

### Lifestyle & Culture
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/travel/search` | Travel intelligence |
| POST | `/api/v1/entertainment/search` | Entertainment & pop culture |
| POST | `/api/v1/daily-life/search` | Daily life knowledge |
| POST | `/api/v1/language/search` | Japanese language |
| POST | `/api/v1/food/search` | Food culture |
| POST | `/api/v1/disaster/search` | Disaster & safety |

### Cross-Domain
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/search` | Search all 14 domains simultaneously |

---

## Data Quality

All knowledge entries include:
- **`source_url`** — Link to authoritative source (government websites, official organizations)
- **`last_verified`** — Date of last verification
- **`confidence`** — Verification status (`verified` / `estimated`)
- **`version`** — Entry version with changelog

Sources include: 厚生労働省 (MHLW), 国税庁 (NTA), 法務省 (MOJ), 国土交通省 (MLIT), 経済産業省 (METI), 日本経団連 (Keidanren), JETRO, 入管庁 (ISA).

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI (Python) |
| Memory Store | SQLite + ChromaDB (vector search) |
| MCP Server | TypeScript (MCP SDK v1.12+) |
| LLM | Gemini / Claude / GPT (fact extraction) |
| Hosting | Render (api.edition.sh) |

## Agent Discovery

| Protocol | Endpoint |
|----------|----------|
| MCP (Streamable HTTP) | `POST https://api.edition.sh/mcp` |
| A2A Agent Card | `GET https://api.edition.sh/.well-known/agent.json` |
| MCP Server Card | `GET https://api.edition.sh/.well-known/mcp/server-card.json` |
| OpenAPI / Swagger | `GET https://api.edition.sh/docs` |

## Agent Harness Compatible

EDITION is designed as a **Tool Registry / Japan Knowledge Layer** for agent harnesses. All 31 tools include MCP annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`), usage guidelines, and behavioral transparency metadata — enabling harness frameworks to auto-discover, evaluate, and integrate EDITION tools without manual configuration.

## Registries

| Registry | Status |
|----------|--------|
| [npm](https://www.npmjs.com/package/edition-mcp-server) | ✅ Published (v0.2.4) |
| [Smithery](https://smithery.ai/server/@hiroshi-c9/edition) | ✅ Listed (31 tools) |
| [Glama](https://glama.ai/mcp/servers/hiroshic9-png/edition-api) | ✅ Grade A Coherence |

## Why Not Mem0 / Letta / Zep?

Those are excellent general-purpose memory tools. But they don't:
- Parse Japanese keigo levels (丁寧語 / 尊敬語 / 謙譲語)
- Detect implicit social hierarchy from honorific patterns
- Score confidence based on Japanese speech patterns (断定 vs 推測 vs 伝聞)
- Include a Japanese regulatory database with 14 knowledge domains

**Japanese business context is structurally different.** Agents need purpose-built infrastructure to navigate it.

## License

MIT
