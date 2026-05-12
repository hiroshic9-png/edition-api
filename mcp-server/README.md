# EDITION Intelligence Platform — MCP Server

Japan Operations OS for autonomous AI agents. 20 knowledge domains, 43 MCP tools, 2 prompt templates — verified, structured intelligence for agents operating in Japan.

[![npm](https://img.shields.io/npm/v/edition-mcp-server)](https://www.npmjs.com/package/edition-mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
npx edition-mcp-server
```

Or install globally:

```bash
npm install -g edition-mcp-server
edition-mcp
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "edition": {
      "command": "npx",
      "args": ["-y", "edition-mcp-server"]
    }
  }
}
```

### Cursor / Windsurf / VS Code

Add to your MCP settings:

```json
{
  "edition": {
    "command": "npx",
    "args": ["-y", "edition-mcp-server"]
  }
}
```

### Custom API URL

By default connects to `https://api.edition.sh`. Override with environment variables:

```json
{
  "edition": {
    "command": "npx",
    "args": ["-y", "edition-mcp-server"],
    "env": {
      "EDITION_API_URL": "https://api.edition.sh",
      "EDITION_API_KEY": "edition_dev_key_for_testing"
    }
  }
}
```

## Tools

### Memory (5 tools)

| Tool | Description |
|------|-------------|
| `memory_store` | Store episodes to persistent memory with Japanese language understanding (keigo, subject omission, implicit context) |
| `memory_recall` | Semantic search across stored memories — handles ambiguous Japanese queries |
| `memory_facts` | List structured facts as subject → predicate → object triples with confidence scores |
| `memory_context` | Get current session context summary for prompt injection |
| `memory_extract` | Auto-extract structured facts from text with keigo/hierarchy analysis |

### Regulations (3 tools)

| Tool | Description |
|------|-------------|
| `regulation_check` | Check Japan business regulations — licenses, governing bodies, penalties, costs, timelines for 10 industries |
| `regulation_industries` | List all 10 regulated industries with their requirements |
| `regulation_tourist` | Tourist/visitor regulation categories (visa, tax-free, transport, accommodation, medical, manners) |

### Protocols (2 tools)

| Tool | Description |
|------|-------------|
| `protocol_check` | Search Japanese business protocols — nemawashi, ringi, hourensou, meishi exchange, seating order, gift-giving |
| `protocol_list` | List all business protocols with importance levels |

### Calendar (2 tools)

| Tool | Description |
|------|-------------|
| `calendar_check` | Search Japan business calendar — fiscal year, holidays, gift seasons, deadlines, seasonal patterns |
| `calendar_list` | List all calendar categories |

### Regional (2 tools)

| Tool | Description |
|------|-------------|
| `regional_check` | Search regional business differences — city characteristics, subsidies, local regulations, business customs |
| `regional_list` | List all regional categories |

### Organization (2 tools)

| Tool | Description |
|------|-------------|
| `organization_check` | Search organizational structures — keiretsu, corporate hierarchy, payment customs, contract practices |
| `organization_list` | List all organization categories |

### Foreign Entry (2 tools)

| Tool | Description |
|------|-------------|
| `foreign_entry_check` | Japan market entry guides — incorporation (KK/GK), management visa, bank account, real estate, tax registration, employee hiring (labor law, dismissal rules) |
| `foreign_entry_list` | List all foreign entry categories |

### Travel (2 tools)

| Tool | Description |
|------|-------------|
| `travel_search` | Search Japan travel knowledge — shinkansen, IC cards, ryokan etiquette, tipping culture |
| `travel_list` | List all travel topics |

### Entertainment (2 tools)

| Tool | Description |
|------|-------------|
| `entertainment_search` | Search Japan entertainment — oshi-katsu fan culture, anime pilgrimage, live events, seasonal festivals |
| `entertainment_list` | List all entertainment topics |

### Daily Life (2 tools)

| Tool | Description |
|------|-------------|
| `daily_life_search` | Search daily life in Japan — postal/address system, garbage sorting, utilities, healthcare/insurance |
| `daily_life_list` | List all daily life topics |

### Language (2 tools)

| Tool | Description |
|------|-------------|
| `language_search` | Search Japanese language structures — keigo system, counter words (josushi), name patterns, business templates |
| `language_list` | List all language topics |

### Food Culture (2 tools)

| Tool | Description |
|------|-------------|
| `food_search` | Search Japan food culture — dining etiquette, cuisine types, restaurant navigation, dietary restrictions (halal, vegetarian) |
| `food_list` | List all food culture topics |

### Disaster & Safety (2 tools)

| Tool | Description |
|------|-------------|
| `disaster_search` | Search disaster/safety knowledge — earthquake shindo scale, typhoon warnings, emergency contacts (110/119), disaster preparedness |
| `disaster_list` | List all disaster & safety topics |

### Cross-Domain (1 tool)

| Tool | Description |
|------|-------------|
| `search` | Cross-domain search across all 20 knowledge domains simultaneously — one query returns matches from all domains |

## Prompt Templates

| Prompt | Description |
|--------|-------------|
| `japan_business_briefing` | Generate a comprehensive Japan business briefing for a specific industry |
| `japan_travel_guide` | Generate a practical travel guide for a specific Japan destination |

## Resources

| Resource | Description |
|----------|-------------|
| `edition://domains` | List of all 20 knowledge domains with descriptions and endpoint information |
| `edition://quality` | Trust Anchor quality scores for each domain — verified data coverage metrics |

## Architecture

EDITION uses a three-layer knowledge architecture:

1. **Rules** — Official regulations, procedures, and requirements
2. **Context** — Unwritten rules, cultural "why", and implicit expectations
3. **Experience** — How to turn correct execution into relationship-building moments

## API

- **REST API**: [https://api.edition.sh](https://api.edition.sh)
- **API Docs**: [https://api.edition.sh/docs](https://api.edition.sh/docs)
- **Landing Page**: [https://edition.sh](https://edition.sh)

## License

MIT
