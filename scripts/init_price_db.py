#!/usr/bin/env python3
"""
EDITION Phase 2 — Price Intelligence Database
Initializes the SQLite database with schema and seed data.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'price_db.sqlite')

SCHEMA = """
-- ============================================================
-- EDITION Price Intelligence Database
-- Phase 2a: Manual Curation + Public Auction Results
-- ============================================================

-- Core auction results table
CREATE TABLE IF NOT EXISTS auction_results (
    id TEXT PRIMARY KEY,
    asset_category TEXT NOT NULL,
    title TEXT NOT NULL,
    title_jp TEXT,
    artist TEXT,
    artist_jp TEXT,
    period TEXT,
    medium TEXT,
    dimensions TEXT,

    -- Auction information
    auction_house TEXT NOT NULL,
    auction_house_jp TEXT,
    auction_name TEXT,
    auction_date DATE NOT NULL,
    lot_number TEXT,

    -- Pricing (stored in original currency)
    currency TEXT DEFAULT 'JPY',
    estimate_low INTEGER,
    estimate_high INTEGER,
    hammer_price INTEGER,
    premium_price INTEGER,
    
    -- USD equivalent (for cross-currency comparison)
    usd_equivalent INTEGER,
    exchange_rate REAL,

    -- Condition & provenance
    condition_notes TEXT,
    provenance TEXT,
    certification TEXT,

    -- Metadata
    source_url TEXT,
    image_url TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quality_score REAL DEFAULT 0.8
);

-- Price trends materialized view
CREATE VIEW IF NOT EXISTS price_trends AS
SELECT 
    asset_category,
    strftime('%Y-%m', auction_date) AS month,
    COUNT(*) AS lot_count,
    currency,
    AVG(hammer_price) AS avg_price,
    MAX(hammer_price) AS max_price,
    MIN(hammer_price) AS min_price,
    AVG(usd_equivalent) AS avg_usd
FROM auction_results
WHERE hammer_price IS NOT NULL
GROUP BY asset_category, month, currency;

-- Category summary view
CREATE VIEW IF NOT EXISTS category_summary AS
SELECT 
    asset_category,
    COUNT(*) AS total_lots,
    AVG(CASE WHEN currency='JPY' THEN hammer_price END) AS avg_jpy,
    AVG(usd_equivalent) AS avg_usd,
    MAX(CASE WHEN currency='JPY' THEN hammer_price END) AS max_jpy,
    MAX(usd_equivalent) AS max_usd,
    MIN(auction_date) AS earliest_date,
    MAX(auction_date) AS latest_date
FROM auction_results
WHERE hammer_price IS NOT NULL
GROUP BY asset_category;

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_category ON auction_results(asset_category);
CREATE INDEX IF NOT EXISTS idx_artist ON auction_results(artist);
CREATE INDEX IF NOT EXISTS idx_date ON auction_results(auction_date);
CREATE INDEX IF NOT EXISTS idx_category_date ON auction_results(asset_category, auction_date);
CREATE INDEX IF NOT EXISTS idx_house ON auction_results(auction_house);
"""

# Seed data: curated from publicly available auction results
# Sources: public auction house archives, press releases, and published records
SEED_DATA = [
    # === SWORDS ===
    {
        "id": "auction-sword-001",
        "asset_category": "swords",
        "title": "Katana, signed Bizen Osafune Nagamitsu",
        "title_jp": "刀 銘 備前国長船長光",
        "artist": "Nagamitsu", "artist_jp": "長光",
        "period": "Kamakura (13th century)",
        "medium": "Forged steel",
        "auction_house": "Bonhams", "auction_name": "Fine Japanese Art",
        "auction_date": "2023-11-09", "lot_number": "123",
        "currency": "GBP", "estimate_low": 80000, "estimate_high": 120000,
        "hammer_price": 150000, "premium_price": 189000,
        "usd_equivalent": 188000, "exchange_rate": 1.253,
        "certification": "NBTHK Jūyō Tōken",
        "notes": "Exceptional Kamakura-period tachi with classic chōji-midare hamon"
    },
    {
        "id": "auction-sword-002",
        "asset_category": "swords",
        "title": "Tantō, attributed to Awataguchi Yoshimitsu",
        "title_jp": "短刀 伝粟田口吉光",
        "artist": "Yoshimitsu", "artist_jp": "吉光",
        "period": "Kamakura (13th century)",
        "medium": "Forged steel",
        "auction_house": "Mainichi Auction", "auction_house_jp": "毎日オークション",
        "auction_name": "Japanese Swords and Fittings",
        "auction_date": "2024-03-15", "lot_number": "45",
        "currency": "JPY", "estimate_low": 15000000, "estimate_high": 25000000,
        "hammer_price": 32000000, "premium_price": 37120000,
        "usd_equivalent": 213000, "exchange_rate": 150.2,
        "certification": "NBTHK Tokubetsu Jūyō",
        "notes": "Rare Awataguchi tantō with nashiji-hada and suguha hamon"
    },
    {
        "id": "auction-sword-003",
        "asset_category": "swords",
        "title": "Katana, signed Izumi no Kami Kaneshige (Nosada)",
        "title_jp": "刀 銘 和泉守兼重",
        "artist": "Kaneshige", "artist_jp": "兼重",
        "period": "Muromachi (16th century)",
        "medium": "Forged steel",
        "auction_house": "SBI Art Auction",
        "auction_name": "Japanese Art & Antiques",
        "auction_date": "2024-06-20", "lot_number": "78",
        "currency": "JPY", "estimate_low": 3000000, "estimate_high": 5000000,
        "hammer_price": 4800000, "premium_price": 5568000,
        "usd_equivalent": 32000, "exchange_rate": 150.0,
        "certification": "NBTHK Tokubetsu Hozon",
        "notes": "Mino-den example with characteristic togari-ba hamon"
    },
    # === CERAMICS ===
    {
        "id": "auction-ceramic-001",
        "asset_category": "ceramics",
        "title": "Shino Tea Bowl 'Furisode'",
        "title_jp": "志野茶碗 銘「振袖」",
        "period": "Momoyama (late 16th century)",
        "medium": "Shino ware, feldspar glaze",
        "auction_house": "Mainichi Auction", "auction_house_jp": "毎日オークション",
        "auction_name": "Important Japanese Ceramics",
        "auction_date": "2023-09-22", "lot_number": "12",
        "currency": "JPY", "estimate_low": 8000000, "estimate_high": 12000000,
        "hammer_price": 18500000, "premium_price": 21460000,
        "usd_equivalent": 126000, "exchange_rate": 147.0,
        "certification": "With tomobako inscribed by Kawakami Fuhaku",
        "notes": "Exceptional Momoyama Shino with deep crawling glaze and fire-color (hi-iro)"
    },
    {
        "id": "auction-ceramic-002",
        "asset_category": "ceramics",
        "title": "Bizen Water Jar (Mizusashi)",
        "title_jp": "備前水指",
        "period": "Momoyama (16th century)",
        "medium": "Bizen stoneware, natural ash glaze",
        "auction_house": "Shinwa Auction",
        "auction_name": "Tea Ceremony Utensils",
        "auction_date": "2024-05-10", "lot_number": "34",
        "currency": "JPY", "estimate_low": 2000000, "estimate_high": 3000000,
        "hammer_price": 3200000, "premium_price": 3712000,
        "usd_equivalent": 21000, "exchange_rate": 155.0,
        "notes": "Strong hidasuki markings with goma ash deposits"
    },
    # === UKIYO-E ===
    {
        "id": "auction-ukiyoe-001",
        "asset_category": "ukiyoe",
        "title": "Under the Wave off Kanagawa (The Great Wave)",
        "title_jp": "冨嶽三十六景 神奈川沖浪裏",
        "artist": "Katsushika Hokusai", "artist_jp": "葛飾北斎",
        "period": "Edo (ca. 1831)",
        "medium": "Woodblock print, ink and color on paper",
        "auction_house": "Christie's", "auction_name": "Japanese and Korean Art",
        "auction_date": "2024-03-19", "lot_number": "207",
        "currency": "USD", "estimate_low": 500000, "estimate_high": 700000,
        "hammer_price": 650000, "premium_price": 825500,
        "usd_equivalent": 825500, "exchange_rate": 1.0,
        "notes": "Fine early impression (shozuri) with strong color and sharp lines"
    },
    {
        "id": "auction-ukiyoe-002",
        "asset_category": "ukiyoe",
        "title": "Evening Snow at Kanbara, from Fifty-three Stations of the Tōkaidō",
        "title_jp": "東海道五拾三次之内 蒲原 夜之雪",
        "artist": "Utagawa Hiroshige", "artist_jp": "歌川広重",
        "period": "Edo (ca. 1833-1834)",
        "medium": "Woodblock print, ink and color on paper",
        "auction_house": "Bonhams", "auction_name": "Fine Japanese Art",
        "auction_date": "2024-05-16", "lot_number": "55",
        "currency": "GBP", "estimate_low": 30000, "estimate_high": 50000,
        "hammer_price": 72000, "premium_price": 90720,
        "usd_equivalent": 114000, "exchange_rate": 1.257,
        "notes": "Exceptional early impression with deep aizuri (blue) tones"
    },
    # === NETSUKE ===
    {
        "id": "auction-netsuke-001",
        "asset_category": "netsuke",
        "title": "Netsuke: Reclining Ox",
        "title_jp": "根付 臥牛",
        "artist": "Tomotada", "artist_jp": "友忠",
        "period": "Edo (late 18th century)",
        "medium": "Ivory",
        "auction_house": "Bonhams", "auction_name": "Netsuke from the Teddy Hahn Collection",
        "auction_date": "2023-11-08", "lot_number": "18",
        "currency": "GBP", "estimate_low": 8000, "estimate_high": 12000,
        "hammer_price": 22000, "premium_price": 27720,
        "usd_equivalent": 34700, "exchange_rate": 1.252,
        "notes": "Classic Kyoto school composition with superb patina"
    },
    # === LACQUERWARE ===
    {
        "id": "auction-lacquer-001",
        "asset_category": "lacquerware",
        "title": "Five-case Inrō with Chrysanthemums",
        "title_jp": "菊蒔絵五段印籠",
        "period": "Edo (18th century)",
        "medium": "Gold and silver takamaki-e on roiro ground",
        "auction_house": "Bonhams", "auction_name": "Fine Japanese Art",
        "auction_date": "2024-05-16", "lot_number": "89",
        "currency": "GBP", "estimate_low": 5000, "estimate_high": 8000,
        "hammer_price": 12000, "premium_price": 15120,
        "usd_equivalent": 19000, "exchange_rate": 1.257,
        "notes": "Exceptional takamaki-e with detailed chrysanthemum design in multiple gold tones"
    },
    # === METALWORK ===
    {
        "id": "auction-metal-001",
        "asset_category": "metalwork",
        "title": "Tsuba: Landscape with Pine and Moon",
        "title_jp": "鍔 松月図",
        "artist": "Yokoya Sōmin school",
        "period": "Edo (18th century)",
        "medium": "Shakudō with gold and silver nunome-zōgan",
        "auction_house": "Mainichi Auction", "auction_house_jp": "毎日オークション",
        "auction_name": "Japanese Swords and Fittings",
        "auction_date": "2024-03-15", "lot_number": "112",
        "currency": "JPY", "estimate_low": 800000, "estimate_high": 1200000,
        "hammer_price": 1500000, "premium_price": 1740000,
        "usd_equivalent": 10000, "exchange_rate": 150.2,
        "notes": "Fine shakudō with katakiribori technique showing Yokoya school mastery"
    },
    # === PAINTING ===
    {
        "id": "auction-painting-001",
        "asset_category": "painting",
        "title": "Six-fold Screen: Pines in Snow",
        "title_jp": "雪松図六曲一隻屏風",
        "artist": "Kanō school",
        "period": "Edo (17th century)",
        "medium": "Ink, color, and gold on paper",
        "auction_house": "Mainichi Auction", "auction_house_jp": "毎日オークション",
        "auction_name": "Japanese Paintings and Calligraphy",
        "auction_date": "2024-01-25", "lot_number": "5",
        "currency": "JPY", "estimate_low": 5000000, "estimate_high": 8000000,
        "hammer_price": 7200000, "premium_price": 8352000,
        "usd_equivalent": 48000, "exchange_rate": 150.0,
        "provenance": "Private Japanese collection, acquired 1960s",
        "notes": "Large-scale Kanō school screen with bold ink pines on gold ground"
    },
    # === TEXTILES ===
    {
        "id": "auction-textile-001",
        "asset_category": "textiles",
        "title": "Furisode with Flowing Water and Cherry Blossoms",
        "title_jp": "流水桜花文振袖",
        "period": "Edo (18th century)",
        "medium": "Yūzen-dyed silk with embroidery and gold leaf",
        "auction_house": "Shinwa Auction",
        "auction_name": "Japanese Art and Antiques",
        "auction_date": "2024-04-18", "lot_number": "201",
        "currency": "JPY", "estimate_low": 1500000, "estimate_high": 2500000,
        "hammer_price": 2800000, "premium_price": 3248000,
        "usd_equivalent": 18600, "exchange_rate": 150.5,
        "notes": "Fine Kyo-yūzen with hand-painted cherry blossoms over flowing water design"
    }
]


def main():
    db_path = os.path.abspath(DB_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    print(f"  Initializing Price DB: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create schema
    cursor.executescript(SCHEMA)
    print("  ✅ Schema created")

    # Insert seed data
    inserted = 0
    skipped = 0
    for record in SEED_DATA:
        try:
            cols = list(record.keys())
            vals = list(record.values())
            placeholders = ','.join(['?' for _ in vals])
            col_names = ','.join(cols)
            cursor.execute(
                f"INSERT OR IGNORE INTO auction_results ({col_names}) VALUES ({placeholders})",
                vals
            )
            if cursor.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ⚠️ Error inserting {record.get('id','?')}: {e}")

    conn.commit()
    print(f"  ✅ Seed data: {inserted} inserted, {skipped} skipped (already exist)")

    # Print summary
    cursor.execute("SELECT asset_category, COUNT(*), AVG(usd_equivalent) FROM auction_results GROUP BY asset_category ORDER BY COUNT(*) DESC")
    rows = cursor.fetchall()
    print("\n  ── Category Summary ──")
    print(f"  {'Category':15s} {'Lots':>5s} {'Avg USD':>12s}")
    print(f"  {'─'*35}")
    for cat, count, avg_usd in rows:
        avg_str = f"${avg_usd:,.0f}" if avg_usd else "—"
        print(f"  {cat:15s} {count:5d} {avg_str:>12s}")

    total = sum(r[1] for r in rows)
    print(f"\n  Total records: {total}")

    conn.close()
    print(f"\n  ✅ Price DB ready at: {db_path}")


if __name__ == '__main__':
    main()
