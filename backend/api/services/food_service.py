"""Food culture service — query handler for food knowledge."""

from backend.api.services.kb_loader import load_domain

FOOD_DB, FOOD_KEYWORDS = load_domain("food")


def search_food(query: str) -> dict:
    """Search food culture knowledge base by keyword matching."""
    query_lower = query.lower()
    results = []

    for topic_key, keywords in FOOD_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in query_lower)
        if score > 0:
            topic_data = FOOD_DB.get(topic_key, {})
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
        "domain": "food",
        "query": query,
        "results": results,
        "total_matches": len(results),
    }


def list_food_topics() -> dict:
    """List all available food culture topics."""
    topics = []
    for key, data in FOOD_DB.items():
        topics.append({
            "key": key,
            "name_ja": data.get("name_ja", ""),
            "name_en": data.get("name_en", ""),
            "category": data.get("category", ""),
            "summary": data.get("summary", ""),
        })
    return {"domain": "food", "topics": topics, "total": len(topics)}
