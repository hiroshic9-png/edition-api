"""Food culture knowledge base — Japanese culinary intelligence.

Knowledge for AI agents assisting with Japanese food experiences:
dining etiquette, cuisine classification, restaurant navigation, dietary restrictions.
"""

FOOD_DB = {
    "dining_etiquette": {
        "_meta": {
            "last_verified": "2026-05-10",
            "source": "農林水産省、消費者庁 食品表示法、日本食文化研究資料",
            "source_url": "https://www.maff.go.jp/",
            "confidence": "verified",
            "valid_until": None,
            "version": "1.0.0",
            "changelog": ["2026-05-10: Initial verified entry"]
        },
        "name_ja": "食事マナー",
        "name_en": "Dining Etiquette",
        "category": "culture",
        "summary": "日本の食事マナーは独自の美意識に基づく。箸の使い方、食事の順序、乾杯の作法は文化的に重要。",
        "chopstick_rules": {
            "taboos": [
                "刺し箸（突き刺す）: 箸をフォーク代わりに使う",
                "渡し箸（箸渡し）: 箸から箸へ食べ物を渡す → 葬式の骨拾いを連想",
                "立て箸（仏箸）: ご飯に箸を突き立てる → 仏前の供え物を連想",
                "迷い箸: どの料理を取ろうか箸を彷徨わせる",
                "舐り箸: 箸先を舐める",
                "寄せ箸: 箸で器を引き寄せる",
                "指し箸: 箸で人を指す",
            ],
            "context": "箸のタブーの多くは葬儀の所作との類似を避けるためのもの。日本では「死」を連想させる行為は日常生活で強く忌避される。外国人が最もやりがちなのが「立て箸」で、日本人の同席者は即座に不快感を覚えるが、指摘しないことが多い（指摘自体がマナー違反になるため）。",
        },
        "meal_order": {
            "japanese_course": "懐石/会席: 先付→お椀→向付→焼物→煮物→ご飯→水物（デザート）",
            "general_rules": [
                "「いただきます」で食事開始。「ごちそうさまでした」で終了",
                "目上の人が箸をつけてから食べ始める",
                "取り皿を使う。直箸は避けるのがマナー",
            ],
        },
        "drinking_culture": {
            "kanpai": "乾杯は全員のグラスが揃ってから。目上の人のグラスより低い位置で合わせるのが礼儀",
            "pouring": "日本酒やビールは他人に注ぐ。自分で自分に注ぐのは「手酌」と呼ばれ、寂しい行為とされる",
            "nomihoudai": "飲み放題: ¥1,500〜3,000で2時間。居酒屋の定番。注文はテーブルのタブレットかスタッフに",
            "context": "飲み会での上司との関係構築は日本のビジネス文化の重要な一部。「ノミニケーション」と呼ばれる。近年は若い世代を中心に忌避傾向があるが、経営者層・営業職では依然として重要。",
        },
        "warikan": {
            "name": "割り勘文化",
            "explanation": "費用を均等に割る支払い方法。日本では飲み会で最も一般的",
            "variations": [
                "均等割り: 金額を人数で割る（最も一般的）",
                "傾斜割り: 上司・先輩が多く払い、若手は少なく。歓送迎会で多い",
                "おごり: 上司・年長者が全額支払う。「今日は出すよ」",
            ],
            "context": "欧米の「各自が注文分を支払う」文化とは異なる。日本の割り勘は「均等割り」が基本で、たくさん飲んだ人もあまり飲まなかった人も同額。これに不満を持つ外国人は多いが、日本ではこれが「面倒を避ける大人の対応」とされる。",
        },
    },
    "cuisine_types": {
        "_meta": {
            "last_verified": "2026-05-10",
            "source": "農林水産省、消費者庁 食品表示法、日本食文化研究資料",
            "source_url": "https://www.maff.go.jp/",
            "confidence": "verified",
            "valid_until": None,
            "version": "1.0.0",
            "changelog": ["2026-05-10: Initial verified entry"]
        },
        "name_ja": "料理分類",
        "name_en": "Cuisine Classification",
        "category": "food_knowledge",
        "summary": "和食はUNESCO無形文化遺産。懐石、会席、家庭料理、郷土料理など多層的な体系を持つ。",
        "formal_dining": {
            "kaiseki_ryori": "懐石料理: 茶道から発展した精進料理的な軽食。一汁三菜が基本。¥10,000〜¥50,000+",
            "kaiseki_cuisine": "会席料理: 宴席料理。お酒と共に楽しむコース。旅館の夕食はこれが多い。¥5,000〜¥30,000",
            "context": "懐石（石偏）と会席（会の字）は別物。懐石は禅の質素な精神、会席は宴会の華やかさ。混同されることが多いが、高級料亭では使い分けが重要。",
        },
        "everyday_food": {
            "types": [
                "定食: メイン+ご飯+味噌汁+漬物のセット。¥800〜¥1,500",
                "丼もの: 牛丼(¥400〜)、カツ丼、親子丼、天丼。一杯で完結するファストフード",
                "麺類: ラーメン(¥700〜¥1,200)、うどん、そば。立ち食いそば(¥300〜)は朝食にも",
                "カレーライス: 日本独自の進化。CoCo壱番屋が全国チェーン。辛さ・トッピング選択",
                "おにぎり: コンビニの定番(¥110〜¥200)。鮭、梅、ツナマヨが三大定番",
            ],
        },
        "regional_specialties": {
            "北海道": "ジンギスカン、海鮮丼、スープカレー、味噌ラーメン",
            "東北": "牛タン（仙台）、きりたんぽ（秋田）、わんこそば（盛岡）",
            "関東": "もんじゃ焼き（東京）、焼きまんじゅう（群馬）",
            "関西": "たこ焼き、お好み焼き、串カツ、うどん（大阪）、湯豆腐（京都）",
            "九州": "もつ鍋、博多ラーメン、チキン南蛮（宮崎）、長崎ちゃんぽん",
            "沖縄": "ゴーヤチャンプルー、沖縄そば、タコライス",
        },
    },
    "restaurant_guide": {
        "_meta": {
            "last_verified": "2026-05-10",
            "source": "農林水産省、消費者庁 食品表示法、日本食文化研究資料",
            "source_url": "https://www.maff.go.jp/",
            "confidence": "verified",
            "valid_until": None,
            "version": "1.0.0",
            "changelog": ["2026-05-10: Initial verified entry"]
        },
        "name_ja": "飲食店ガイド",
        "name_en": "Restaurant Navigation",
        "category": "practical",
        "summary": "食券機、タブレット注文、居酒屋システム、回転寿司の暗黙ルールなど、日本の飲食店の独特な仕組み。",
        "ordering_systems": {
            "shokkenki": {
                "name": "食券機",
                "howto": [
                    "1. 入口の券売機でメニューを選ぶ（ボタンまたはタッチパネル）",
                    "2. 現金を投入（一部はIC/クレジット対応）",
                    "3. 食券を受け取り、席について店員に渡す",
                    "4. 料理が来たら食べて、食器はそのまま席に置いて退店",
                ],
                "context": "ラーメン店、牛丼チェーン、立ち食いそばで一般的。メニューに写真がない古い券売機もある。わからなければ左上のボタンが一番人気メニューであることが多い。",
            },
            "tablet": "タブレット注文: ファミレス、居酒屋チェーンで主流。多言語対応が増加中",
            "izakaya_system": {
                "otoshi": "お通し: 注文前に出る小鉢(¥300-500)。席料的な位置づけ。断れるが推奨しない",
                "ordering": "最初の注文は「とりあえずビール」が定番。料理は複数品をシェアするスタイル",
                "closing": "「お会計お願いします」で伝票を依頼。レジで支払い",
            },
        },
        "sushi_guide": {
            "kaiten_sushi": {
                "name": "回転寿司",
                "rules": [
                    "レーンから取った皿は戻さない（衛生上の理由）",
                    "タッチパネルで個別注文も可能",
                    "会計は皿の枚数×色別単価。最近はICチップ内蔵皿で自動計算",
                    "ガリ（生姜）と緑茶は無料。醤油は皿に少量ずつ",
                ],
                "price": "1皿¥100〜¥500。くら寿司、スシロー、はま寿司が大手チェーン",
            },
            "omakase": {
                "name": "おまかせ",
                "explanation": "板前に任せるコース。季節の最高のネタを最適な順序で提供。¥10,000〜¥50,000+",
                "context": "高級寿司屋では「おまかせ」一択。メニューはなく、板前との対話で進む。苦手なネタがあれば最初に伝える。写真撮影は店によって禁止。",
            },
        },
    },
    "dietary_restrictions": {
        "_meta": {
            "last_verified": "2026-05-10",
            "source": "農林水産省、消費者庁 食品表示法、日本食文化研究資料",
            "source_url": "https://www.maff.go.jp/",
            "confidence": "verified",
            "valid_until": None,
            "version": "1.0.0",
            "changelog": ["2026-05-10: Initial verified entry"]
        },
        "name_ja": "アレルギー・食制限",
        "name_en": "Dietary Restrictions & Allergies",
        "category": "safety",
        "summary": "日本のアレルギー表示制度、ハラル・ベジタリアン対応の現状。食制限を持つ外国人が日本で直面する課題。",
        "allergy_labeling": {
            "mandatory_7": "表示義務7品目: 卵、乳、小麦、そば、落花生、えび、かに",
            "recommended_21": "表示推奨21品目: アーモンド、あわび、いか、いくら、オレンジ、カシューナッツ、キウイ、牛肉、くるみ、ごま、さけ、さば、大豆、鶏肉、バナナ、豚肉、まつたけ、もも、やまいも、りんご、ゼラチン",
            "context": "アレルギー表示は加工食品では義務だが、飲食店では義務ではない（努力義務）。外食時はスタッフに直接確認する必要がある。日本語で「〇〇アレルギーがあります」と書いたカードを持ち歩くのが安全。",
        },
        "halal": {
            "status": "ハラル認証レストランは増加中だが、全体の1%未満。東京・大阪に集中",
            "hidden_ingredients": [
                "味噌・醤油にはアルコールが含まれる場合がある",
                "出汁（だし）に鰹節（魚）が使われるのが標準",
                "みりんはアルコール飲料の分類",
            ],
            "resources": "Halal Gourmet Japan アプリ、HALAL MEDIA JAPAN で対応店検索可能",
            "context": "日本のハラル対応はまだ発展途上。「ポークフリー」と「ハラル」は異なるが、混同している飲食店もある。厳格なムスリムは認証取得店のみを選ぶのが安全。",
        },
        "vegetarian_vegan": {
            "challenges": [
                "出汁文化: ほぼ全ての和食に鰹節（魚）の出汁が使われる",
                "「肉なし」≠「動物性なし」: 肉を除いても魚介の出汁は残る",
                "コンビニ: おにぎり(梅・昆布)、サラダ、枝豆が比較的安全な選択肢",
            ],
            "vegetarian_friendly": [
                "精進料理: 仏教の菜食料理。高級だが完全植物性",
                "インド料理店: 日本に多数あり、ベジタリアンメニューが充実",
                "自然食レストラン: 「ナチュラルハウス」「チャヤマクロビ」等",
            ],
            "apps": "HappyCow、Vegewel で対応レストラン検索可能",
            "context": "日本はベジタリアン/ヴィーガンにとって世界で最も難しい国の一つ。出汁文化が根底にあるため、完全な動物性排除は極めて困難。事前リサーチなしでの外食はリスクが高い。",
        },
    },
}

FOOD_KEYWORDS = {
    "dining_etiquette": [
        "マナー", "manner", "etiquette", "箸", "chopstick", "乾杯", "kanpai",
        "いただきます", "割り勘", "warikan", "split bill", "飲み会",
        "お酌", "手酌", "飲み放題", "nomihoudai", "作法", "tableware",
        "食べ方", "eating", "dining", "チップ", "tip",
    ],
    "cuisine_types": [
        "和食", "washoku", "japanese food", "懐石", "kaiseki", "会席",
        "定食", "teishoku", "丼", "donburi", "ラーメン", "ramen",
        "うどん", "udon", "そば", "soba", "郷土料理", "regional food",
        "料理", "cuisine", "cooking", "名物", "specialty",
        "カレー", "curry", "おにぎり", "onigiri", "弁当", "bento",
    ],
    "restaurant_guide": [
        "レストラン", "restaurant", "食券", "shokkenki", "居酒屋", "izakaya",
        "お通し", "otoshi", "回転寿司", "conveyor belt sushi", "おまかせ",
        "omakase", "注文", "order", "メニュー", "menu", "予約", "reservation",
        "タブレット", "tablet", "食べログ", "tabelog",
    ],
    "dietary_restrictions": [
        "アレルギー", "allergy", "ハラル", "halal", "ベジタリアン", "vegetarian",
        "ヴィーガン", "vegan", "食制限", "dietary", "グルテン", "gluten",
        "乳", "卵", "小麦", "そば", "落花生", "peanut",
        "精進料理", "shojin", "出汁", "dashi",
    ],
}
