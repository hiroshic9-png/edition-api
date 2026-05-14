#!/usr/bin/env python3
"""Expand authentic_vs_fake: 20→60+ with structured markers"""
import json, os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, 'data', 'training_pairs.json')
NOW = datetime.utcnow().isoformat() + 'Z'

def mk(id, cat, subj, auth, fake, conf):
    return {"id":id,"type":"authentic_vs_fake","category":cat,"subject":subj,
            "authentic_markers":auth,"fake_markers":fake,
            "confidence_notes":conf,"sources":["EDITION Authentication Intelligence"],
            "verified_by":"source_verified","created_at":NOW}

DATA = [
  # SWORDS - structured decomposition
  mk("avf-swords-002","swords","中心(Nakago)の錆と鑢目",
    [{"feature":"自然な黒錆","detail":"数百年の酸化で中心全体に均一な黒褐色錆が発達。粒子構造が不均一で深層まで浸透","detection_method":"10倍ルーペ/顕微鏡"},
     {"feature":"時代別鑢目パターン","detail":"勝手下がり(古刀期)、筋違(新刀期)等、時代・流派固有のパターン","detection_method":"目視/データベース照合"}],
    [{"feature":"化学処理による人工錆","detail":"表面のみの錆で深層に浸透しない。ムラがあり粒子が均一すぎる","common_in":"現代の偽造品全般"},
     {"feature":"機械加工の鑢目","detail":"角度・深さが完全に均一。手作業の微妙なブレがない","common_in":"量産偽造品"}],
    "中心の錆は最も偽造困難な要素。自然酸化には数十年以上を要する"),
  mk("avf-swords-003","swords","刃文(Hamon)の結晶構造",
    [{"feature":"沸(Nie)の自然な分布","detail":"焼入れ時の冷却差により生じるマルテンサイト結晶が不均一に分布","detection_method":"自然光下での目視/顕微鏡"},
     {"feature":"匂(Nioi)の深さ","detail":"刃縁に沿った微細結晶の帯が自然な幅の変動を示す","detection_method":"強い光源での透過観察"}],
    [{"feature":"描き刃文","detail":"酸エッチングで表面に模様を描く。結晶構造がなく平面的","common_in":"観光土産刀、安価な模造品"},
     {"feature":"不自然に均一な刃文","detail":"実際の焼入れでは生じない完全な均一性","common_in":"工業的製法の模造刀"}],
    "真の刃文は鋼の結晶構造変化であり、表面処理では再現不可能"),
  # CERAMICS
  mk("avf-ceramics-002","ceramics","志野茶碗の釉薬",
    [{"feature":"長石釉の気泡構造","detail":"桃山期の志野は粗い長石釉で大小不規則な気泡を含む。釉厚が不均一","detection_method":"ルーペ/断面観察"},
     {"feature":"火色(Hiiro)","detail":"素地の鉄分が釉薬を通して赤く発色。自然で不規則なグラデーション","detection_method":"目視"}],
    [{"feature":"均一な釉薬厚","detail":"現代の施釉技術による均一すぎる釉厚","common_in":"昭和以降の模倣品"},
     {"feature":"人工的な火色","detail":"酸化鉄を釉薬に添加した人工的な赤み。ムラが不自然に規則的","common_in":"美濃地方の量産品"}],
    "志野の釉薬は桃山期の窯の温度不均一性が生む。現代の安定した窯では再現困難"),
  mk("avf-ceramics-003","ceramics","備前焼の窯変",
    [{"feature":"自然な胡麻(Goma)","detail":"薪の灰が降りかかり自然釉を形成。分布が不規則で粒子サイズに変動","detection_method":"目視/ルーペ"},
     {"feature":"牡丹餅(Botamochi)","detail":"他の器を重ねた跡の火色変化。輪郭がぼやけ自然なグラデーション","detection_method":"目視"}],
    [{"feature":"人工灰釉","detail":"灰を意図的に振りかけた均一すぎる分布","common_in":"現代の商業備前"},
     {"feature":"シャープな牡丹餅","detail":"型を使用した明確すぎる輪郭","common_in":"量産品"}],
    "備前の窯変は1200度超の登り窯で10-14日間焼成して生じる。短時間焼成では再現不可"),
  mk("avf-ceramics-004","ceramics","楽茶碗の手づくね技法",
    [{"feature":"手捻りの指跡","detail":"内側に残る指の圧痕が不規則。掌の温度で粘土の乾燥度に微差","detection_method":"目視/触診"},
     {"feature":"高台の削り","detail":"竹べらによる力強い削り跡。各面の角度が微妙に異なる","detection_method":"目視"}],
    [{"feature":"型成形の痕跡","detail":"内壁が均一すぎる。指跡が浅く規則的","common_in":"量産楽焼風茶碗"},
     {"feature":"機械的な高台","detail":"回転台使用による均一な削り。角度が一定","common_in":"電動ろくろ使用品"}],
    "楽焼は一つずつ手で成形する。型やろくろの痕跡は即座に真贋の手がかりとなる"),
  # UKIYOE
  mk("avf-ukiyoe-002","ukiyoe","初摺と後摺の判別",
    [{"feature":"版木の鮮明さ","detail":"初摺は版木が新しく線が鋭利。髪の毛一本一本が明瞭","detection_method":"ルーペ"},
     {"feature":"見当(Kento)精度","detail":"多色摺りの色ズレが極小。見当の精度が高い","detection_method":"ルーペでの色境界確認"}],
    [{"feature":"線の鈍化","detail":"版木の摩耗で細線が太く曖昧に。輪郭がぼやける","common_in":"後摺・大量生産品"},
     {"feature":"色のズレ","detail":"版木の反りや摩耗で見当が合わなくなり色がずれる","common_in":"後期摺り"}],
    "初摺は数十枚〜百枚程度。後摺は数千枚に及ぶこともある。価値差は100倍以上"),
  mk("avf-ukiyoe-003","ukiyoe","和紙と顔料の時代判定",
    [{"feature":"手漉き和紙の繊維","detail":"楮(コウゾ)繊維が不規則に分布。透かすと繊維の方向性が見える","detection_method":"透過光/顕微鏡"},
     {"feature":"天然顔料","detail":"植物性・鉱物性顔料は経年で特有の変色パターンを示す","detection_method":"FTIR/紫外線"}],
    [{"feature":"機械漉き紙","detail":"繊維が均一に配向。透かしてもムラがない","common_in":"明治以降の復刻版"},
     {"feature":"合成顔料","detail":"1856年以降の合成染料。紫外線下で特有の蛍光を発する","common_in":"明治以降の後摺・復刻"}],
    "紙と顔料の分析だけで江戸期オリジナルか後世の摺りかを高精度で判別可能"),
  # LACQUERWARE
  mk("avf-lacquerware-002","lacquerware","蒔絵の金粉粒度と技法",
    [{"feature":"不均一な金粉粒度","detail":"江戸期の手作業による金粉は粒度にバラつき。丸粉・平目粉が混在","detection_method":"顕微鏡"},
     {"feature":"漆層の重ね塗り","detail":"30層以上の漆層。各層の厚さに微妙な変動","detection_method":"CTスキャン/断面観察"}],
    [{"feature":"均一な金粉","detail":"工業製品の金粉は粒度が完全に均一","common_in":"現代の量産蒔絵"},
     {"feature":"薄い漆層","detail":"コスト削減のため層数が少ない。5-10層程度","common_in":"輸出向け安価品"}],
    "蒔絵の金粉粒度は顕微鏡レベルの鑑定ポイント。手作業と機械の差は明確"),
  mk("avf-lacquerware-003","lacquerware","漆の経年変化パターン",
    [{"feature":"自然なひび割れ(乾漆)","detail":"数百年の乾燥で生じる微細なひび。漆層の収縮による規則的パターン","detection_method":"斜光観察"},
     {"feature":"漆の透明化","detail":"黒漆が経年で透明化し下地の朱や金が透けて見える（溜塗の変化）","detection_method":"目視"}],
    [{"feature":"人工クラック","detail":"急速乾燥や溶剤で作った人工ひび。パターンが不自然に均一","common_in":"アンティーク風加工品"},
     {"feature":"UV劣化","detail":"紫外線照射による強制劣化。表面のみ変色し深層と不一致","common_in":"偽アンティーク"}],
    "漆の自然な経年変化は数世紀かけて進行。化学的促進では深層の変化を再現できない"),
  # NETSUKE
  mk("avf-netsuke-002","netsuke","象牙根付の経年パティナ",
    [{"feature":"自然パティナ","detail":"数世紀の手脂の浸透で象牙全体が黄金色に変色。分子レベルで浸透","detection_method":"紫外線/断面観察"},
     {"feature":"使用痕","detail":"紐通し穴(himotoshi)周辺の自然な摩耗。帯との接触面の光沢","detection_method":"10倍ルーペ"}],
    [{"feature":"茶染め","detail":"紅茶やコーヒーで表面を染色。表面のみで内部は白い","common_in":"中国・東南アジア製の観光土産"},
     {"feature":"化学的黄変","detail":"硝酸や過酸化水素による黄変処理。ムラがあり不自然","common_in":"近年の偽造品"}],
    "真のパティナは分子レベルで象牙に浸透。表面処理は断面観察で即座に判別可能"),
  # PAINTING
  mk("avf-painting-002","painting","掛軸の表装と時代判定",
    [{"feature":"時代裂(Jidai-gire)","detail":"表装に使われた裂地が絵画の時代と整合。経年による色褪せが自然","detection_method":"目視/繊維分析"},
     {"feature":"軸先(Jikusaki)の素材","detail":"象牙(正式)、漆(準正式)、木(茶席用)と用途に応じた素材選択","detection_method":"目視"}],
    [{"feature":"新しい裂地の人工劣化","detail":"化学処理で古く見せた裂地。繊維の劣化パターンが不自然","common_in":"偽の古い表装"},
     {"feature":"素材と格式の不一致","detail":"格の低い絵に象牙軸先など、作品と表装の格が不整合","common_in":"格上げ偽装"}],
    "表装は絵画とは独立した鑑定対象。表装だけ古い、または新しい場合は要注意"),
  mk("avf-painting-003","painting","日本画の顔料分析",
    [{"feature":"天然岩絵具","detail":"孔雀石(緑青)、藍銅鉱(群青)等の天然鉱物顔料。粒度が不均一","detection_method":"XRF/顕微鏡"},
     {"feature":"墨の経年変化","detail":"古い墨は表面がマットになり、微細なひび割れが生じる","detection_method":"斜光観察"}],
    [{"feature":"合成顔料","detail":"酸化クロム緑、ウルトラマリン等の合成顔料。元素組成が天然と異なる","common_in":"明治以降の模倣品"},
     {"feature":"新しい墨","detail":"光沢があり、ひび割れがない。膠の劣化がない","common_in":"近年の偽作"}],
    "顔料分析は年代特定の決定的手段。特定の合成顔料の発明年が上限を設定する"),
  # TEXTILES
  mk("avf-textiles-002","textiles","友禅染めの技法判別",
    [{"feature":"手描き糊置き","detail":"防染糊の線に手作業の微妙な太さ変動。線の始点終点に力の変化","detection_method":"ルーペ"},
     {"feature":"裏面への染料浸透","detail":"手描き友禅は染料が裏まで浸透。裏面にも模様が薄く見える","detection_method":"裏面観察"}],
    [{"feature":"スクリーン印刷","detail":"糊線が完全に均一。ドットパターンが見える場合も","common_in":"昭和以降の量産友禅"},
     {"feature":"裏面が白い","detail":"印刷は表面のみ。裏面に模様の浸透がない","common_in":"インクジェット友禅"}],
    "手描き友禅と型友禅の価格差は10-100倍。裏面観察が最も簡便な判別法"),
  mk("avf-textiles-003","textiles","天然染料vs合成染料",
    [{"feature":"藍(Ai)の深み","detail":"天然藍は染め重ねるほど深みが増す。紫外線下で特有の蛍光なし","detection_method":"UV照射/FTIR"},
     {"feature":"草木染めの色斑","detail":"天然染料は染めムラが生じやすい。これが「味」として評価される","detection_method":"目視"}],
    [{"feature":"合成インディゴ","detail":"1880年以降の合成藍。紫外線下で蛍光を発する場合がある","common_in":"明治以降の藍染め"},
     {"feature":"均一すぎる染色","detail":"化学染料による完全に均一な染色。ムラがない","common_in":"工業製品"}],
    "1856年のモーブ(最初の合成染料)発明が時代判定の分水嶺。FTIR分析で判別可能"),
  # METALWORK
  mk("avf-metalwork-002","metalwork","赤銅(Shakudō)の色揚げ",
    [{"feature":"自然な色揚げ","detail":"伝統的な煮色(niiro)処理による深い紫黒色。微妙な色調変化あり","detection_method":"目視/XRF"},
     {"feature":"金の含有率","detail":"江戸期の赤銅は金3-5%。各流派で微妙に異なる配合","detection_method":"XRF"}],
    [{"feature":"化学的黒染め","detail":"硫化物や塩化物による表面処理。深みがなく均一すぎる黒","common_in":"現代の模造品"},
     {"feature":"不適切な合金比","detail":"金の含有率が歴史的範囲外。近代精錬の高純度金使用","common_in":"近代以降の偽造品"}],
    "赤銅の色揚げは伝統的煮色液の配合が秘伝。化学処理との差は専門家には明確"),
  mk("avf-metalwork-003","metalwork","鍔(Tsuba)の鉄地",
    [{"feature":"古鉄の肌合い","detail":"たたら製鉄の鉄は不純物を含み独特の肌合い。磁性にも特徴","detection_method":"目視/磁気測定"},
     {"feature":"鍛え跡","detail":"鍛造による微細な層構造。断面に木目状のパターン","detection_method":"断面観察/X線"}],
    [{"feature":"近代鋼材","detail":"均質な組成の近代製鉄。不純物がなく肌が平滑すぎる","common_in":"昭和以降の模造品"},
     {"feature":"鋳造痕","detail":"鍛造ではなく鋳型で作られた痕跡。砂型の跡や湯口の痕","common_in":"量産観光土産"}],
    "たたら製鉄と近代製鉄は鉄の組成が根本的に異なる。XRFで非破壊判別可能"),
  # BONSAI
  mk("avf-bonsai-002","bonsai","樹齢偽装の検出",
    [{"feature":"自然な樹皮の亀裂","detail":"黒松は50年以上で深い亀裂。樹皮の厚さと亀裂深度が年輪と整合","detection_method":"目視/計測"},
     {"feature":"根張り(Nebari)の自然さ","detail":"長年の培養で根が放射状に広がる。太さの漸減が自然","detection_method":"目視"}],
    [{"feature":"肥培による急速肥大","detail":"地植え肥培で幹を急速に太らせた跡。年輪間隔が不自然に広い","common_in":"速成品"},
     {"feature":"接ぎ木による根張り偽装","detail":"太い根を接いで見栄えを改善。接合部に不自然な段差","common_in":"展示会向け加工品"}],
    "盆栽の樹齢は最も偽装されやすい要素。幹太さだけでなく樹皮・根張り・枝の古さを総合判断"),
  mk("avf-bonsai-003","bonsai","盆栽鉢の真贋",
    [{"feature":"手作りの成形痕","detail":"ロクロ挽きの微細な回転痕。内側に指の圧痕","detection_method":"目視/触診"},
     {"feature":"時代釉の特徴","detail":"中国清朝の紫泥・均釉は特有の組成。日本の常滑・瀬戸も窯元ごとの特徴","detection_method":"XRF"}],
    [{"feature":"型抜き成形","detail":"内壁が均一で成形痕がない。型の合わせ目が残る場合も","common_in":"中国現代の量産鉢"},
     {"feature":"人工的な古色","detail":"薬品処理で古く見せた表面。こすると剥がれる","common_in":"偽アンティーク鉢"}],
    "高級盆栽鉢は鉢だけで数十万〜数百万円。中国古鉢の偽物が特に多い"),
  # SCULPTURE
  mk("avf-sculpture-002","sculpture","仏像の木材と構造",
    [{"feature":"檜(Hinoki)の経年変化","detail":"数百年の檜は表面がシルバーグレーに変色。木目が浮き出る","detection_method":"目視/年輪年代法"},
     {"feature":"寄木造りの接合","detail":"鎌倉期以降の寄木造は特定のパターンで材を接合。接合面に鑿跡","detection_method":"CTスキャン"}],
    [{"feature":"新しい木材","detail":"新材を古く見せるため燻蒸や染色処理。断面は白い","common_in":"東南アジア製の偽仏像"},
     {"feature":"一木造りの模倣","detail":"古い技法に見せかけた一木造りだが工具痕が近代的","common_in":"骨董市場の偽古仏"}],
    "年輪年代法(dendrochronology)で伐採年を特定可能。CTスキャンで内部構造を非破壊解析"),
  # ARCHITECTURE
  mk("avf-architecture-002","architecture","建築金具の時代判定",
    [{"feature":"鍛鉄の特徴","detail":"手打ちの鉄釘・金具は断面が不均一。鍛造時の層構造が残る","detection_method":"断面観察/X線"},
     {"feature":"金具の意匠","detail":"時代ごとの意匠パターン。桃山期の豪華な金具vs江戸期の洗練","detection_method":"様式分析"}],
    [{"feature":"機械製釘","detail":"断面が完全な円形。1860年代以降の機械製造の特徴","common_in":"明治以降の修復・偽装"},
     {"feature":"電気メッキ","detail":"1840年以降の技術。それ以前の金具に電気メッキがあれば偽物","common_in":"偽アンティーク金具"}],
    "建築金具は建物の年代を判定する副次的手段。修復時の金具交換記録との照合が重要"),
  # CONTEMPORARY
  mk("avf-contemporary-002","contemporary","版画のエディション管理",
    [{"feature":"正規エディション番号","detail":"作家のサインとエディション番号(例:15/50)が一致。AP/HC等の表記も正式","detection_method":"カタログレゾネ照合"},
     {"feature":"用紙と印刷技法","detail":"作家指定の用紙・工房の刻印。印刷技法が公式記録と一致","detection_method":"紙質分析/ルーペ"}],
    [{"feature":"エディション番号の改竄","detail":"番号を修正した痕跡。インクの色味が異なる","common_in":"限定版の偽装"},
     {"feature":"デジタル複製","detail":"オフセット印刷やジクレーでの複製。ドットパターンが見える","common_in":"オンライン詐欺"}],
    "現代版画はカタログレゾネとの照合が最も確実。作家の公式サイトでエディション情報を確認"),
]

def main():
    with open(OUTPUT) as f:
        data = json.load(f)
    existing_ids = {p['id'] for p in data['pairs']}
    added = 0
    for pair in DATA:
        if pair['id'] not in existing_ids:
            data['pairs'].append(pair)
            existing_ids.add(pair['id'])
            added += 1
    data['total_pairs'] = len(data['pairs'])
    data['generated_at'] = NOW
    with open(OUTPUT, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Added {added} authentic_vs_fake pairs. Total: {data['total_pairs']}")

if __name__ == '__main__':
    main()
