# edition-mcp-server

MCP server for the **EDITION Intelligence Platform** — contextual intelligence infrastructure for AI agents operating in Japan.

## What it does

Provides 8 tools that give AI agents the ability to:

- **Remember** conversations with Japanese-aware fact extraction (keigo analysis, social hierarchy detection, confidence scoring)
- **Navigate** Japanese business regulations across 10 industries + tourist rules

## Install

```bash
npx edition-mcp-server
```

Or install globally:

```bash
npm install -g edition-mcp-server
edition-mcp
```

## Configure

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "edition": {
      "command": "npx",
      "args": ["-y", "edition-mcp-server"],
      "env": {
        "EDITION_API_URL": "http://localhost:8000",
        "EDITION_API_KEY": "your_api_key"
      }
    }
  }
}
```

### Cursor

Add to MCP settings:

```json
{
  "edition": {
    "command": "npx",
    "args": ["-y", "edition-mcp-server"],
    "env": {
      "EDITION_API_URL": "http://localhost:8000",
      "EDITION_API_KEY": "your_api_key"
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `memory_store` | Store episode + auto-extract structured facts from Japanese text |
| `memory_recall` | Semantic search across stored episodes |
| `memory_facts` | List structured facts (subject → predicate → object with confidence) |
| `memory_context` | Get context summary for an entity or session |
| `memory_extract` | Extract facts from text with keigo/hierarchy analysis |
| `regulation_check` | Check Japanese business regulations by industry |
| `regulation_industries` | List all 10 supported industries |
| `regulation_tourist` | Tourist regulation lookup (visa, tax-free, transit, etc.) |

## Backend

This MCP server connects to the EDITION REST API backend. To run your own:

```bash
git clone https://github.com/hiroshic9-png/edition.git
cd edition
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.api.main:app --reload
```

## License

MIT
