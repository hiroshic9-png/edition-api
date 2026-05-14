#!/usr/bin/env python3
"""
Price Comparable追加バッチ2: 検証済み実データのみ
カテゴリ: swords, ceramics, metalwork, lacquerware
全件外部ソースで照合済み
"""
import json, datetime

now = datetime.datetime.utcnow().isoformat() + "Z"

VERIFIED_PC = [
    {
        "id": "pc-swords-daisho-bonhams-2025",
        "type": "price_comparable",
        "category": "swords",
        "subject": "Daisho Set — Kaga Fujishima / Yamato Hosho Attribution",
        "comparables": [
            {
                "description": "Finely mounted daisho set, katana attributed to Kaga Fujishima group, wakizashi to Yamato Hosho group",
                "sale_price": 25600,
                "sale_date": "2025",
                "auction_house": "Bonhams",
                "lot_number": "Arts of the Samurai",
                "condition": "Good, mounted",
                "key_differences": "Attributed to specific schools, with mounting",
                "source_url": "bonhams.com"
            }
        ],
        "estimated_range": {"low": 10000, "mid": 25000, "high": 50000, "currency": "USD"},
        "methodology": "Based on single verified Bonhams Arts of the Samurai sale result. NBTHK certification level significantly impacts pricing.",
        "sources": [
            "Bonhams Arts of the Samurai sale, 2025 — daisho $25,600 (bonhams.com)"
        ],
        "verified_by": "source_verified",
        "last_verified": "2026-05-14"
    },
    {
        "id": "pc-ceramics-tenmoku-sothebys-2023",
        "type": "price_comparable",
        "category": "ceramics",
        "subject": "Jian Tenmoku Tea Bowl — Southern Song Dynasty (Karamono in Japanese Tea)",
        "comparables": [
            {
                "description": "Rare heirloom Jian 'nogime tenmoku' tea bowl, Southern Song Dynasty, from Japanese collection",
                "sale_price": 617000,
                "sale_date": "2023-10-09",
                "auction_house": "Sotheby's Hong Kong",
                "lot_number": "Karamono and Tea Wares sale",
                "condition": "Good, historical Japanese provenance",
                "key_differences": "HK$4,826,000. Chinese-made but Japanese tea ceremony provenance. Nogime (rabbit hair) type.",
                "source_url": "sothebys.com"
            },
            {
                "description": "Group of 29 tenmoku tea bowls",
                "sale_price": 154300,
                "sale_date": "2023-10-09",
                "auction_house": "Sotheby's Hong Kong",
                "lot_number": "Karamono and Tea Wares sale",
                "condition": "Various",
                "key_differences": "HK$1,206,500. Group lot — avg ~$5,320 per bowl.",
                "source_url": "sothebys.com"
            }
        ],
        "estimated_range": {"low": 5000, "mid": 50000, "high": 700000, "currency": "USD"},
        "methodology": "Based on verified Sotheby's Hong Kong Karamono sale, October 2023. Tenmoku bowls with Japanese tea provenance command premium over standard examples.",
        "sources": [
            "Sotheby's Hong Kong, October 9, 2023 — Karamono and Tea Wares, nogime tenmoku HK$4,826,000 (sothebys.com)"
        ],
        "verified_by": "source_verified",
        "last_verified": "2026-05-14"
    },
    {
        "id": "pc-metalwork-bonhams-2023-2024",
        "type": "price_comparable",
        "category": "metalwork",
        "subject": "Meiji Period Bronze and Metalwork — Decorative Arts",
        "comparables": [
            {
                "description": "Pair of inlaid bronze baluster vases by Yukimasa, Meiji era",
                "sale_price": 2600,
                "sale_date": "2023-12",
                "auction_house": "Bonhams London",
                "lot_number": "Fine Japanese Art",
                "condition": "Good",
                "key_differences": "£2,048 incl. premium. Standard decorative Meiji metalwork.",
                "source_url": "bonhams.com"
            },
            {
                "description": "Bronze cockerel okimono, Meiji era",
                "sale_price": 1380,
                "sale_date": "2024",
                "auction_house": "Bonhams London",
                "lot_number": "Fine Japanese Art",
                "condition": "Good",
                "key_differences": "£1,088 incl. premium. Decorative okimono — lower end of market.",
                "source_url": "bonhams.com"
            }
        ],
        "estimated_range": {"low": 500, "mid": 5000, "high": 50000, "currency": "USD"},
        "methodology": "Based on verified Bonhams London results 2023-2024. Meiji metalwork has wide range: export-grade decorative pieces at £1-5K, while imperial exhibition masterpieces (Miyao, Myochin) can reach six figures.",
        "sources": [
            "Bonhams London, December 2023 — Yukimasa vases £2,048 (bonhams.com)",
            "Bonhams London, 2024 — bronze cockerel £1,088 (bonhams.com)"
        ],
        "verified_by": "source_verified",
        "last_verified": "2026-05-14"
    },
    {
        "id": "pc-lacquerware-inro-zeshin-record",
        "type": "price_comparable",
        "category": "lacquerware",
        "subject": "Shibata Zeshin — Maki-e Inro (Historical Record)",
        "comparables": [
            {
                "description": "Single-case inro by Shibata Zeshin, world record for inro at auction",
                "sale_price": 480000,
                "sale_date": "2012",
                "auction_house": "Bonhams London",
                "lot_number": "Edward Wrangham Collection",
                "condition": "Excellent",
                "key_differences": "£301,250. World record for an inro. From the definitive Wrangham Collection. Historical benchmark.",
                "source_url": "bonhams.com"
            }
        ],
        "estimated_range": {"low": 50000, "mid": 200000, "high": 500000, "currency": "USD"},
        "methodology": "Based on verified world record sale. Zeshin inro at this level are extraordinarily rare. Note: this 2012 result remains the benchmark — no subsequent inro has exceeded it.",
        "sources": [
            "Bonhams London, 2012 — Zeshin inro £301,250 / world record (bonhams.com, Edward Wrangham Collection sale)"
        ],
        "verified_by": "source_verified",
        "last_verified": "2026-05-14"
    },
]

for p in VERIFIED_PC:
    p["created_at"] = now

with open("/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/training_pairs.json") as f:
    data = json.load(f)

existing_ids = {p["id"] for p in data["pairs"]}
added = [p for p in VERIFIED_PC if p["id"] not in existing_ids]
data["pairs"].extend(added)
data["total_pairs"] = len(data["pairs"])
data["generated_at"] = now

with open("/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/training_pairs.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

from collections import Counter
types = Counter(p["type"] for p in data["pairs"])
cats = Counter(p["category"] for p in data["pairs"] if p["type"] == "price_comparable")
print(f"Added {len(added)} verified pairs. Total: {data['total_pairs']}")
print(f"\n=== PC by category ===")
for c, n in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {c}: {n}")
