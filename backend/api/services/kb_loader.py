"""Centralized JSON Knowledge Base loader.

Single source of truth for loading all EDITION knowledge from data/kb/*.json.
Replaces the legacy *_kb.py Python modules with a clean JSON-based pipeline.

Usage:
    from backend.api.services.kb_loader import load_domain

    DB, KEYWORDS = load_domain("calendar")
    # DB = dict loaded from data/kb/calendar.json
    # KEYWORDS = dict loaded from data/kb/calendar_keywords.json
"""
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Resolve KB directory relative to project root
_KB_DIR = Path(__file__).resolve().parents[3] / "data" / "kb"

# In-memory cache (module-level singleton)
_cache: dict[str, dict] = {}


def _load_json(filename: str) -> dict:
    """Load and cache a JSON file from the KB directory."""
    if filename in _cache:
        return _cache[filename]

    filepath = _KB_DIR / filename
    if not filepath.exists():
        logger.warning(f"KB file not found: {filepath}")
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        _cache[filename] = data
        return data
    except Exception as e:
        logger.error(f"Failed to load KB file {filepath}: {e}")
        return {}


def load_domain(domain: str) -> tuple[dict, dict]:
    """Load a knowledge domain and its keywords from JSON files.

    Args:
        domain: Domain name (e.g. "calendar", "food", "regulation")

    Returns:
        Tuple of (database_dict, keywords_dict)
    """
    db = _load_json(f"{domain}.json")
    keywords = _load_json(f"{domain}_keywords.json")
    return db, keywords


def load_regulation() -> tuple[dict, dict, dict, dict]:
    """Load the regulation domain with all its components.

    Regulation is special: it has industry DB + tourist DB + industry keywords + tourist keywords.

    Returns:
        Tuple of (REGULATION_DB, TOURIST_REGULATIONS, INDUSTRY_KEYWORDS, TOURIST_KEYWORDS)
    """
    regulation_db = _load_json("regulation.json")
    tourist_regulations = _load_json("regulation_tourist.json")
    industry_keywords = _load_json("regulation_industry_keywords.json")
    tourist_keywords = _load_json("regulation_tourist_keywords.json")
    return regulation_db, tourist_regulations, industry_keywords, tourist_keywords


def load_all_domains() -> dict[str, dict]:
    """Load all knowledge domains. Used by freshness reports and audits.

    Returns:
        Dict mapping domain_name -> database_dict
    """
    domain_names = [
        "regulation", "protocol", "calendar", "regional",
        "organization", "foreign_entry", "travel", "entertainment",
        "daily_life", "language", "food", "disaster",
    ]
    domains = {}
    for name in domain_names:
        db = _load_json(f"{name}.json")
        if db:
            domains[name] = db
    return domains


def invalidate_cache(domain: Optional[str] = None):
    """Invalidate the in-memory cache. Useful for hot-reloading after KB updates.

    Args:
        domain: If provided, only invalidate files for this domain.
                If None, invalidate entire cache.
    """
    global _cache
    if domain is None:
        _cache.clear()
        logger.info("KB cache fully invalidated")
    else:
        keys_to_remove = [k for k in _cache if k.startswith(domain)]
        for k in keys_to_remove:
            del _cache[k]
        logger.info(f"KB cache invalidated for domain: {domain}")
