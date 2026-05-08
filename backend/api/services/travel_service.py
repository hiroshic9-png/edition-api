"""Travel intelligence service — query handler for Japan travel knowledge."""

from ..services.travel_kb import TRAVEL_DB, TRAVEL_KEYWORDS


def search_travel(query: str) -> dict:
    """Search travel knowledge base by keyword matching."""
    query_lower = query.lower()
    results = []

    for topic_key, keywords in TRAVEL_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in query_lower)
        if score > 0:
            topic_data = TRAVEL_DB.get(topic_key, {})
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
        "domain": "travel",
        "query": query,
        "results": results,
        "total_matches": len(results),
    }


def list_travel_topics() -> dict:
    """List all available travel topics."""
    topics = []
    for key, data in TRAVEL_DB.items():
        topics.append({
            "key": key,
            "name_ja": data.get("name_ja", ""),
            "name_en": data.get("name_en", ""),
            "category": data.get("category", ""),
            "summary": data.get("summary", ""),
        })
    return {"domain": "travel", "topics": topics, "total": len(topics)}
