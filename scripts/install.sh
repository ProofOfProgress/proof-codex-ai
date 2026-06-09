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
  echo "    Add OPENAI_API_KEY to .env for full chat (optional for offline mode)."
fi

mkdir -p data

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
