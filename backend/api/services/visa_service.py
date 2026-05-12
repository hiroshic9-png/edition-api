"""Visa & Immigration service — query handler for Japan visa/immigration knowledge."""

from backend.api.services.kb_loader import load_domain

VISA_DB, VISA_KEYWORDS = load_domain("visa_immigration")


def search_visa(query: str) -> dict:
    """Search visa/immigration knowledge base."""
    query_lower = query.lower()
    results = []

    for topic_key, keywords in VISA_KEYWORDS.items():
        if isinstance(keywords, list):
            score = sum(1 for kw in keywords if kw.lower() in query_lower)
        elif isinstance(keywords, dict):
            score = 0
            for alias_list in keywords.values():
                score += sum(1 for kw in alias_list if kw.lower() in query_lower)
        else:
            score = 0
        if score > 0:
            topic_data = VISA_DB.get(topic_key, {})
            results.append({
                "topic": topic_key,
                "name_ja": topic_data.get("name_ja", ""),
                "name_en": topic_data.get("name_en", ""),
                "data": topic_data,
                "relevance_score": score,
            })

    for entry_key, entry_data in VISA_DB.items():
        if entry_key.startswith("_"):
            continue
        name_ja = entry_data.get("name_ja", "")
        name_en = entry_data.get("name_en", "")
        desc = entry_data.get("description", "")
        text = f"{entry_key} {name_ja} {name_en} {desc}".lower()
        if query_lower in text and not any(r["topic"] == entry_key for r in results):
            results.append({
                "topic": entry_key,
                "name_ja": name_ja,
                "name_en": name_en,
                "data": entry_data,
                "relevance_score": 1,
            })

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {"domain": "visa_immigration", "query": query, "results": results, "total_matches": len(results)}


def list_visa_topics() -> dict:
    """List all visa/immigration topics."""
    topics = []
    for key, data in VISA_DB.items():
        if key.startswith("_"):
            continue
        topics.append({
            "key": key,
            "name_ja": data.get("name_ja", ""),
            "name_en": data.get("name_en", ""),
            "description": data.get("description", ""),
        })
    return {"domain": "visa_immigration", "topics": topics, "total": len(topics)}
