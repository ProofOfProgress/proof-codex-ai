#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Syncing secrets from environment (if any)..."
python3 scripts/sync_secrets.py 2>/dev/null || true

if grep -qE '^OPENAI_API_KEY=sk-' .env 2>/dev/null && ! grep -qi 'your-key' .env 2>/dev/null; then
  echo "    Chat mode: full (OpenAI connected)"
else
  echo "    Chat mode: offline — run: bash scripts/set-openai-key.sh"
fi

echo "==> Starting Shorts Bot web UI..."
echo "    Open: http://localhost:8080"
echo "    Stop: Ctrl+C"
echo ""

python3 -m shorts_bot.web
