"""Organization knowledge base — Japanese corporate structure and business practices.

Covers keiretsu, industry associations, contract customs, payment practices,
corporate hierarchy, and decision-making patterns unique to Japan.
"""

ORGANIZATION_DB = {
    "corporate_hierarchy": {
        "name_ja": "企業の役職体系",
        "name_en": "Corporate Hierarchy",
        "category": "structure",
        "summary": "日本企業の役職は細かく階層化されており、各役職に期待される役割・権限・敬称が異なる。",
        "hierarchy": [
            {"rank": 1, "title_ja": "会長", "title_en": "Chairman", "role": "名誉職。前社長が就任することが多い。経営の最終的な後見人"},
            {"rank": 2, "title_ja": "社長（代表取締役）", "title_en": "President / CEO", "role": "最高経営責任者。会社の代表権を持つ"},
            {"rank": 3, "title_ja": "副社長", "title_en": "Executive Vice President", "role": "社長の補佐。社長不在時の代行"},
            {"rank": 4, "title_ja": "専務取締役", "title_en": "Senior Managing Director", "role": "経営全般の管理。複数の事業部門を統括"},
            {"rank": 5, "title_ja": "常務取締役", "title_en": "Managing Director", "role": "特定の事業部門の管理"},
            {"rank": 6, "title_ja": "執行役員", "title_en": "Executive Officer", "role": "取締役会の決定に基づき業務を執行。法律上の取締役ではない"},
            {"rank": 7, "title_ja": "本部長", "title_en": "General Manager / Division Head", "role": "事業本部の長"},
            {"rank": 8, "title_ja": "部長", "title_en": "Department Manager", "role": "部門の責任者。実質的な意思決定の中心"},
            {"rank": 9, "title_ja": "次長", "title_en": "Deputy Department Manager", "role": "部長の補佐"},
            {"rank": 10, "title_ja": "課長", "title_en": "Section Manager", "role": "課の責任者。日常業務の管理・決裁の最前線"},
            {"rank": 11, "title_ja": "係長", "title_en": "Subsection Chief", "role": "小チームのリーダー。管理職の入口"},
            {"rank": 12, "title_ja": "主任", "title_en": "Senior Staff", "role": "一般社員の中の上位。後輩指導の役割"},
            {"rank": 13, "title_ja": "一般社員", "title_en": "Staff", "role": "新入社員〜若手社員"},
        ],
        "agent_tips": [
            "部長が実質的な決定権を持つことが多い（社長決裁は形式的な場合も）",
            "「課長代理」「課長補佐」「担当課長」等の中間的な役職も多い",
            "名刺の役職で相手の権限レベルを推測できるが、実権は異なることもある",
            "外資系企業のVP、Director等の肩書きは日本の階層と直接対応しない",
        ],
    },

    "keiretsu": {
        "name_ja": "系列・企業グループ",
        "name_en": "Keiretsu (Corporate Groups)",
        "category": "structure",
        "summary": "日本企業は歴史的な企業グループ（系列）で結びついており、グループ内での取引優先が根強い。",
        "major_groups": [
            {
                "name": "三菱グループ",
                "core": ["三菱UFJフィナンシャル・グループ", "三菱商事", "三菱重工業"],
                "meeting": "金曜会（月1回の社長会）",
                "characteristics": "組織力・重厚長大。「組織の三菱」と呼ばれる",
            },
            {
                "name": "三井グループ",
                "core": ["三井住友フィナンシャルグループ", "三井物産", "三井不動産"],
                "meeting": "二木会（月1回の社長会）",
                "characteristics": "個人の自主性重視。「人の三井」と呼ばれる",
            },
            {
                "name": "住友グループ",
                "core": ["三井住友フィナンシャルグループ", "住友商事", "住友化学"],
                "meeting": "白水会",
                "characteristics": "結束力が強い。「結束の住友」と呼ばれる",
            },
            {
                "name": "トヨタグループ",
                "core": ["トヨタ自動車", "デンソー", "アイシン"],
                "meeting": "協豊会",
                "characteristics": "自動車産業のピラミッド型系列。下請け構造が明確",
            },
        ],
        "agent_tips": [
            "系列企業への営業は、グループ内のメインバンクや商社を通じたアプローチが有効",
            "系列外からの参入は困難だが、技術的優位性があれば可能",
            "近年は系列の結びつきが弱まりつつあるが、金融・不動産では依然として強い",
        ],
    },

    "payment_practices": {
        "name_ja": "支払慣行",
        "name_en": "Payment Practices",
        "category": "transaction",
        "summary": "日本企業の支払いサイト（支払いまでの期間）は国際的に見て長く、手形取引も依然として残る。",
        "standard_terms": {
            "月末締め翌月末払い": {
                "description": "当月の取引を月末で締め、翌月末に支払う（最も一般的）",
                "payment_cycle": "30-60日",
            },
            "月末締め翌々月末払い": {
                "description": "当月の取引を月末で締め、翌々月末に支払う",
                "payment_cycle": "60-90日",
            },
            "20日締め翌月末払い": {
                "description": "当月20日で締め、翌月末に支払う",
                "payment_cycle": "40-70日",
            },
        },
        "payment_methods": [
            {"method": "銀行振込", "share": "約70%", "notes": "最も一般的。振込手数料は通常買い手負担"},
            {"method": "手形", "share": "約10%（減少傾向）", "notes": "2026年に手形の電子化推進（でんさい）。不渡り2回で銀行取引停止"},
            {"method": "口座振替", "share": "約10%", "notes": "BtoC取引や定期的な支払いで利用"},
            {"method": "クレジットカード", "share": "約5%", "notes": "BtoB取引では少ないが増加傾向"},
            {"method": "現金", "share": "約5%（減少傾向）", "notes": "小規模取引。インボイス制度で更に減少"},
        ],
        "agent_tips": [
            "下請法により、発注者は60日以内の支払いが義務（違反は公正取引委員会の勧告対象）",
            "手形サイト（支払期日）が120日を超える手形は下請法違反の可能性",
            "請求書はPDF送付が増えているが、紙の原本を求める企業も多い",
            "インボイス制度（2023年10月〜）により、適格請求書の発行・保存が必要",
        ],
    },

    "contract_customs": {
        "name_ja": "契約慣行",
        "name_en": "Contract Customs",
        "category": "transaction",
        "summary": "日本の契約は「関係性」の上に成り立つ。契約書は重要だが、信頼関係がより重視される。",
        "key_concepts": [
            {
                "concept": "基本契約書 + 個別契約書",
                "description": "取引の基本条件を基本契約で定め、個別の注文は個別契約（注文書・注文請書）で行う。日本独自の二層構造",
            },
            {
                "concept": "印鑑（実印・角印）",
                "description": "契約書には法人の実印（代表者印）を押印。法的には署名でも有効だが、実印が慣習的に求められる",
            },
            {
                "concept": "収入印紙",
                "description": "契約書の金額に応じた収入印紙の貼付が必要（印紙税法）。電子契約なら不要",
            },
            {
                "concept": "契約の自動更新",
                "description": "1年契約で「申し出がなければ自動更新」が一般的。解約には通常1-3ヶ月前の書面通知が必要",
            },
        ],
        "stamp_tax": [
            {"contract_amount": "1万円未満", "tax": "非課税"},
            {"contract_amount": "1万円〜100万円", "tax": "200円"},
            {"contract_amount": "100万円〜500万円", "tax": "1,000円"},
            {"contract_amount": "500万円〜1,000万円", "tax": "5,000円"},
            {"contract_amount": "1,000万円〜5,000万円", "tax": "10,000円"},
            {"contract_amount": "5,000万円〜1億円", "tax": "30,000円"},
            {"contract_amount": "1億円〜5億円", "tax": "60,000円"},
        ],
        "agent_tips": [
            "電子契約（クラウドサイン、DocuSign等）を使えば印紙税は不要。大企業でも導入が進んでいる",
            "契約書の締結前に「覚書」「MOU」を交わすケースも多い。法的拘束力は内容による",
            "日本語と英語の契約書で齟齬がある場合、日本語版が優先される条項を入れることが多い",
        ],
    },

    "industry_associations": {
        "name_ja": "業界団体",
        "name_en": "Industry Associations",
        "category": "network",
        "summary": "日本では業界団体が規制と企業の橋渡し役を果たし、加入が事実上の必須要件となることが多い。",
        "role": [
            "業界の自主規制・ガイドラインの策定",
            "政府への政策提言・ロビイング",
            "業界標準の技術規格・認証制度の運営",
            "会員企業間の情報交換・ネットワーキング",
            "業界統計の収集・公表",
        ],
        "major_associations": [
            {"name": "日本経済団体連合会（経団連）", "members": "大企業中心、約1,500社", "influence": "最高。政策決定に強い影響力"},
            {"name": "日本商工会議所", "members": "中小企業中心、約125万社", "influence": "高。地域経済の要"},
            {"name": "経済同友会", "members": "経営者個人の参加、約1,400人", "influence": "高。経営者の声として政策提言"},
            {"name": "全国中小企業団体中央会", "members": "中小企業組合、約2.6万組合", "influence": "中。中小企業政策に特化"},
        ],
        "agent_tips": [
            "業界団体への加入は法的義務ではないが、未加入は「業界のアウトサイダー」と見なされる場合がある",
            "業界団体経由で紹介を得ると、営業の成功率が大幅に上がる",
            "外国企業も業界団体に加入可能（在日外国商工会議所もある）",
        ],
    },
}

# ── Keyword matching ──────────────────────────────────

ORGANIZATION_KEYWORDS = {
    "corporate_hierarchy": ["役職", "hierarchy", "部長", "課長", "社長", "取締役", "title", "position", "肩書き", "係長", "主任", "執行役員", "常務", "専務", "本部長", "次長", "manager", "director", "officer", "階層", "組織図"],
    "keiretsu": ["系列", "keiretsu", "企業グループ", "三菱", "三井", "住友", "トヨタ", "グループ", "group", "下請け", "サプライチェーン", "supply chain", "ピラミッド", "メインバンク"],
    "payment_practices": ["支払い", "payment", "振込", "手形", "請求書", "invoice", "支払サイト", "入金", "仕入", "仕入先", "supplier", "買掛", "売掛", "月末締め", "翌月末", "現金", "cash", "銀行", "bank", "口座", "account", "でんさい", "インボイス"],
    "contract_customs": ["契約", "contract", "印鑑", "押印", "収入印紙", "基本契約", "覚書", "MOU", "lease", "賃貸", "不動産", "物件", "敷金", "礼金", "保証金", "テナント", "署名", "sign", "電子契約", "更新", "解約", "自動更新", "交渉", "negotiation"],
    "industry_associations": ["業界団体", "association", "経団連", "商工会議所", "組合", "団体", "加入", "会員", "ネットワーク", "network", "ロビイング", "lobby", "協会"],
}
