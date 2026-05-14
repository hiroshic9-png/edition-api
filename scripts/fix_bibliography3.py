#!/usr/bin/env python3
"""
書誌情報修正バッチ3
"""
import json, datetime

now = datetime.datetime.utcnow().isoformat() + "Z"

CORRECTIONS = {
    # ❌ 書籍として存在しない
    "Nishimura, Japanese Embroidery History": None,  # この書名の書籍は存在しない

    # ⚠️ タイトル不正確 → 修正
    "Nishikawa, Japanese Buddhist Sculpture Techniques": "Nishikawa Kyotaro & Sano Emily, The Great Age of Japanese Buddhist Sculpture AD 600-1300, 1982",
    "Nishikawa, Butsuzo no Mikata": "Nishikawa Kyotaro, Butsuzo no Mikata (仏像の見方), Geijutsu Shincho feature / general guide",
    "Ogasawara, Japanese Sword Mountings": "Ogasawara Nobuo, Japanese Swords, Hoikusha, ISBN 4-586-54022-2",
    "Nakamura Masao, Tea Room Architecture": "Nakamura Masao, Sukiya Kenchiku Shusei, Shogakukan, 1983 / Chashitsu o Yomu, Tankosha, 2002",
}

with open("/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/training_pairs.json") as f:
    data = json.load(f)

corrections_applied = 0
sources_removed = 0

for p in data["pairs"]:
    for field in ["sources", "evidence"]:
        if field not in p:
            continue
        new_sources = []
        for s in p[field]:
            if s in CORRECTIONS:
                replacement = CORRECTIONS[s]
                if replacement is None:
                    sources_removed += 1
                    print(f"  REMOVED from {p['id']}: {s}")
                else:
                    new_sources.append(replacement)
                    corrections_applied += 1
                    print(f"  CORRECTED in {p['id']}: {s}")
            else:
                new_sources.append(s)
        p[field] = new_sources

# Orphan check
orphaned = [p["id"] for p in data["pairs"] if len(p.get("sources",[]) + p.get("evidence",[])) == 0]

data["generated_at"] = now
data["total_pairs"] = len(data["pairs"])

with open("/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/training_pairs.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n=== BIBLIOGRAPHY BATCH 3 ===")
print(f"Corrected: {corrections_applied}, Removed: {sources_removed}, Orphaned: {len(orphaned)}")
if orphaned:
    for pid in orphaned:
        print(f"  ⚠️ {pid}")
