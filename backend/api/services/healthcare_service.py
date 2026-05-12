"""Healthcare service — query handler for Japan healthcare knowledge."""
from backend.api.services.kb_loader import load_domain
HC_DB, HC_KEYWORDS = load_domain("healthcare")

def search_healthcare(query: str) -> dict:
    query_lower = query.lower()
    results = []
    for topic_key, keywords in HC_KEYWORDS.items():
        if isinstance(keywords, list):
            score = sum(1 for kw in keywords if kw.lower() in query_lower)
        elif isinstance(keywords, dict):
            score = 0
            for alias_list in keywords.values():
                score += sum(1 for kw in alias_list if kw.lower() in query_lower)
        else:
            score = 0
        if score > 0:
            topic_data = HC_DB.get(topic_key, {})
            results.append({"topic": topic_key, "name_ja": topic_data.get("name_ja", ""), "name_en": topic_data.get("name_en", ""), "data": topic_data, "relevance_score": score})
    for k, v in HC_DB.items():
        if k.startswith("_"): continue
        text = f"{k} {v.get('name_ja','')} {v.get('name_en','')} {v.get('description','')}".lower()
        if query_lower in text and not any(r["topic"] == k for r in results):
            results.append({"topic": k, "name_ja": v.get("name_ja",""), "name_en": v.get("name_en",""), "data": v, "relevance_score": 1})
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {"domain": "healthcare", "query": query, "results": results, "total_matches": len(results)}

def list_healthcare_topics() -> dict:
    topics = [{"key": k, "name_ja": v.get("name_ja",""), "name_en": v.get("name_en",""), "description": v.get("description","")} for k, v in HC_DB.items() if not k.startswith("_")]
    return {"domain": "healthcare", "topics": topics, "total": len(topics)}
