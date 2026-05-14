#!/usr/bin/env python3
"""
書誌情報の修正: 実在が確認できない書籍引用を修正または除去
照合結果に基づく厳密な修正
"""
import json, datetime

now = datetime.datetime.utcnow().isoformat() + "Z"

# 照合結果: 不正確な引用 → 正確な引用 or 除去
CORRECTIONS = {
    # ❌ 書籍として存在しない
    "Chiappa, Hiroshige Catalogue": None,  # Chiappaはオンラインindex作成者。書籍ではない
    "Thompson, Censor Seals on Japanese Prints": None,  # 著者はKendon Ishii
    "Shimada, Japanese Painting Formats": None,  # この書名の書籍は存在しない
    "Hayakawa, The Art of Japanese Scroll Mounting": None,  # この書名の書籍は存在しない
    "Keyes, impression quality analysis": None,  # 独立した書籍ではない
    "Keyes, Hiroshige's Tokaido printing analysis": None,  # 展覧会カタログのエッセイ、独立書籍ではない
    
    # ⚠️ タイトル不正確 → 正確なタイトルに修正
    "Ohmura, Military Swords of Japan": "Ohmura Tomoyuki, ohmura-study.net (online research resource)",  # オンラインリソース
    "Sumiyoshi, Japanese Woodworking Joints": "Sumiyoshi & Matsui, Wood Joints in Classical Japanese Architecture, Kajima, 1991",
    "Cort, Japanese Ceramics Technical Studies": "Cort, Louise Allison — ceramics research (Smithsonian)",  # 特定書名は確認不可
    "Cort, Shigaraki Potters Valley": "Cort, Shigaraki, Potters' Valley, Cambridge UP, 1979",
    
    # ⚠️ 重複統合
    "Chong, Tokyo 1955-1970": "Chong, Tokyo 1955-1970: A New Avant-Garde, MoMA, 2012",
    "Mori, History of Japanese Buddhist Sculpture": "Mori Hisashi, Japanese Buddhist Sculpture, trans. Eckel, 1974",
    "Rice, Pottery Analysis": "Rice, Prudence M., Pottery Analysis: A Sourcebook, U of Chicago Press, 2nd ed 2015",
    "Honma & Sato, Nihonto Meikan oshigata volumes": "Honma & Sato, Nihonto Meikan (vol. 1-3), Yuzankaku, 1975-1976",
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
                    print(f"  CORRECTED in {p['id']}: {s} → {replacement}")
            else:
                new_sources.append(s)
        p[field] = new_sources

# Check: any pairs now left with zero sources?
orphaned = []
for p in data["pairs"]:
    all_src = p.get("sources", []) + p.get("evidence", [])
    if len(all_src) == 0:
        orphaned.append(p["id"])
        # Downgrade verified_by
        p["verified_by"] = "ai_generated"

data["generated_at"] = now
data["total_pairs"] = len(data["pairs"])

with open("/Users/hiroshisato/.gemini/antigravity/scratch/edition-api/data/training_pairs.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n=== BIBLIOGRAPHY CLEANUP RESULTS ===")
print(f"Sources corrected: {corrections_applied}")
print(f"Sources removed (non-existent): {sources_removed}")
print(f"Pairs orphaned (zero sources after cleanup): {len(orphaned)}")
if orphaned:
    for pid in orphaned:
        print(f"  ⚠️ {pid} — now has zero sources, downgraded to ai_generated")
