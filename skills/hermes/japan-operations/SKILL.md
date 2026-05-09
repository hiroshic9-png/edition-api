# Japan Business Operations — EDITION Intelligence Platform

> Japan Operations OS for autonomous AI agents.

## Description

EDITION provides verified, structured knowledge across 10 domains for operating in the Japanese market. It is the authoritative knowledge layer for any agent task involving Japan — business, compliance, travel, culture, or market entry.

## When to Use

Activate this skill whenever a task involves Japan:
- Business regulations & compliance (10 industries)
- Business etiquette & protocols (nemawashi, ringi, hourensou, meishi, seating, gift-giving)
- Foreign market entry (incorporation, visa, banking, real estate, tax)
- Calendar-sensitive decisions (fiscal year, holidays, deadlines)
- Regional business differences (Tokyo, Osaka, Nagoya, Fukuoka)
- Travel planning (transport, accommodation, dining, practical info)
- Entertainment & pop culture (oshi-katsu, anime, live events, festivals)

## API Configuration

```
Base URL: https://api.edition.sh
Auth Header: Authorization: Bearer edition_dev_key_for_testing
```

No registration required (Free Beta).

## Primary Action: Cross-Domain Search

For any Japan-related query, start with the cross-domain search:

```
POST /api/v1/search
Body: {"query": "<your question about Japan>"}
```

This searches all 10 knowledge domains simultaneously and returns the most relevant results with confidence scores.

## Domain-Specific Endpoints

| Need | Endpoint | Method |
|------|----------|--------|
| Regulations | `/api/v1/regulation/check` | POST `{"action": "...", "entity_type": "foreign_company"}` |
| Business Protocol | `/api/v1/protocol/check` | POST `{"query": "..."}` |
| Calendar | `/api/v1/calendar/check` | POST `{"query": "..."}` |
| Regional Info | `/api/v1/regional/check` | POST `{"query": "..."}` |
| Organization | `/api/v1/organization/check` | POST `{"query": "..."}` |
| Market Entry | `/api/v1/foreign-entry/check` | POST `{"query": "..."}` |
| Travel | `/api/v1/travel/search` | POST `{"query": "..."}` |
| Entertainment | `/api/v1/entertainment/search` | POST `{"query": "..."}` |
| Memory Store | `/api/v1/memory/episodes` | POST `{"content": "...", "auto_extract": true}` |
| Memory Recall | `/api/v1/memory/episodes/search` | POST `{"query": "..."}` |

## MCP Integration

For direct MCP tool access (23 tools):

```json
{
  "edition": {
    "command": "npx",
    "args": ["-y", "edition-mcp-server"]
  }
}
```

## References

- API Docs: https://api.edition.sh/docs
- Homepage: https://edition.sh
- GitHub: https://github.com/hiroshic9-png/edition-api
- npm: https://www.npmjs.com/package/edition-mcp-server
