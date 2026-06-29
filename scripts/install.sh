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

if [[ -n "${HUB_SSH_HOST:-}" && -n "${HUB_SSH_USER:-}" && -n "${HUB_SSH_PRIVATE_KEY:-}" ]]; then
  echo "==> Hub secrets detected — auto-connecting to owner laptop..."
  bash scripts/hub_connect.sh --quiet || echo "    WARN: hub offline (laptop asleep or Tailscale down on HP)"
fi

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
echo "  YouTube connect (once): python3 -m shorts_bot.youtube.auth_cli  (API upload, not Playwright)"
echo "  CLI chat:             python3 -m shorts_bot"
echo "  Seed starter drafts:  python3 scripts/seed_starter_drafts.py"
echo "  Channel setup copy:   docs/YOUTUBE_CHANNEL_SETUP.md"
echo ""
