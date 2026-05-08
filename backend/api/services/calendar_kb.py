"""Calendar knowledge base — Japanese business calendar and seasonal awareness.

Critical timing knowledge that AI agents need to operate effectively in Japan.
Covers fiscal years, holidays, gift seasons, administrative deadlines, and
seasonal business patterns.
"""

CALENDAR_DB = {
    "fiscal_year": {
        "name_ja": "会計年度",
        "name_en": "Fiscal Year",
        "category": "business_cycle",
        "summary": "日本企業の約7割は4月始まり（4月1日〜翌3月31日）の会計年度を採用。政府・自治体も同様。",
        "details": {
            "standard": {
                "start": "4月1日",
                "end": "翌年3月31日",
                "adoption_rate": "上場企業の約70%、政府・自治体は100%",
            },
            "alternatives": [
                {"period": "1月〜12月", "adoption": "外資系企業に多い（約15%）"},
                {"period": "その他（7月〜、10月〜等）", "adoption": "小売・アパレル等で散見（約15%）"},
            ],
        },
        "key_periods": [
            {"period": "4月", "event": "新年度開始。人事異動・組織改編が集中。新入社員の入社式"},
            {"period": "5月中旬", "event": "3月期決算企業の決算発表集中期間"},
            {"period": "6月", "event": "株主総会の集中月（3月決算企業）。役員改選"},
            {"period": "9月末", "event": "中間決算（上半期終了）"},
            {"period": "10月", "event": "下半期開始。秋の人事異動"},
            {"period": "12月", "event": "年末調整。冬の賞与支給"},
            {"period": "1-2月", "event": "翌年度の予算策定・承認。採用活動の本格化"},
            {"period": "3月", "event": "年度末。予算消化の駆け込み発注が増加。決算対策"},
        ],
        "agent_tips": [
            "3月は年度末で予算消化のため発注が急増するが、4月以降は予算凍結で急減する",
            "4月の人事異動で担当者が変わることが多い。引き継ぎ情報の更新が必要",
            "6月の株主総会シーズンは経営陣が多忙。重要な提案は5月までに行う",
            "決算発表の日程はTDnet（適時開示情報伝達システム）で確認可能",
        ],
    },

    "public_holidays": {
        "name_ja": "祝日・大型連休",
        "name_en": "Public Holidays & Extended Breaks",
        "category": "holidays",
        "summary": "日本の祝日は年間16日。大型連休（GW・お盆・年末年始）はビジネスが実質停止する。",
        "holidays": [
            {"date": "1月1日", "name": "元日", "business_impact": "年末年始休暇の一部（12/29-1/3が一般的）"},
            {"date": "1月第2月曜", "name": "成人の日", "business_impact": "低（通常の祝日）"},
            {"date": "2月11日", "name": "建国記念の日", "business_impact": "低"},
            {"date": "2月23日", "name": "天皇誕生日", "business_impact": "低"},
            {"date": "3月20日頃", "name": "春分の日", "business_impact": "低（年度末の繁忙期と重なる）"},
            {"date": "4月29日", "name": "昭和の日", "business_impact": "GWの始まり"},
            {"date": "5月3日", "name": "憲法記念日", "business_impact": "GW中核"},
            {"date": "5月4日", "name": "みどりの日", "business_impact": "GW中核"},
            {"date": "5月5日", "name": "こどもの日", "business_impact": "GW終了"},
            {"date": "7月第3月曜", "name": "海の日", "business_impact": "低〜中"},
            {"date": "8月11日", "name": "山の日", "business_impact": "お盆休暇と接続して長期連休化"},
            {"date": "9月第3月曜", "name": "敬老の日", "business_impact": "シルバーウィーク形成の可能性"},
            {"date": "9月22日頃", "name": "秋分の日", "business_impact": "シルバーウィーク形成の可能性"},
            {"date": "10月第2月曜", "name": "スポーツの日", "business_impact": "低"},
            {"date": "11月3日", "name": "文化の日", "business_impact": "低"},
            {"date": "11月23日", "name": "勤労感謝の日", "business_impact": "低"},
        ],
        "extended_breaks": {
            "golden_week": {
                "name": "ゴールデンウィーク（GW）",
                "period": "4月29日〜5月5日（前後に有給を取り最大10連休）",
                "business_impact": "critical",
                "notes": [
                    "多くの企業が4/29-5/5を連続休暇とする",
                    "この期間の商談・契約締結は事実上不可能",
                    "GW前の4月中旬までに重要な案件は片付ける",
                    "GW明けの5月病（五月病）で社員のモチベーションが低下する傾向",
                ],
            },
            "obon": {
                "name": "お盆",
                "period": "8月13日〜16日（前後に有給を取り最大9連休）",
                "business_impact": "high",
                "notes": [
                    "法定の祝日ではないが、多くの企業が夏季休暇を設定",
                    "帰省ラッシュで交通機関が混雑",
                    "製造業は工場を停止することが多い",
                    "官公庁は通常営業だが、担当者が休暇のことが多い",
                ],
            },
            "nenmatsu_nenshi": {
                "name": "年末年始",
                "period": "12月29日〜1月3日（前後に有給を取り最大10連休）",
                "business_impact": "critical",
                "notes": [
                    "12月28日が仕事納め（御用納め）、1月4日が仕事始め（御用始め）が標準",
                    "年末の挨拶回りは12月中旬〜下旬",
                    "年始の挨拶回りは1月第1-2週",
                    "年賀状の準備は12月中旬まで（ビジネスでは減少傾向だが依然重要）",
                ],
            },
        },
    },

    "gift_seasons": {
        "name_ja": "贈答シーズン",
        "name_en": "Gift-Giving Seasons",
        "category": "relationship",
        "summary": "日本のビジネスでは季節の贈答が関係維持に重要。時期を逃すと失礼にあたる。",
        "seasons": [
            {
                "name": "お年賀",
                "period": "1月1日〜1月15日（松の内）",
                "purpose": "新年の挨拶",
                "budget": "1,000〜3,000円",
                "notes": "年始の挨拶回りの際に持参。年賀状とは別",
            },
            {
                "name": "バレンタインデー（義理チョコ）",
                "period": "2月14日",
                "purpose": "職場の人間関係維持（減少傾向）",
                "budget": "500〜1,000円",
                "notes": "近年は廃止する企業も多い。ハラスメント問題との関連",
            },
            {
                "name": "ホワイトデー",
                "period": "3月14日",
                "purpose": "バレンタインのお返し",
                "budget": "バレンタインの1.5-2倍",
                "notes": "バレンタインを受け取った場合はお返しが必須",
            },
            {
                "name": "お中元",
                "period": "関東: 7/1-7/15、関西: 7/15-8/15",
                "purpose": "上半期のお世話への感謝",
                "budget": "3,000〜10,000円",
                "notes": "百貨店からの配送が一般的。のし紙は「お中元」",
            },
            {
                "name": "お歳暮",
                "period": "12月初旬〜12月20日",
                "purpose": "一年間のお世話への感謝",
                "budget": "3,000〜10,000円（お中元より少し高め）",
                "notes": "お中元を贈る相手にはお歳暮も贈るのが原則。片方だけならお歳暮を優先",
            },
        ],
        "agent_tips": [
            "贈答の手配は時期の2-3週間前に完了する（百貨店の配送は混雑する）",
            "公務員への贈答は国家公務員倫理法で厳しく制限されている",
            "社内規程で贈答の上限額が決まっている企業が多い（事前確認必須）",
        ],
    },

    "administrative_deadlines": {
        "name_ja": "行政・税務の主要締切",
        "name_en": "Administrative & Tax Deadlines",
        "category": "compliance",
        "summary": "日本で事業を行う上で遵守すべき主要な行政・税務の締切日。期限超過は罰則や加算税の対象。",
        "deadlines": [
            {
                "deadline": "1月31日",
                "item": "法定調書の提出、給与支払報告書の提出",
                "authority": "税務署、市区町村",
                "penalty": "1年以下の懲役または50万円以下の罰金",
            },
            {
                "deadline": "2月16日〜3月15日",
                "item": "所得税の確定申告",
                "authority": "税務署",
                "penalty": "無申告加算税（15-20%）、延滞税",
            },
            {
                "deadline": "3月15日",
                "item": "贈与税の申告",
                "authority": "税務署",
                "penalty": "無申告加算税",
            },
            {
                "deadline": "3月31日",
                "item": "固定資産税の課税基準日（1月1日時点の所有者に課税）",
                "authority": "市区町村",
                "penalty": "N/A",
            },
            {
                "deadline": "決算日の翌日から2ヶ月以内",
                "item": "法人税・法人住民税・法人事業税の確定申告",
                "authority": "税務署、都道府県、市区町村",
                "penalty": "無申告加算税（15-20%）、延滞税（年約9%）",
            },
            {
                "deadline": "決算日の翌日から2ヶ月以内",
                "item": "消費税の確定申告",
                "authority": "税務署",
                "penalty": "無申告加算税、延滞税",
            },
            {
                "deadline": "6月30日",
                "item": "労働保険の年度更新（概算・確定保険料の申告・納付）",
                "authority": "労働基準監督署",
                "penalty": "10%の追徴金",
            },
            {
                "deadline": "7月10日",
                "item": "社会保険の算定基礎届の提出",
                "authority": "年金事務所",
                "penalty": "6ヶ月以下の懲役または50万円以下の罰金",
            },
            {
                "deadline": "毎月10日",
                "item": "源泉所得税の納付（前月分）",
                "authority": "税務署",
                "penalty": "不納付加算税（10%）、延滞税",
                "notes": "納期の特例（従業員10人未満）: 7月10日と1月20日の年2回",
            },
            {
                "deadline": "毎月末",
                "item": "社会保険料の納付（前月分）",
                "authority": "年金事務所",
                "penalty": "延滞金（年約9%）",
            },
        ],
        "agent_tips": [
            "3月決算企業は5月末が法人税申告期限。申告期限の延長特例（1ヶ月）を申請している企業が多い",
            "e-Tax（電子申告）を利用すると一部の申告期限が延長される場合がある",
            "消費税の中間申告（年1回・年3回・年11回）の要否は前年の消費税額で決まる",
        ],
    },

    "seasonal_business": {
        "name_ja": "季節性のあるビジネスイベント",
        "name_en": "Seasonal Business Events",
        "category": "business_cycle",
        "summary": "日本のビジネスには季節性が強く、時期によって商談の成功率や需要が大きく変動する。",
        "monthly_guide": {
            "1月": {
                "events": ["年始挨拶回り", "新春セール", "成人式（1月第2月曜）"],
                "business_notes": "年始は挨拶中心で実務は第2週から本格化。新規提案は1月後半から",
            },
            "2月": {
                "events": ["確定申告シーズン開始", "節分（2/3）"],
                "business_notes": "会計・税務関連の需要増。年度末に向けた予算確認の時期",
            },
            "3月": {
                "events": ["年度末", "卒業・異動シーズン", "引越しシーズン"],
                "business_notes": "予算消化の駆け込み発注。送別会シーズン。不動産需要のピーク",
            },
            "4月": {
                "events": ["新年度", "入社式", "花見シーズン"],
                "business_notes": "新体制発足。歓迎会シーズン。新担当者との関係構築開始",
            },
            "5月": {
                "events": ["GW", "決算発表集中", "五月病"],
                "business_notes": "GW明けは稟議が滞留している。5月後半から本格的な営業活動",
            },
            "6月": {
                "events": ["梅雨入り", "株主総会", "夏の賞与（6月下旬〜7月上旬）"],
                "business_notes": "賞与支給後は消費意欲が高まる。株主総会後に新役員体制が発足",
            },
            "7月": {
                "events": ["お中元シーズン", "夏休み前の追い込み"],
                "business_notes": "お盆前に案件を片付けようとする動きが強まる",
            },
            "8月": {
                "events": ["お盆", "夏季休暇"],
                "business_notes": "ビジネスは実質的にスローダウン。新規提案は9月以降に持ち越し",
            },
            "9月": {
                "events": ["上半期末", "中間決算", "秋の展示会シーズン"],
                "business_notes": "上半期の数字追い込み。下半期の計画策定開始",
            },
            "10月": {
                "events": ["下半期開始", "秋の人事異動", "ハロウィン"],
                "business_notes": "新体制での活動開始。年末に向けた商戦準備",
            },
            "11月": {
                "events": ["年末商戦の準備", "酉の市", "七五三"],
                "business_notes": "年内に案件を片付けるための商談が活発化",
            },
            "12月": {
                "events": ["お歳暮", "忘年会", "冬の賞与", "仕事納め"],
                "business_notes": "12月中旬までに年内の案件を決着。忘年会は関係構築の重要な機会",
            },
        },
    },
}

# ── Keyword matching ──────────────────────────────────

CALENDAR_KEYWORDS = {
    "fiscal_year": ["会計年度", "fiscal year", "決算", "年度", "事業年度", "決算期"],
    "public_holidays": ["祝日", "holiday", "連休", "GW", "ゴールデンウィーク", "お盆", "年末年始", "休日", "振替休日"],
    "gift_seasons": ["贈答", "お中元", "お歳暮", "手土産", "gift", "お年賀", "バレンタイン", "ホワイトデー"],
    "administrative_deadlines": ["締切", "deadline", "確定申告", "税務", "申告", "届出", "納付", "社会保険", "労働保険"],
    "seasonal_business": ["季節", "season", "商戦", "繁忙期", "閑散期", "時期", "いつ", "when", "タイミング"],
}
