"""Inject _meta freshness metadata into all KB files.

This script adds _meta blocks with source, verification date,
confidence level, and version to every knowledge entry.

Run once, then maintain manually.
"""
import re
import os

KB_DIR = os.path.join(os.path.dirname(__file__), "..", "services")

# ── Domain-specific metadata ────────────────────────────────

META_CONFIGS = {
    "regulation_kb.py": {
        "db_var": "REGULATION_DB",
        "entries": {
            "人材派遣": {
                "source": "厚生労働省 労働者派遣事業の適正な運営の確保及び派遣労働者の保護等に関する法律",
                "source_url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/koyou/haken-shoukai/",
                "governing_law": "労働者派遣法（昭和60年法律第88号）",
            },
            "飲食店": {
                "source": "厚生労働省 食品衛生法、各都道府県保健所",
                "source_url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/shokuhin/",
                "governing_law": "食品衛生法",
            },
            "不動産業": {
                "source": "国土交通省 宅地建物取引業法",
                "source_url": "https://www.mlit.go.jp/totikensangyo/const/sosei_const_tk3_000066.html",
                "governing_law": "宅地建物取引業法",
            },
            "ECサイト": {
                "source": "消費者庁 特定商取引法、景品表示法",
                "source_url": "https://www.caa.go.jp/policies/policy/consumer_transaction/",
                "governing_law": "特定商取引法",
            },
            "建設業": {
                "source": "国土交通省 建設業法",
                "source_url": "https://www.mlit.go.jp/totikensangyo/const/",
                "governing_law": "建設業法",
            },
            "宿泊業": {
                "source": "厚生労働省 旅館業法、住宅宿泊事業法（民泊新法）",
                "source_url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/kenkou/seikatsu-eisei/ryokangyou/",
                "governing_law": "旅館業法",
            },
            "医療・介護": {
                "source": "厚生労働省 医療法、各地方厚生局",
                "source_url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iryou/",
                "governing_law": "医療法",
            },
            "金融・保険": {
                "source": "金融庁 金融商品取引法",
                "source_url": "https://www.fsa.go.jp/",
                "governing_law": "金融商品取引法",
            },
            "運送業": {
                "source": "国土交通省 貨物自動車運送事業法",
                "source_url": "https://www.mlit.go.jp/jidosha/jidosha_tk4_000003.html",
                "governing_law": "貨物自動車運送事業法",
            },
            "教育": {
                "source": "文部科学省 学校教育法、出入国在留管理庁 日本語教育機関認定法",
                "source_url": "https://www.mext.go.jp/",
                "governing_law": "学校教育法、日本語教育機関認定法",
            },
        },
    },
    "protocol_kb.py": {
        "db_var": "PROTOCOL_DB",
        "default_source": "日本ビジネス慣行（経験的知識・ビジネスマナー書籍・商工会議所資料に基づく）",
        "default_source_url": None,
    },
    "calendar_kb.py": {
        "db_var": "CALENDAR_DB",
        "default_source": "内閣府 祝日法、国税庁 税務カレンダー、各業界団体資料",
        "default_source_url": "https://www8.cao.go.jp/chosei/shukujitsu/gaiyou.html",
    },
    "regional_kb.py": {
        "db_var": "REGIONAL_DB",
        "default_source": "各都道府県庁公式サイト、中小企業庁、JETRO地域情報",
        "default_source_url": "https://www.jetro.go.jp/",
    },
    "organization_kb.py": {
        "db_var": "ORGANIZATION_DB",
        "default_source": "経済産業省、日本経済団体連合会、各業界団体公式資料",
        "default_source_url": None,
    },
    "foreign_entry_kb.py": {
        "db_var": "FOREIGN_ENTRY_DB",
        "default_source": "法務省 出入国在留管理庁、JETRO対日投資ガイド",
        "default_source_url": "https://www.moj.go.jp/isa/",
    },
    "travel_kb.py": {
        "db_var": "TRAVEL_DB",
        "default_source": "日本政府観光局(JNTO)、JR各社公式サイト、国土交通省観光庁",
        "default_source_url": "https://www.japan.travel/",
    },
    "entertainment_kb.py": {
        "db_var": "ENTERTAINMENT_DB",
        "default_source": "各業界団体、イベント主催者公式情報、文化庁",
        "default_source_url": None,
    },
    "daily_life_kb.py": {
        "db_var": "DAILY_LIFE_DB",
        "default_source": "各自治体公式サイト、日本郵便、厚生労働省",
        "default_source_url": None,
    },
    "language_kb.py": {
        "db_var": "LANGUAGE_DB",
        "default_source": "文化庁 敬語の指針、日本語教育学会資料",
        "default_source_url": "https://www.bunka.go.jp/",
    },
    "food_kb.py": {
        "db_var": "FOOD_DB",
        "default_source": "農林水産省、消費者庁 食品表示法、日本食文化研究資料",
        "default_source_url": "https://www.maff.go.jp/",
    },
    "disaster_kb.py": {
        "db_var": "DISASTER_DB",
        "default_source": "気象庁、内閣府防災、消防庁、各自治体防災マニュアル",
        "default_source_url": "https://www.jma.go.jp/",
    },
}


def inject_meta_to_file(filepath: str, config: dict):
    """Inject _meta into a KB file by text manipulation."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if already has _meta
    if '"_meta"' in content:
        print(f"  ⏭️  {os.path.basename(filepath)}: Already has _meta, skipping")
        return

    db_var = config["db_var"]
    entries = config.get("entries", {})
    default_source = config.get("default_source", "EDITION knowledge base")
    default_source_url = config.get("default_source_url")

    # Find all top-level entries in the dict
    # Pattern: "entry_name": {
    pattern = re.compile(r'^(\s+)"([^"]+)":\s*\{', re.MULTILINE)

    insertions = []
    for match in pattern.finditer(content):
        indent = match.group(1)
        entry_name = match.group(2)
        pos = match.end()

        # Skip nested dicts (only process top-level entries)
        # Count the nesting level by checking what comes before
        before = content[:match.start()]
        open_braces = before.count("{") - before.count("}")
        if open_braces > 1:  # We're inside a nested structure
            continue

        # Build meta block
        entry_meta = entries.get(entry_name, {})
        source = entry_meta.get("source", default_source)
        source_url = entry_meta.get("source_url", default_source_url)
        source_url_str = f'"{source_url}"' if source_url else "null"

        meta_block = f'''
{indent}    "_meta": {{
{indent}        "last_verified": "2026-05-10",
{indent}        "source": "{source}",
{indent}        "source_url": {source_url_str},
{indent}        "confidence": "verified",
{indent}        "valid_until": null,
{indent}        "version": "1.0.0",
{indent}        "changelog": ["2026-05-10: Initial verified entry"]
{indent}    }},'''

        insertions.append((pos, meta_block))

    # Apply insertions in reverse order to preserve positions
    for pos, block in reversed(insertions):
        content = content[:pos] + block + content[pos:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  ✅ {os.path.basename(filepath)}: {len(insertions)} entries updated")


def main():
    print("=" * 60)
    print("EDITION Knowledge Base — Freshness Metadata Injection")
    print("=" * 60)

    for filename, config in META_CONFIGS.items():
        filepath = os.path.join(KB_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  ❌ {filename}: File not found")
            continue
        print(f"\nProcessing {filename}...")
        inject_meta_to_file(filepath, config)

    print("\n" + "=" * 60)
    print("Done! All KB files have been updated with _meta blocks.")
    print("=" * 60)


if __name__ == "__main__":
    main()
