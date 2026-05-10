"""Foreign business entry knowledge base — Essential steps for foreign companies/individuals entering Japan.

This is a cross-industry foundational knowledge base covering:
- Company incorporation (法人設立)
- Business manager visa (経営管理ビザ)
- Bank account opening
- Real estate / office leasing
- Tax registration
- Employee hiring basics
"""

FOREIGN_ENTRY_DB = {
    "company_incorporation": {
        "_meta": {
            "last_verified": "2026-05-10",
            "source": "法務省 出入国在留管理庁、JETRO対日投資ガイド",
            "source_url": "https://www.moj.go.jp/isa/",
            "confidence": "verified",
            "valid_until": None,
            "version": "1.0.0",
            "changelog": ["2026-05-10: Initial verified entry"]
        },
        "name_ja": "法人設立",
        "name_en": "Company Incorporation",
        "category": "legal",
        "summary": "日本で事業を行うための法人設立手続き。株式会社または合同会社の設立が一般的。",
        "company_types": [
            {
                "type": "株式会社 (Kabushiki Kaisha / KK)",
                "capital_requirement": "1円以上（ただし経営管理ビザ取得には500万円以上が実質必要）",
                "features": "最も信用度が高い。上場可能。取締役1名以上",
                "registration_cost": "約20-25万円（登録免許税15万円 + 定款認証5万円 + 印紙代等）",
                "recommended_for": "本格的な事業展開、B2B取引、融資を受ける場合",
            },
            {
                "type": "合同会社 (Godo Kaisha / GK)",
                "capital_requirement": "1円以上",
                "features": "設立費用が安い。定款認証不要。米国LLCに相当",
                "registration_cost": "約6-10万円（登録免許税6万円 + 印紙代等）",
                "recommended_for": "小規模事業、IT系スタートアップ、コスト重視の場合",
            },
        ],
        "procedures": [
            {
                "step": 1,
                "what": "会社の基本事項を決定",
                "detail": "商号、事業目的、本店所在地、資本金額、事業年度、役員構成を決定",
                "tips": "事業目的は将来の拡張を見越して広めに設定。許認可事業は正確な表現が必要",
                "duration": "1-2日",
            },
            {
                "step": 2,
                "what": "会社印鑑の作成",
                "detail": "法人実印（代表者印）、銀行印、角印の3本セットを作成",
                "tips": "印鑑は日本の商慣習で必須。オンラインで注文可能（3,000-30,000円）",
                "duration": "3-7日",
            },
            {
                "step": 3,
                "what": "定款の作成・認証（株式会社のみ）",
                "detail": "公証役場で定款認証を受ける。電子定款なら印紙税4万円が不要",
                "tips": "行政書士・司法書士に依頼するのが一般的（手数料5-10万円）",
                "duration": "1-3日",
            },
            {
                "step": 4,
                "what": "資本金の払込",
                "detail": "発起人の個人口座に資本金を振り込み、通帳のコピーを取得",
                "tips": "日本の銀行口座が必要。なければ代表者の個人口座（海外口座可の場合あり）",
                "duration": "1日",
            },
            {
                "step": 5,
                "what": "法務局で設立登記",
                "detail": "本店所在地を管轄する法務局に登記申請。申請日が会社の設立日になる",
                "tips": "オンライン申請も可能。登記完了まで通常7-10営業日",
                "duration": "7-10営業日",
            },
            {
                "step": 6,
                "what": "設立後の届出",
                "detail": "税務署（法人設立届出書）、都道府県税事務所、市区町村、年金事務所への届出",
                "tips": "税務署への届出は設立後2ヶ月以内。青色申告の承認申請も同時に行う",
                "duration": "1-2週間",
            },
        ],
        "total_cost": "株式会社: 25-50万円（専門家費用含む）/ 合同会社: 10-20万円",
        "total_duration": "2-4週間（書類準備から登記完了まで）",
        "experience_tips": [
            "法務局の窓口で『初めての設立です』と伝えると、担当者が丁寧に教えてくれる。日本の行政窓口は『分からない』と正直に言う人に優しい",
            "司法書士との最初の打ち合わせで事業ビジョンを熱く語ると、専門家が『この人を応援したい』と感じて積極的に動いてくれる。専門家も人間",
        ],
    },

    "business_visa": {

        "_meta": {

            "last_verified": "2026-05-10",

            "source": "法務省 出入国在留管理庁、JETRO対日投資ガイド",

            "source_url": "https://www.moj.go.jp/isa/",

            "confidence": "verified",

            "valid_until": None,

            "version": "1.0.0",

            "changelog": ["2026-05-10: Initial verified entry"]

        },
        "name_ja": "経営管理ビザ（在留資格）",
        "name_en": "Business Manager Visa",
        "category": "immigration",
        "summary": "外国人が日本で事業の経営または管理を行うために必要な在留資格。取得は厳格で準備に時間がかかる。",
        "requirements": [
            "事業所の確保（バーチャルオフィス不可。実体のある事務所・店舗が必要）",
            "資本金500万円以上、または常勤職員2名以上の雇用",
            "事業の安定性・継続性を示す事業計画書",
            "申請者が事業の経営または管理に実質的に従事すること",
        ],
        "procedures": [
            {
                "step": 1,
                "what": "事前準備",
                "detail": "事業計画書の作成、事務所の賃貸契約、資本金の準備",
                "tips": "事業計画書は入管審査の最重要書類。売上予測、市場分析、資金計画を含める",
                "duration": "1-3ヶ月",
            },
            {
                "step": 2,
                "what": "法人設立（日本での協力者が必要）",
                "detail": "日本にいる協力者（共同代表、行政書士等）が代理で法人設立手続きを行う",
                "tips": "申請者本人が日本にいない場合、短期ビザで来日して手続きを行うケースも多い",
                "duration": "2-4週間",
            },
            {
                "step": 3,
                "what": "在留資格認定証明書の申請",
                "detail": "出入国在留管理局（入管）に申請。審査期間は1-3ヶ月",
                "tips": "必要書類: 申請書、事業計画書、登記簿謄本、事務所の賃貸契約書、資本金の証明、履歴書等",
                "duration": "1-3ヶ月",
            },
            {
                "step": 4,
                "what": "査証（ビザ）の取得",
                "detail": "認定証明書を母国の日本大使館に持参し、査証を申請",
                "tips": "認定証明書の有効期限は3ヶ月。期限内に査証を取得して入国する必要がある",
                "duration": "1-2週間",
            },
            {
                "step": 5,
                "what": "入国・在留カードの受領",
                "detail": "日本の空港で在留カードを受領。市区町村で住民登録を行う",
                "tips": "在留期間は通常1年（初回）。更新時に事業の実績が審査される",
                "duration": "入国当日",
            },
        ],
        "total_duration": "3-6ヶ月（事前準備から入国まで）",
        "cost": "入管申請手数料なし。行政書士費用: 15-30万円",
        "common_pitfalls": [
            "バーチャルオフィスで申請して不許可（実体のある事務所が必須）",
            "事業計画が曖昧で不許可（具体的な売上予測・顧客リストが必要）",
            "資本金500万円の出所が不明確（送金記録・預金証明が必要）",
            "日本語の書類準備が不十分（行政書士の活用を強く推奨）",
        ],
        "experience_tips": [
            "事業計画書に『日本社会への貢献』を明記すると入管の印象が変わる。雇用創出、技術移転、地域活性化など『日本にとってのメリット』を語る",
            "行政書士を『コスト』ではなく『投資』と考える。良い行政書士は入管の審査傾向を熟知しており、許可率を劇的に上げる",
        ],
    },

    "bank_account": {

        "_meta": {

            "last_verified": "2026-05-11",

            "source": "全国銀行協会、JETRO対日投資ガイド、各銀行公式情報",

            "source_url": "https://www.zenginkyo.or.jp/",

            "confidence": "verified",

            "valid_until": None,

            "version": "1.0.1",

            "changelog": ["2026-05-10: Initial verified entry", "2026-05-11: source/source_url修正（入管庁→全銀協）、誤字修正"]

        },
        "name_ja": "法人銀行口座の開設",
        "name_en": "Corporate Bank Account Opening",
        "category": "finance",
        "summary": "外国人が日本で法人口座を開設するのは非常に困難。マネーロンダリング対策で審査が厳格。",
        "difficulty": "非常に高い。設立直後の法人、外国人代表者の場合は複数回拒否されるケースが一般的",
        "recommended_banks": [
            {"bank": "ゆうちょ銀行", "difficulty": "やや易", "notes": "審査が比較的緩い。ただし法人取引の機能が限定的"},
            {"bank": "ネット銀行（GMOあおぞら、住信SBI等）", "difficulty": "中", "notes": "オンライン完結。スタートアップに人気"},
            {"bank": "都市銀行（三菱UFJ、三井住友、みずほ）", "difficulty": "高", "notes": "信用度が最も高いが審査が最も厳格"},
            {"bank": "信用金庫", "difficulty": "中", "notes": "地域密着型。紹介があると通りやすい"},
        ],
        "required_documents": [
            "登記簿謄本（発行後3ヶ月以内）",
            "定款のコピー",
            "代表者の在留カード・パスポート",
            "代表者の住民票",
            "法人の印鑑証明書",
            "事業計画書・会社案内",
            "事務所の賃貸契約書",
            "代表者の実印",
        ],
        "tips": [
            "設立直後は審査が通りにくい。1-3ヶ月の事業実績を作ってから再申請するのも手",
            "ゆうちょ銀行 → ネット銀行 → 都市銀行の順で申請するのが現実的",
            "法人口座開設支援を行う行政書士・コンサルタントもいる",
            "日本語での面談が必要な場合が多い。通訳同伴は銀行による",
        ],
        "experience_tips": [
            "口座開設の面談で『日本で長期的に事業を展開したい』と明確に伝えると、銀行の審査担当の印象が変わる。短期的な印象を与えるとマネロンリスクと見なされる",
            "信用金庫は『地域に貢献する企業』を支援する使命がある。『この地域で雇用を生みたい』と伝えると対応が変わる",
        ],
    },

    "real_estate": {

        "_meta": {

            "last_verified": "2026-05-11",

            "source": "国土交通省、宅地建物取引業法、JETRO対日投資ガイド",

            "source_url": "https://www.mlit.go.jp/",

            "confidence": "verified",

            "valid_until": None,

            "version": "1.0.1",

            "changelog": ["2026-05-10: Initial verified entry", "2026-05-11: source/source_url修正（入管庁→国交省）、誤字修正"]

        },
        "name_ja": "事務所・店舗の物件探し",
        "name_en": "Office / Shop Leasing",
        "category": "real_estate",
        "summary": "日本の不動産賃貸には独自の慣習がある。外国人には理解しにくい費用構造と保証制度。",
        "cost_structure": [
            {"item": "敷金（しききん）", "description": "保証金。退去時に原状回復費を差し引いて返還", "typical": "家賃の1-6ヶ月分（商業物件は3-6ヶ月）"},
            {"item": "礼金（れいきん）", "description": "大家への謝礼。返還されない", "typical": "家賃の0-2ヶ月分（最近は0のケースも増加）"},
            {"item": "仲介手数料", "description": "不動産仲介会社への手数料", "typical": "家賃の1ヶ月分 + 消費税"},
            {"item": "前家賃", "description": "入居月の家賃（日割り）+ 翌月分", "typical": "家賃の1-2ヶ月分"},
            {"item": "保証会社費用", "description": "家賃保証会社への加入費", "typical": "家賃の0.5-1ヶ月分（外国人は必須のケースが多い）"},
            {"item": "火災保険", "description": "借家人賠償保険", "typical": "1.5-3万円/年"},
        ],
        "居抜き物件": {
            "description": "前テナントの内装・設備がそのまま残っている物件。飲食店に特に多い",
            "merit": "初期投資を大幅に削減できる（内装費用500-2000万円→0-200万円）",
            "risk": "設備の状態を入念にチェック。前テナントの撤退理由も確認すべき",
        },
        "tips": [
            "外国人の賃貸は拒否されるケースがある。外国人対応の仲介会社を選ぶ",
            "経営管理ビザ申請前に事務所を確保する必要がある（バーチャルオフィス不可）",
            "契約書は日本語のみの場合が多い。翻訳・説明を仲介会社に求める",
            "居抜き物件は「造作譲渡費」として前テナントに50-300万円を支払うケースがある",
        ],
        "experience_tips": [
            "不動産仲介の担当者と信頼関係を築くと、公開前の良い物件を紹介してもらえる。受け身で『紹介を待つ』のではなく『こういう条件で探している』と具体的に伝えると担当者が積極的に動いてくれる",
            "内見で物件の良い点を褒めると、大家や管理会社の印象が良くなり審査が有利に働くことがある",
        ],
    },

    "tax_registration": {

        "_meta": {

            "last_verified": "2026-05-11",

            "source": "国税庁、JETRO対日投資ガイド",

            "source_url": "https://www.nta.go.jp/",

            "confidence": "verified",

            "valid_until": None,

            "version": "1.0.1",

            "changelog": ["2026-05-10: Initial verified entry", "2026-05-11: source/source_url修正（入管庁→国税庁）"]

        },
        "name_ja": "税務届出",
        "name_en": "Tax Registration",
        "category": "tax",
        "summary": "法人設立後に必要な税務関連の届出一覧。期限を守らないと罰則や不利益が発生する。",
        "required_filings": [
            {
                "document": "法人設立届出書",
                "authority": "税務署",
                "deadline": "設立後2ヶ月以内",
                "penalty": "届出がないと各種届出の前提が欠ける",
            },
            {
                "document": "青色申告の承認申請書",
                "authority": "税務署",
                "deadline": "設立後3ヶ月以内 or 最初の事業年度末（早い方）",
                "penalty": "申請しないと白色申告になり、欠損金の繰越控除等の優遇が受けられない",
            },
            {
                "document": "給与支払事務所等の開設届出書",
                "authority": "税務署",
                "deadline": "給与支払開始から1ヶ月以内",
                "penalty": "届出しないと源泉徴収の義務が認識されない",
            },
            {
                "document": "法人設立届出書",
                "authority": "都道府県税事務所・市区町村",
                "deadline": "設立後すみやかに（自治体により異なる）",
                "penalty": "届出がないと法人住民税・法人事業税の通知が届かない",
            },
            {
                "document": "消費税課税事業者届出書（該当する場合）",
                "authority": "税務署",
                "deadline": "課税事業者となる期間の前日まで",
                "penalty": "インボイス発行不可",
            },
            {
                "document": "適格請求書発行事業者の登録申請書",
                "authority": "税務署",
                "deadline": "任意（ただしB2B取引には実質必須）",
                "penalty": "インボイスが発行できず、取引先に不利益が生じる",
            },
        ],
        "tips": [
            "税理士への依頼を強く推奨。月額2-5万円が相場",
            "初年度は免税事業者（売上1,000万円以下）の場合が多いが、インボイス対応は別途判断が必要",
            "青色申告の申請は絶対に忘れないこと。欠損金の10年繰越控除、30万円未満の即時償却等の優遇が受けられなくなる",
        ],
        "experience_tips": [
            "税理士を『コスト』ではなく『戦略パートナー』として扱うと、税務だけでなく事業全体のアドバイスをもらえる。良い税理士は経営者の右腕になる",
            "初回の確定申告を丁寧に行うと、税務署からの心証が変わる。『しっかりした会社』という印象はその後の税務調査の対応にも影響する",
        ],
    },
    "employee_hiring": {
        "_meta": {
            "last_verified": "2026-05-11",
            "source": "厚生労働省、労働基準法、JETRO対日投資ガイド",
            "source_url": "https://www.mhlw.go.jp/",
            "confidence": "verified",
            "valid_until": None,
            "version": "1.0.0",
            "changelog": ["2026-05-11: Initial verified entry"]
        },
        "name_ja": "従業員の雇用",
        "name_en": "Employee Hiring Basics",
        "category": "labor",
        "summary": "日本の労働法は従業員保護が手厚い。解雇規制、社会保険、有給休暇のルールを理解せずに雇用すると深刻なトラブルに発展する。",
        "employment_types": [
            {
                "type": "正社員（無期雇用）",
                "characteristics": "期間の定めなし。フルタイム。解雇は極めて困難（解雇権濫用法理）",
                "benefits": "社会保険完備、賞与、退職金が一般的",
                "recommended_for": "コア人材。長期的な事業運営に必要なポジション",
            },
            {
                "type": "契約社員（有期雇用）",
                "characteristics": "契約期間あり（通常1年、最長3年）。5年超で無期転換権が発生（労働契約法18条）",
                "benefits": "正社員と同等の社会保険。同一労働同一賃金の原則",
                "recommended_for": "プロジェクト型の業務、事業の初期段階",
            },
            {
                "type": "パート・アルバイト",
                "characteristics": "短時間労働。週20時間以上で社会保険加入義務",
                "benefits": "有給休暇は勤務日数に応じて付与（比例付与）",
                "recommended_for": "補助的業務、繁忙期の人員確保",
            },
            {
                "type": "業務委託（フリーランス）",
                "characteristics": "雇用関係なし。指揮命令権なし。偽装請負に注意",
                "benefits": "社会保険・有給休暇の義務なし。ただしフリーランス保護法（2024年11月施行）で契約条件の明示等が義務化",
                "recommended_for": "専門性の高い業務、IT開発等",
            },
        ],
        "mandatory_obligations": [
            {
                "item": "社会保険の加入",
                "detail": "法人は従業員1名でも加入義務。健康保険+厚生年金。保険料は労使折半",
                "deadline": "雇用開始から5日以内に届出",
            },
            {
                "item": "労働保険の加入",
                "detail": "雇用保険+労災保険。労災保険は全額事業主負担",
                "deadline": "従業員雇用から10日以内に届出",
            },
            {
                "item": "労働条件通知書",
                "detail": "賃金、労働時間、休日、契約期間等を書面で明示する義務（労働基準法15条）",
                "deadline": "雇用契約締結時",
            },
            {
                "item": "36協定の届出",
                "detail": "法定労働時間（1日8時間、週40時間）を超える残業には労使協定が必要",
                "deadline": "残業が発生する前に届出",
            },
        ],
        "dismissal_rules": {
            "summary": "日本の解雇規制は世界でも最も厳しい水準。客観的に合理的な理由がなく、社会通念上相当と認められない解雇は無効（労働契約法16条）",
            "notice_period": "30日前の予告、または30日分以上の解雇予告手当の支払い",
            "common_pitfalls": [
                "能力不足による解雇は、改善指導の記録が必須。即日解雇はほぼ不可能",
                "整理解雇（リストラ）には4要件が必要: 人員削減の必要性、解雇回避努力、人選の合理性、手続きの妥当性",
                "試用期間中の解雇も制限あり。14日以降は解雇予告が必要",
            ],
        },
        "paid_leave": {
            "entitlement": "入社6ヶ月・出勤率80%以上で10日付与。以後1年ごとに増加し最大20日",
            "obligation": "年5日の有給取得義務（2019年4月〜）。違反は1人あたり30万円以下の罰金",
        },
        "experience_tips": [
            "日本では『採用は慎重に、解雇はほぼ不可能』が大原則。欧米の感覚で『合わなければ辞めてもらう』は通用しない。採用時の見極めが全て",
            "社会保険労務士（社労士）への顧問契約を強く推奨。月額2-5万円で労務管理の法的リスクを大幅に軽減できる。特に外国人経営者には必須",
        ],
    },
}

# ── Keyword matching ──────────────────────────────────

FOREIGN_ENTRY_KEYWORDS = {
    "company_incorporation": ["法人設立", "会社設立", "incorporation", "設立登記", "定款", "登記", "株式会社", "合同会社", "KK", "GK", "起業", "創業", "設立費用"],
    "business_visa": ["ビザ", "visa", "在留資格", "経営管理", "入管", "immigration", "在留カード", "residence", "外国人", "foreigner", "就労"],
    "bank_account": ["銀行口座", "bank account", "口座開設", "法人口座", "振込", "ゆうちょ", "都市銀行", "ネット銀行"],
    "real_estate": ["物件", "不動産", "real estate", "賃貸", "lease", "事務所", "office", "店舗", "shop", "敷金", "礼金", "居抜き", "テナント", "仲介"],
    "tax_registration": ["税務届出", "tax registration", "法人設立届", "青色申告", "税務署", "開業届", "インボイス", "税理士", "確定申告", "消費税"],
    "employee_hiring": ["雇用", "hiring", "従業員", "employee", "採用", "recruitment", "労働", "labor", "社会保険", "解雇", "dismissal", "正社員", "契約社員", "パート", "アルバイト", "有給", "36協定", "社労士", "労働基準法", "フリーランス", "業務委託"],
}
