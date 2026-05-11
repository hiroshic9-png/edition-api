# EDITION Japan Skills Pack

**Structured knowledge packs for AI agents operating in Japan.**

These Skills files follow the emerging MCP Skills primitive format — Markdown with YAML frontmatter that bundles domain-specific knowledge, standard operating procedures, and tool orchestration instructions.

## Available Skills

| Skill | Domains | Use Case |
|-------|---------|----------|
| [japan-market-entry](./japan-market-entry.md) | regulation, foreign_entry, organization | Foreign company entering Japan |
| [japan-business-ops](./japan-business-ops.md) | protocol, calendar, regional, language | Daily business operations |
| [japan-travel-guide](./japan-travel-guide.md) | travel, food, entertainment, disaster | Tourist/visitor assistance |
| [japan-daily-living](./japan-daily-living.md) | daily_life, food, language | Living in Japan as a foreigner |
| [japan-cultural-context](./japan-cultural-context.md) | protocol, organization, language | Cultural intelligence for agents |
| [japan-safety-compliance](./japan-safety-compliance.md) | disaster, regulation | Safety & regulatory compliance |

## How to Use

### With MCP-compatible agents
Point your agent to this directory. Skills-aware clients will automatically load relevant packs based on task context.

### With EDITION API
Each skill references specific EDITION tools. Connect to:
- **MCP**: `npx -y edition-mcp-server`
- **REST**: `https://api.edition.sh`

## Architecture

```
Agent Task → Skill Matcher → Load Relevant Skill Pack
                                    ↓
                          Read SOP + Key Knowledge
                                    ↓
                          Execute EDITION Tools
                                    ↓
                          Return Structured Response
```

## Quality

All knowledge is sourced from Japanese government agencies and verified institutions. Each skill file includes `source_authorities` in its frontmatter for traceability.
