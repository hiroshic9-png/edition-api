#!/usr/bin/env python3
"""
Export price_db.sqlite to static JSON files for frontend consumption.
Run after adding new auction data to regenerate the API-compatible JSON.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'price_db.sqlite')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def export():
    conn = sqlite3.connect(os.path.abspath(DB_PATH))
    conn.row_factory = sqlite3.Row

    # 1. All auction results
    rows = conn.execute("""
        SELECT * FROM auction_results ORDER BY auction_date DESC
    """).fetchall()
    results = [dict(r) for r in rows]

    # 2. Category summary
    cats = conn.execute("""
        SELECT 
            asset_category,
            COUNT(*) as total_lots,
            ROUND(AVG(usd_equivalent)) as avg_usd,
            MAX(usd_equivalent) as max_usd,
            MIN(usd_equivalent) as min_usd,
            ROUND(AVG(CASE WHEN currency='JPY' THEN hammer_price END)) as avg_jpy,
            MAX(CASE WHEN currency='JPY' THEN hammer_price END) as max_jpy,
            MIN(auction_date) as earliest,
            MAX(auction_date) as latest
        FROM auction_results
        WHERE hammer_price IS NOT NULL
        GROUP BY asset_category
        ORDER BY total_lots DESC
    """).fetchall()
    categories = [dict(c) for c in cats]

    # 3. Recent notable sales (top 5 by USD value)
    notable = conn.execute("""
        SELECT id, asset_category, title, title_jp, artist, artist_jp,
               auction_house, auction_date, currency,
               hammer_price, premium_price, usd_equivalent,
               certification, notes
        FROM auction_results
        WHERE usd_equivalent IS NOT NULL
        ORDER BY usd_equivalent DESC
        LIMIT 5
    """).fetchall()
    highlights = [dict(n) for n in notable]

    # 4. Market stats
    stats = conn.execute("""
        SELECT
            COUNT(*) as total_records,
            COUNT(DISTINCT asset_category) as categories_covered,
            COUNT(DISTINCT auction_house) as auction_houses,
            ROUND(SUM(usd_equivalent)) as total_market_value,
            MIN(auction_date) as data_from,
            MAX(auction_date) as data_to
        FROM auction_results
    """).fetchone()

    # Build output
    output = {
        "meta": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "version": "2.0a",
            "description": "EDITION Price Intelligence — Curated Auction Data"
        },
        "stats": dict(stats),
        "categories": categories,
        "highlights": highlights,
        "results": results
    }

    out_path = os.path.join(OUT_DIR, 'price_intelligence.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"  ✅ Exported {len(results)} records to {out_path}")
    print(f"  📊 {dict(stats)['categories_covered']} categories, {dict(stats)['auction_houses']} auction houses")
    print(f"  💰 Total tracked value: ${dict(stats)['total_market_value']:,.0f}")

    conn.close()


if __name__ == '__main__':
    export()
