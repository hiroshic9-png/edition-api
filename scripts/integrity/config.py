"""
EDITION Integrity Engine — Configuration
==========================================
信頼できるソースのホワイトリスト、検証パラメータ、閾値の定義。
ここに定義されていないソースからのデータは一切受け入れない。
"""
import os

# === PATHS ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
ASSETS_PATH = os.path.join(DATA_DIR, "assets.json")
PAIRS_PATH = os.path.join(DATA_DIR, "training_pairs.json")
CATEGORIES_PATH = os.path.join(DATA_DIR, "categories.json")
QUARANTINE_DIR = os.path.join(DATA_DIR, "quarantine")
AUDIT_LOG_DIR = os.path.join(DATA_DIR, "audit_log")
KNOWLEDGE_PATH = os.path.join(DATA_DIR, "integrity_knowledge.json")

# === TRUSTED SOURCES — WHITELIST ===
# Tier 1: 公的機関 API — 最高信頼。データの権威的原典。
# Tier 2: 主要オークションハウス公式 — 価格データの唯一の正当ソース。
# Tier 3: 学術・専門機関 — 参考情報として許容。単独での採用は不可。
TRUSTED_SOURCES = {
    "tier_1": {
        "met": {
            "name": "The Metropolitan Museum of Art",
            "api_base": "https://collectionapi.metmuseum.org/public/collection/v1",
            "web_domain": "metmuseum.org",
            "image_domain": "images.metmuseum.org",
            "id_prefix": "met-",
            "license_field": "isPublicDomain",
            "license_value": True,
            "our_license": "CC0",
        },
        "aic": {
            "name": "Art Institute of Chicago",
            "api_base": "https://api.artic.edu/api/v1",
            "web_domain": "artic.edu",
            "image_domain": "artic.edu/iiif",
            "id_prefix": "artic-",
            "license_field": "is_public_domain",
            "license_value": True,
            "our_license": "CC0",
        },
        "va": {
            "name": "Victoria and Albert Museum",
            "api_base": "https://api.vam.ac.uk/v2",
            "web_domain": "collections.vam.ac.uk",
            "image_domain": "framemark.vam.ac.uk",
            "id_prefix": "va-",
            "license_field": None,  # V&A uses separate image rights
            "our_license": "CC BY-NC",
        },
    },
    "tier_2": {
        "christies":  {"domain": "christies.com",  "name": "Christie's"},
        "sothebys":   {"domain": "sothebys.com",   "name": "Sotheby's"},
        "bonhams":    {"domain": "bonhams.com",     "name": "Bonhams"},
        "phillips":   {"domain": "phillips.com",    "name": "Phillips"},
    },
    "tier_3": {
        "tnm":    {"domain": "tnm.jp",         "name": "Tokyo National Museum"},
        "nbthk":  {"domain": "touken.or.jp",   "name": "NBTHK"},
        "bunka":  {"domain": "bunka.go.jp",    "name": "Agency for Cultural Affairs"},
    },
}

# === VERIFICATION THRESHOLDS ===
# これらの閾値を下回るデータは一切採用しない。

# 最低照合数: 少なくとも2つの独立ソースで確認できなければ採用しない
MIN_CROSS_REFERENCES = 2

# 原文独自性: API原文との類似度がこの値を超えたらコピーと判定
ORIGINALITY_COPY_THRESHOLD = 0.30  # 30%以上の連続一致 → 盗用

# 連続一致単語数: この数以上の連続一致は盗用と判定
MAX_CONSECUTIVE_MATCH_WORDS = 10

# 鮮度: この日数を超えたデータは再検証が必要
FRESHNESS_MAX_DAYS = 90

# Quarantine: 全データは保留ゾーンを経由（自動昇格は全Checkpoint通過時のみ）
QUARANTINE_REQUIRED = True
AUTO_PROMOTE_ON_PASS = True  # 全Checkpoint通過で自動昇格

# === FIELD VERIFICATION ===
# アセットで必須の検証フィールド（1つでも不一致なら不合格）
ASSET_CRITICAL_FIELDS = [
    "title",        # タイトル
    "period",       # 年代
    "medium",       # 素材
    "artist",       # 作家（ソースに存在する場合）
    "license",      # ライセンス
    "source_url",   # ソースURL
    "image_id",     # 画像ID
]

# === FORBIDDEN PATTERNS ===
# 絶対に採用してはならないデータのパターン
FORBIDDEN_IMAGE_PATTERNS = [
    "placeholder",
    "unsplash.com",
    "via.placeholder.com",
    "picsum.photos",
    "/generated/",
    "stock",
]

FORBIDDEN_SOURCE_PATTERNS = [
    "wikipedia.org",      # Wikipediaは原典ではない
    "reddit.com",
    "facebook.com",
    "instagram.com",
    "pinterest.com",
    "ebay.com",           # eBayは信頼できるソースではない
]
