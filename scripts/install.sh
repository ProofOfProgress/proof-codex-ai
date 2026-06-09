#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Installing Shorts Bot dependencies..."
python3 -m pip install -r requirements.txt

echo "==> Installing Playwright Chromium (for YouTube/CapCut later)..."
python3 -m playwright install chromium

if [ ! -f .env ]; then
  echo "==> Creating .env from .env.example"
  cp .env.example .env
fi

echo "==> Syncing API keys from environment (Cursor secrets)..."
python3 scripts/sync_secrets.py 2>/dev/null || true
echo "    Full chat: bash scripts/set-openai-key.sh  (or add OPENAI_API_KEY to Cursor secrets)"

mkdir -p data

chmod +x scripts/*.sh 2>/dev/null || true

echo "==> Running tests..."
python3 -m pytest tests/ -q

echo ""
echo "==> Shorts Bot installed."
echo ""
echo "  Tomorrow setup:  see docs/TOMORROW.md"
echo "  Health check:    bash scripts/doctor.sh"
echo "  Start web UI:    bash scripts/start.sh"
echo "  Then open:       http://localhost:8080"
echo ""
echo "  YouTube connect (once): python3 -m shorts_bot.youtube.auth_cli"
echo "  CLI chat:             python3 -m shorts_bot"
echo ""
