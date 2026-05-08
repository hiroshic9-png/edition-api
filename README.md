# EDITION Intelligence Platform

**The missing infrastructure for AI agents operating in Japan.**

Memory API + Regulation Check API + Procedural Knowledge + MCP Server — purpose-built for Japanese business context.

---

## The Problem

AI agents working with Japanese businesses hit walls that generic tools can't solve:

- **Keigo (敬語)**: A sentence like _"ワインをお持ちすれば喜ばれるかと存じます"_ hides the subject, uses layered honorifics, and expresses uncertainty — generic NLP treats this as noise
- **Implicit agreements**: Japanese business communication rarely states things directly
- **Regulatory maze**: 10+ industries with overlapping national/prefectural regulations, most documentation only in Japanese
- **No persistent context**: Agents forget everything between sessions

## What This Does

### 1. Memory API — Japanese-aware persistent memory

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
- **Facts** — structured knowledge (auto-extracted via LLM)
- **Context** — summarized state per entity/topic

### 2. Regulation API — 10 industries + tourist rules

Pre-built regulatory database covering:
- EC sites, Real estate, Staffing, Food service, Construction
- Healthcare, Finance, Transport, Education, Accommodation
- Tourist categories: Visa, Tax-free, Transit, Medical, Manners

**6 industries include step-by-step procedural guides** (39 total steps) — covering what to do, how, where, required documents, costs, timelines, and common pitfalls.

```bash
curl -X POST /api/v1/regulation/check \
  -d '{"industry": "food_service", "query": "What licenses do I need to open a restaurant in Tokyo?"}'
```

### 3. MCP Server — 8 tools for Claude, Cursor, etc.

| Tool | Description |
|------|-------------|
| `memory_store` | Store episode + auto-extract facts |
| `memory_recall` | Semantic search across episodes |
| `memory_facts` | List structured facts |
| `memory_context` | Get context summary |
| `memory_extract` | Extract facts from text |
| `regulation_check` | Check regulations by industry |
| `regulation_industries` | List covered industries |
| `regulation_tourist` | Tourist regulation lookup |

## Quick Start

### Backend

```bash
git clone https://github.com/hiroshic9-png/edition.git
cd edition
python3 -m venv venv && source venv/bin/activate
pip install fastapi 'uvicorn[standard]' pydantic sqlalchemy aiosqlite chromadb python-dotenv google-genai

# Set your LLM key (any one of these)
echo 'GEMINI_API_KEY=your_key' > .env
# or ANTHROPIC_API_KEY or OPENAI_API_KEY

python -m uvicorn backend.api.main:app --reload
# → http://localhost:8000/docs
```

### MCP Server (for Claude Desktop / Cursor)

```bash
cd mcp-server && npm install && npm run build && npm start
```

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "edition": {
      "command": "node",
      "args": ["/path/to/mcp-server/dist/index.js"],
      "env": {
        "EDITION_API_URL": "http://localhost:8000",
        "EDITION_API_KEY": "your_api_key"
      }
    }
  }
}
```

## API Endpoints

### Memory
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/memory/episodes` | Store episode (set `auto_extract=true` for auto fact extraction) |
| POST | `/api/v1/memory/episodes/search` | Semantic search |
| POST | `/api/v1/memory/facts` | Add fact |
| GET | `/api/v1/memory/facts` | List facts |
| GET | `/api/v1/memory/context` | Context summary |
| POST | `/api/v1/memory/extract` | Extract facts from text |

### Regulation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/regulation/check` | Check regulations (10 industries + LLM RAG) |
| GET | `/api/v1/regulation/industries` | List industries |
| GET | `/api/v1/regulation/tourist` | Tourist categories |

## Tech Stack

| Layer | Technology |
|-------|-----------| 
| API | FastAPI (Python) |
| Memory Store | SQLite + ChromaDB (vector search) |
| MCP | TypeScript SDK v1.29 |
| LLM | Gemini / Claude / GPT (fact extraction + RAG) |

## Why Not Mem0 / Letta / Zep?

Those are excellent general-purpose memory tools. But they don't:
- Parse Japanese keigo levels (丁寧語 / 尊敬語 / 謙譲語)
- Detect implicit social hierarchy from honorific patterns
- Score confidence based on Japanese speech patterns (断定 vs 推測 vs 伝聞)
- Include a Japanese regulatory database

This project exists because **Japanese business context is structurally different**, and agents need purpose-built infrastructure to navigate it.

## License

MIT
