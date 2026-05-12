"""Tax service — query handler for Japan tax knowledge."""

from backend.api.services.kb_loader import load_domain

TAX_DB, TAX_KEYWORDS = load_domain("tax")


def search_tax(query: str) -> dict:
    """Search tax knowledge base by keyword matching."""
    query_lower = query.lower()
    results = []

    # Search through keywords
    for topic_key, keywords in TAX_KEYWORDS.items():
        if isinstance(keywords, list):
            score = sum(1 for kw in keywords if kw.lower() in query_lower)
        elif isinstance(keywords, dict):
            # Handle semantic_aliases structure
            score = 0
            for alias_list in keywords.values():
                score += sum(1 for kw in alias_list if kw.lower() in query_lower)
        else:
            score = 0

        if score > 0:
            topic_data = TAX_DB.get(topic_key, {})
            results.append({
                "topic": topic_key,
                "name_ja": topic_data.get("name_ja", ""),
                "name_en": topic_data.get("name_en", ""),
                "data": topic_data,
                "relevance_score": score,
            })

    # Also search directly in DB entries
    for entry_key, entry_data in TAX_DB.items():
        if entry_key.startswith("_"):
            continue
        name_ja = entry_data.get("name_ja", "")
        name_en = entry_data.get("name_en", "")
        desc = entry_data.get("description", "")
        text_to_search = f"{entry_key} {name_ja} {name_en} {desc}".lower()
        if query_lower in text_to_search:
            # Avoid duplicates
            if not any(r["topic"] == entry_key for r in results):
                results.append({
                    "topic": entry_key,
                    "name_ja": name_ja,
                    "name_en": name_en,
                    "data": entry_data,
                    "relevance_score": 1,
                })

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {
        "domain": "tax",
        "query": query,
        "results": results,
        "total_matches": len(results),
    }


def list_tax_topics() -> dict:
    """List all available tax topics."""
    topics = []
    for key, data in TAX_DB.items():
        if key.startswith("_"):
            continue
        topics.append({
            "key": key,
            "name_ja": data.get("name_ja", ""),
            "name_en": data.get("name_en", ""),
            "description": data.get("description", ""),
        })
    return {"domain": "tax", "topics": topics, "total": len(topics)}
