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
echo "  Chat interface:  python3 -m shorts_bot.web"
echo "  Then open:     http://localhost:8080"
echo ""
echo "  CLI chat:      python3 -m shorts_bot"
echo ""
