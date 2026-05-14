#!/usr/bin/env python3
"""
書誌情報修正バッチ2: 追加照合結果に基づく修正
"""
import json, datetime

now = datetime.datetime.utcnow().isoformat() + "Z"

CORRECTIONS = {
    # ❌ 書籍として存在しない — 削除
    "Aimé, Mokume Gane in the Art of Japan": None,  # 「Aimé」名義の書籍は存在しない。正しくはSteve Midgett
    "Yaso Kazu, Metallurgy of Japanese Swords": None,  # 「Yaso Kazu」は存在しない。正しくはTawara Kuniichi
    "Ogawa, Japanese Metalwork Techniques": None,  # この書名の書籍は存在しない
    "Sasaki, Natural Dyes of Japan": None,  # この書名の書籍は存在しない

    # ⚠️ タイトル不正確 → 正確なタイトルに修正
    "Earle, The Satsuma Homage": "Earle, Joe, Splendors of Imperial Japan (Khalili Collection), 2002",
    "Bushell, Netsuke Familiar and Unfamiliar": "Bushell, Raymond, Netsuke Familiar and Unfamiliar, Weatherhill, 1975 (ISBN 978-0834801158)",
    "Harris, Japanese Imperial Craftsmen": "Harris, Victor, Japanese Imperial Craftsmen: Meiji Art from the Khalili Collection, British Museum Press, 1994 (ISBN 978-0714114637)",
    "Mitsutani, Japanese Dendrochronology Database": "Mitsutani Takumi, Dendrochronology in Japan, Nara National Research Institute for Cultural Properties (nabunken.go.jp)",

    # ✅ 以下は存在確認済み → そのまま（修正不要だが記録用）
    # Sato Kanzan, The Japanese Sword → ISBN 978-0870115622 ✅
    # Kapp & Yoshihara, The Craft of the Japanese Sword ✅
    # Newland, The Hotei Encyclopedia of Japanese Woodblock Prints ✅
    # Andreas Marks, Publishers of Japanese Woodblock Prints ✅
    # Dalby, Kimono: Fashioning Culture ✅
    # Lugt, Les Marques de Collections ✅
    # Nishi & Hozumi, What Is Japanese Architecture? ✅
    # Tsuji Nobuo, History of Japanese Art ✅
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

# Check for orphaned pairs
orphaned = []
for p in data["pairs"]:
    all_src = p.get("sources", []) + p.get("evidence", [])
    if len(all_src) == 0:
        orphaned.append(p["id"])
        p["verified_by"] = "ai_generated"

data["generated_at"] = now
data["total_pairs"] = len(data["pairs"])

with open("/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/training_pairs.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n=== BIBLIOGRAPHY BATCH 2 RESULTS ===")
print(f"Sources corrected: {corrections_applied}")
print(f"Sources removed (non-existent books): {sources_removed}")
print(f"Pairs orphaned: {len(orphaned)}")
if orphaned:
    for pid in orphaned:
        print(f"  ⚠️ {pid}")
