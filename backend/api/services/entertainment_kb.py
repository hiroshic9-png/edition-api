"""Entertainment knowledge base — Japan pop culture and event intelligence.

Structured knowledge for AI agents supporting entertainment, fan engagement,
oshi-katsu (推し活), and event attendance in Japan.
"""

ENTERTAINMENT_DB = {
    "oshikatsu": {
        "name_ja": "推し活",
        "name_en": "Oshi-katsu (Fan Support Activities)",
        "category": "fan_culture",
        "summary": "「推し」（お気に入りのアイドル・キャラクター等）を応援する活動全般。日本独自のファンカルチャーで、経済規模は数千億円。",
        "activities": [
            "ライブ・コンサートへの参加",
            "グッズ・物販の購入",
            "聖地巡礼（作品の舞台となった場所への訪問）",
            "推しカラーのファッション・ネイル",
            "SNSでの応援投稿・ファンアート",
            "生誕祭（推しの誕生日を祝うイベント）",
            "応援広告（駅・ビル等に推しの広告を出す）",
        ],
        "ticket_acquisition": {
            "methods": [
                "ファンクラブ先行（最も確実。年会費¥3,000-10,000が一般的）",
                "一般発売（プレイガイド: チケットぴあ、ローソンチケット、イープラス）",
                "抽選販売が主流（先着順は少ない）",
            ],
            "resale": {
                "legal": "チケトレ（公式リセール）、チケット流通センター等の公式ルート",
                "illegal": "転売は「チケット不正転売禁止法」（2019年施行）で違法。定価超えの転売は罰則あり",
            },
        },
        "economic_scale": "推し活市場は約7,000億円（2023年推定）。ファン1人あたりの年間支出は平均約4万円",
    },
    "anime_manga": {
        "name_ja": "アニメ・マンガ",
        "name_en": "Anime & Manga",
        "category": "content",
        "summary": "日本のアニメ・マンガ産業は世界的に影響力を持つ。聖地巡礼、コミケ、アニメイト等の文化が独自のエコシステムを形成。",
        "major_events": [
            {"name": "コミックマーケット（コミケ）", "period": "8月・12月（年2回）", "venue": "東京ビッグサイト",
             "scale": "参加者約17万人/日（3日間）", "tips": "サークル参加は半年前に申込。一般参加もリストバンド制に移行"},
            {"name": "AnimeJapan", "period": "3月", "venue": "東京ビッグサイト",
             "scale": "約15万人", "tips": "業界最大の商談会も併設"},
            {"name": "ジャンプフェスタ", "period": "12月", "venue": "幕張メッセ",
             "scale": "約15万人", "tips": "少年ジャンプ系の最新情報発表"},
            {"name": "ワンダーフェスティバル（ワンフェス）", "period": "2月・7月", "venue": "幕張メッセ",
             "scale": "約5万人", "tips": "フィギュア・模型の祭典。当日版権制度あり"},
        ],
        "pilgrimage_spots": {
            "description": "聖地巡礼（せいちじゅんれい）= アニメ・マンガの舞台となった実在の場所を訪問すること",
            "famous_examples": [
                {"work": "スラムダンク", "location": "鎌倉高校前駅の踏切（神奈川県）"},
                {"work": "君の名は。", "location": "須賀神社の階段（東京・四谷）"},
                {"work": "鬼滅の刃", "location": "竈門神社（福岡県太宰府市）"},
                {"work": "ラブライブ！", "location": "神田明神（東京・秋葉原）"},
            ],
            "economic_impact": "聖地巡礼による地方経済効果は年間数百億円規模",
        },
        "shopping": [
            {"name": "秋葉原（東京）", "description": "電気街→オタク文化の中心地。アニメイト、まんだらけ、ゲーマーズ等が集結"},
            {"name": "中野ブロードウェイ（東京）", "description": "レアグッズ・ヴィンテージトイの聖地。まんだらけ本店"},
            {"name": "日本橋（大阪）", "description": "関西のオタク文化の中心地。でんでんタウン"},
            {"name": "アニメイト", "description": "全国120店舗以上のアニメ・マンガ専門ショップチェーン"},
        ],
    },
    "live_entertainment": {
        "name_ja": "ライブエンターテインメント",
        "name_en": "Live Entertainment",
        "category": "events",
        "summary": "日本のライブエンタメ市場は約6,000億円。独自のルールとマナーが存在する。",
        "venue_types": {
            "arenas": [
                {"name": "東京ドーム", "capacity": "約55,000人", "notes": "最大級のコンサート会場"},
                {"name": "横浜アリーナ", "capacity": "約17,000人"},
                {"name": "さいたまスーパーアリーナ", "capacity": "最大37,000人"},
                {"name": "京セラドーム大阪", "capacity": "約55,000人"},
                {"name": "日本武道館", "capacity": "約14,000人", "notes": "アーティストの「聖地」とされる"},
            ],
            "live_houses": {
                "description": "小規模なライブハウス。キャパ100-2,000人程度",
                "famous": ["Zepp", "LIQUIDROOM", "新宿BLAZE", "下北沢SHELTER"],
            },
        },
        "concert_manners": [
            "ペンライト（サイリウム）の色はアーティスト・メンバーごとに決まっている",
            "コール（掛け声）は曲ごとにパターンが決まっている（事前に調べる）",
            "撮影・録音は原則禁止（許可されている場合を除く）",
            "スタンディングの場合、前方はモッシュ・ダイブが起きることがある",
            "物販は開演の数時間前から長蛇の列。人気グッズは即売切れ",
        ],
    },
    "seasonal_events": {
        "name_ja": "季節のイベント",
        "name_en": "Seasonal Events",
        "category": "cultural_events",
        "summary": "日本の四季に合わせた文化的イベント。旅行やビジネスの計画に影響する。",
        "events": [
            {"month": "1-2月", "name": "初詣・節分", "description": "神社仏閣への新年の参拝。恵方巻きの文化"},
            {"month": "3-4月", "name": "花見（桜）", "description": "桜の開花に合わせた花見。東京の見頃は3月下旬〜4月上旬"},
            {"month": "7-8月", "name": "花火大会・夏祭り", "description": "全国各地で花火大会。浴衣を着て参加する文化"},
            {"month": "8月", "name": "お盆", "description": "先祖の霊を迎える期間。帰省ラッシュ"},
            {"month": "10月", "name": "ハロウィン", "description": "渋谷の仮装が有名だったが2023年以降は規制強化"},
            {"month": "11月", "name": "紅葉", "description": "紅葉狩り。京都が最も有名。見頃は11月中旬〜下旬"},
            {"month": "12月", "name": "イルミネーション・クリスマス", "description": "カップルイベント化。クリスマスケーキとKFCの文化"},
            {"month": "12月31日", "name": "年越し", "description": "除夜の鐘（108回）。年越しそばを食べる"},
        ],
    },
}

ENTERTAINMENT_KEYWORDS = {
    "oshikatsu": [
        "推し", "推し活", "oshi", "ファン", "fan", "アイドル", "idol",
        "ライブ", "live", "コンサート", "concert", "チケット", "ticket",
        "グッズ", "goods", "物販", "merch", "応援", "support",
        "ファンクラブ", "fan club", "生誕祭", "聖地巡礼",
    ],
    "anime_manga": [
        "アニメ", "anime", "マンガ", "manga", "漫画", "comic",
        "コミケ", "comiket", "秋葉原", "Akihabara", "オタク", "otaku",
        "フィギュア", "figure", "コスプレ", "cosplay", "同人", "doujin",
        "聖地巡礼", "pilgrimage", "アニメイト", "animate",
    ],
    "live_entertainment": [
        "ライブ", "live", "コンサート", "concert", "フェス", "festival",
        "東京ドーム", "Tokyo Dome", "武道館", "Budokan", "ペンライト",
        "penlight", "会場", "venue", "チケット", "ticket", "座席", "seat",
    ],
    "seasonal_events": [
        "花見", "hanami", "桜", "cherry blossom", "花火", "fireworks",
        "祭り", "matsuri", "festival", "紅葉", "autumn leaves",
        "イルミネーション", "illumination", "ハロウィン", "Halloween",
        "初詣", "hatsumode", "浴衣", "yukata",
    ],
}
