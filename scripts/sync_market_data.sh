#!/bin/bash
# ═══════════════════════════════════════════════════════════
# EDITION — Market Data Sync from KANTEISHI API
# ═══════════════════════════════════════════════════════════
# Fetches live market data from KANTEISHI API (Mac Mini)
# and updates the static JSON used by GitHub Pages.
#
# Usage: ./scripts/sync_market_data.sh
# ═══════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"

# KANTEISHI API — accessed via SSH to Mac Mini
SSH_HOST="${KANTEISHI_SSH:-macmini}"
API_PORT="${KANTEISHI_PORT:-8901}"

echo "═══ EDITION Market Data Sync ═══"
echo "SSH: $SSH_HOST → localhost:$API_PORT"
echo "Target: $DATA_DIR"
echo ""

# 1. Fetch /market/stats via SSH
echo "▶ Fetching /market/stats..."
MARKET_RAW=$(ssh "$SSH_HOST" "curl -sf http://localhost:${API_PORT}/market/stats" 2>/dev/null) || {
  echo "✗ Failed to reach KANTEISHI API via SSH (${SSH_HOST}:${API_PORT})"
  echo "  Trying hostname direct..."
  MARKET_RAW=$(curl -sf --connect-timeout 5 "http://SatonoMac-mini.local:${API_PORT}/market/stats" 2>/dev/null) || {
    echo "✗ All connection methods failed."
    exit 1
  }
}
echo "  ✓ Received market data"

# 2. Fetch /estimate/model
echo "▶ Fetching /estimate/model..."
MODEL_RAW=$(ssh "$SSH_HOST" "curl -sf http://localhost:${API_PORT}/estimate/model" 2>/dev/null) || {
  MODEL_RAW=$(curl -sf --connect-timeout 5 "http://SatonoMac-mini.local:${API_PORT}/estimate/model" 2>/dev/null) || {
    echo "✗ Failed to fetch /estimate/model"
    exit 1
  }
}
echo "  ✓ Received model info"

# 3. Write raw data to temp files (avoids shell escaping issues)
TMPDIR=$(mktemp -d "$PROJECT_DIR/.sync_tmp_XXXXXX")
trap "rm -rf $TMPDIR" EXIT

echo "$MARKET_RAW" > "$TMPDIR/market.json"
echo "$MODEL_RAW" > "$TMPDIR/model.json"

# 4. Transform to market_intelligence.json
echo "▶ Transforming data..."
python3 - "$TMPDIR" "$DATA_DIR" <<'PYEOF'
import json, sys
from datetime import datetime, timezone
from pathlib import Path

tmpdir = Path(sys.argv[1])
data_dir = Path(sys.argv[2])

market = json.loads((tmpdir / "market.json").read_text())
model = json.loads((tmpdir / "model.json").read_text())

output = {
    "meta": {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "KANTEISHI API /market/stats (live sync)",
        "model_version": market["overview"].get("model_version", model.get("version", "0.5"))
    },
    "stats": {
        "total_records": market["overview"]["total_lots"],
        "total_artists": market["overview"]["total_artists"],
        "categories_covered": 8,
        "auction_houses": 3,
        "total_market_value": market["overview"]["total_tracked_value_jpy"],
        "r2_ensemble": round(market["overview"]["r2_ensemble"], 3),
        "median_error_pct": round(market["overview"]["median_error_pct"], 1),
        "sbi_lots": market["overview"]["sbi_lots"],
        "shinwa_lots": market["overview"]["shinwa_lots"]
    },
    "top_artists_by_volume": market["top_artists_by_volume"],
    "top_artists_by_value": market["top_artists_by_value"],
    "auction_houses": [
        {"name": "SBI Art Auction", "lots": market["overview"]["sbi_lots"], "source": "sbi"},
        {"name": "Shinwa Auction", "lots": market["overview"]["shinwa_lots"], "source": "shinwa"},
        {"name": "Mainichi Auction", "lots": market["overview"]["total_lots"] - market["overview"]["sbi_lots"] - market["overview"]["shinwa_lots"], "source": "mainichi"}
    ]
}

(data_dir / "market_intelligence.json").write_text(
    json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f'  ✓ market_intelligence.json updated ({output["stats"]["total_records"]:,} lots)')
PYEOF

# 5. Summary
echo ""
echo "═══ Sync Complete ═══"
echo "  Updated: market_intelligence.json"
echo "  Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""
echo "  To deploy: git add data/ && git commit -m 'sync: market data' && git push"
