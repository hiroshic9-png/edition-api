# EDITION API Reference

## Base URL
```
https://api.edition.sh
```

## Authentication
All requests require:
```
Authorization: Bearer edition_dev_key_for_testing
Content-Type: application/json
```

## Endpoints

### Cross-Domain Search
```
POST /api/v1/search
{"query": "opening a restaurant in Osaka"}
```
Response: Matches from all 10 domains with confidence scores.

### Regulation Check
```
POST /api/v1/regulation/check
{"action": "open a restaurant in Tokyo", "entity_type": "foreign_company"}
```
entity_type options: "foreign_company", "domestic_company", "individual", "tourist"

### Business Protocol
```
POST /api/v1/protocol/check
{"query": "nemawashi"}
```
Available protocols: nemawashi, ringi, hourensou, meishi_koukan, sekijun, zoutou

### Calendar
```
POST /api/v1/calendar/check
{"query": "tax filing deadline"}
```
Categories: holidays, fiscal_year, gift_seasons, admin_deadlines, seasonal_business

### Regional
```
POST /api/v1/regional/check
{"query": "Osaka business culture"}
```

### Organization
```
POST /api/v1/organization/check
{"query": "payment terms in Japan"}
```

### Foreign Entry
```
POST /api/v1/foreign-entry/check
{"query": "management visa requirements"}
```
Categories: incorporation, visa, banking, real_estate, tax_registration

### Travel
```
POST /api/v1/travel/search
{"query": "shinkansen tips"}
```

### Entertainment
```
POST /api/v1/entertainment/search
{"query": "oshi-katsu ticket buying"}
```

### Memory
```
# Store episode
POST /api/v1/memory/episodes
{"content": "Meeting with Tanaka-san went well", "auto_extract": true}

# Search memories
POST /api/v1/memory/episodes/search
{"query": "what happened with Tanaka"}

# Get facts
GET /api/v1/memory/facts?valid_only=true

# Get context summary
GET /api/v1/memory/context
```

## List Endpoints (GET, no body required)
- `/api/v1/regulation/industries`
- `/api/v1/regulation/tourist`
- `/api/v1/protocol/list`
- `/api/v1/calendar/list`
- `/api/v1/regional/list`
- `/api/v1/organization/list`
- `/api/v1/foreign-entry/list`
- `/api/v1/travel/list`
- `/api/v1/entertainment/list`
