"""Daily life service — query handler for Japan daily life knowledge."""

from ..services.daily_life_kb import DAILY_LIFE_DB, DAILY_LIFE_KEYWORDS


def search_daily_life(query: str) -> dict:
    """Search daily life knowledge base by keyword matching."""
    query_lower = query.lower()
    results = []

    for topic_key, keywords in DAILY_LIFE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in query_lower)
        if score > 0:
            topic_data = DAILY_LIFE_DB.get(topic_key, {})
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
        "domain": "daily_life",
        "query": query,
        "results": results,
        "total_matches": len(results),
    }


def list_daily_life_topics() -> dict:
    """List all available daily life topics."""
    topics = []
    for key, data in DAILY_LIFE_DB.items():
        topics.append({
            "key": key,
            "name_ja": data.get("name_ja", ""),
            "name_en": data.get("name_en", ""),
            "category": data.get("category", ""),
            "summary": data.get("summary", ""),
        })
    return {"domain": "daily_life", "topics": topics, "total": len(topics)}
