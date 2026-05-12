"""Banking & Finance service — query handler for Japan banking/finance knowledge."""

from backend.api.services.kb_loader import load_domain

BANKING_DB, BANKING_KEYWORDS = load_domain("banking_finance")


def search_banking(query: str) -> dict:
    """Search banking/finance knowledge base."""
    query_lower = query.lower()
    results = []

    for topic_key, keywords in BANKING_KEYWORDS.items():
        if isinstance(keywords, list):
            score = sum(1 for kw in keywords if kw.lower() in query_lower)
        elif isinstance(keywords, dict):
            score = 0
            for alias_list in keywords.values():
                score += sum(1 for kw in alias_list if kw.lower() in query_lower)
        else:
            score = 0
        if score > 0:
            topic_data = BANKING_DB.get(topic_key, {})
            results.append({
                "topic": topic_key,
                "name_ja": topic_data.get("name_ja", ""),
                "name_en": topic_data.get("name_en", ""),
                "data": topic_data,
                "relevance_score": score,
            })

    for entry_key, entry_data in BANKING_DB.items():
        if entry_key.startswith("_"):
            continue
        text = f"{entry_key} {entry_data.get('name_ja', '')} {entry_data.get('name_en', '')} {entry_data.get('description', '')}".lower()
        if query_lower in text and not any(r["topic"] == entry_key for r in results):
            results.append({
                "topic": entry_key,
                "name_ja": entry_data.get("name_ja", ""),
                "name_en": entry_data.get("name_en", ""),
                "data": entry_data,
                "relevance_score": 1,
            })

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {"domain": "banking_finance", "query": query, "results": results, "total_matches": len(results)}


def list_banking_topics() -> dict:
    """List all banking/finance topics."""
    topics = []
    for key, data in BANKING_DB.items():
        if key.startswith("_"):
            continue
        topics.append({
            "key": key,
            "name_ja": data.get("name_ja", ""),
            "name_en": data.get("name_en", ""),
            "description": data.get("description", ""),
        })
    return {"domain": "banking_finance", "topics": topics, "total": len(topics)}
