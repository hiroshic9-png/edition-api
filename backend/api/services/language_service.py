"""Japanese language service — query handler for language knowledge."""

from backend.api.services.kb_loader import load_domain

LANGUAGE_DB, LANGUAGE_KEYWORDS = load_domain("language")


def search_language(query: str) -> dict:
    """Search language knowledge base by keyword matching."""
    query_lower = query.lower()
    results = []

    for topic_key, keywords in LANGUAGE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in query_lower)
        if score > 0:
            topic_data = LANGUAGE_DB.get(topic_key, {})
            results.append({
                "topic": topic_key,
                "name_ja": topic_data.get("name_ja", ""),
                "name_en": topic_data.get("name_en", ""),
                "summary": topic_data.get("summary", ""),
                "data": topic_data,
                "relevance_score": score,
            })

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {
        "domain": "language",
        "query": query,
        "results": results,
        "total_matches": len(results),
    }


def list_language_topics() -> dict:
    """List all available language topics."""
    topics = []
    for key, data in LANGUAGE_DB.items():
        topics.append({
            "key": key,
            "name_ja": data.get("name_ja", ""),
            "name_en": data.get("name_en", ""),
            "category": data.get("category", ""),
            "summary": data.get("summary", ""),
        })
    return {"domain": "language", "topics": topics, "total": len(topics)}
