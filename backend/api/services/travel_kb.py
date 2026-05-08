"""Travel knowledge base — Japan inbound tourism intelligence.

Structured knowledge for AI agents assisting travelers and businesses
operating in Japan's tourism sector.
"""

TRAVEL_DB = {
    "transportation": {
        "name_ja": "交通機関",
        "name_en": "Transportation",
        "category": "infrastructure",
        "summary": "日本の公共交通機関は世界最高水準。鉄道網が発達し、都市間は新幹線、都市内は地下鉄・私鉄が中心。",
        "shinkansen_tips": [
            "Japan Rail Pass: 7日間¥50,000、14日間¥80,000、21日間¥100,000",
            "のぞみ・みずほはJR Pass不可（2023年10月改定）。ひかり・さくらを利用",
            "繁忙期（GW・お盆・年末年始）は指定席の事前予約必須",
        ],
        "ic_cards": "Suica/PASMO/ICOCA等。全国相互利用対応。電車・バス・コンビニで利用可能",
        "taxi_etiquette": [
            "ドアは自動開閉。手で開けない",
            "チップ不要。後部座席に座る",
            "GO/S.RIDE/Uberアプリで配車可能",
        ],
    },
    "accommodation": {
        "name_ja": "宿泊",
        "name_en": "Accommodation",
        "category": "lodging",
        "summary": "旅館・カプセルホテル・ビジネスホテル・民泊など多様な宿泊形態がある。",
        "ryokan_etiquette": [
            "チェックイン時に靴を脱ぐ",
            "大浴場では入浴前に体を洗う",
            "タトゥーは大浴場利用不可の場合あり（貸切風呂推奨）",
            "夕食は18:00-19:00開始が一般的。遅刻不可",
        ],
        "price_ranges": {
            "旅館": "¥10,000〜¥100,000+/泊（一泊二食付き）",
            "ビジネスホテル": "¥5,000〜¥15,000/泊",
            "カプセルホテル": "¥2,500〜¥5,000/泊",
            "民泊": "¥3,000〜¥30,000/泊（年間180日上限の規制あり）",
        },
        "major_chains": ["東横INN", "アパホテル", "ドーミーイン", "コンフォートホテル"],
    },
    "dining": {
        "name_ja": "飲食",
        "name_en": "Dining",
        "category": "food",
        "summary": "東京は世界最多のミシュラン星保有都市。独自の食事マナーと多様な料理ジャンル。",
        "etiquette": [
            "「いただきます」（食前）「ごちそうさまでした」（食後）を言う",
            "箸のタブー: 刺し箸、渡し箸、迷い箸",
            "チップは不要。渡すと失礼になる場合がある",
            "居酒屋の「お通し」は自動的に出る前菜（¥300-500加算）",
            "ラーメンを啜るのはマナー違反ではない",
        ],
        "regional_ramen": {
            "東京": "醤油ラーメン（澄んだスープ）",
            "札幌": "味噌ラーメン（濃厚味噌＋バター・コーン）",
            "博多": "豚骨ラーメン（白濁豚骨スープ＋極細麺）",
            "京都": "鶏白湯ラーメン",
        },
        "payment_tips": [
            "小規模店舗は現金のみが多い。¥10,000-20,000の現金を携帯",
            "PayPay、交通系ICが普及。VISA/Masterが最も対応率が高い",
        ],
    },
    "practical_info": {
        "name_ja": "実用情報",
        "name_en": "Practical Information",
        "category": "visitor_essentials",
        "summary": "訪日旅行者が知っておくべき通信、マナー、安全、医療等の情報。",
        "emergency": {
            "police": "110",
            "fire_ambulance": "119",
            "tourist_hotline": "050-3816-2787（JNTO多言語24時間）",
        },
        "connectivity": [
            "eSIM（Ubigi, Airalo等）: $5-20で7-30日",
            "セブン銀行ATM: 海外カード対応24時間",
            "Japan Wi-Fi auto-connect（NTTアプリ）",
        ],
        "manners": [
            "電車内での通話は禁止。マナーモードに設定",
            "歩きながらの飲食はマナー違反（京都等は条例化）",
            "ゴミ箱は公共の場にほぼない。持ち帰りが原則",
            "温泉ではタオルを湯船に入れない",
            "消費税10%（食品8%）。免税は¥5,000以上から",
        ],
    },
}

TRAVEL_KEYWORDS = {
    "transportation": [
        "交通", "transport", "電車", "train", "新幹線", "shinkansen",
        "地下鉄", "subway", "タクシー", "taxi", "バス", "bus", "JR",
        "Suica", "PASMO", "IC card", "JR Pass", "鉄道", "移動",
        "切符", "ticket", "空港", "airport", "成田", "羽田",
    ],
    "accommodation": [
        "宿泊", "ホテル", "hotel", "旅館", "ryokan", "民泊", "Airbnb",
        "カプセル", "capsule", "泊まる", "stay", "宿", "inn",
        "チェックイン", "予約", "booking", "温泉", "onsen",
    ],
    "dining": [
        "飲食", "レストラン", "restaurant", "ラーメン", "ramen",
        "寿司", "sushi", "居酒屋", "izakaya", "食べる", "eat",
        "グルメ", "和食", "Japanese food", "弁当", "bento",
        "箸", "chopsticks", "お通し", "飲み放題",
    ],
    "practical_info": [
        "SIM", "WiFi", "現金", "cash", "ATM", "両替", "exchange",
        "安全", "safety", "緊急", "emergency", "マナー", "manner",
        "地震", "earthquake", "台風", "typhoon", "トイレ", "toilet",
        "病院", "hospital", "チップ", "tip", "免税", "tax free",
    ],
}
