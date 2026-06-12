#!/usr/bin/env bash
# Add your OpenAI API key so chat works tonight.
# Usage:
#   bash scripts/set-openai-key.sh              # reads OPENAI_API_KEY from env
#   bash scripts/set-openai-key.sh sk-abc...    # pass key as argument
set -euo pipefail
cd "$(dirname "$0")/.."

KEY="${1:-${OPENAI_API_KEY:-}}"

if [ -z "$KEY" ]; then
  echo ""
  echo "OpenAI API key needed for full chat (separate from ChatGPT Pro)."
  echo "Get one at: https://platform.openai.com/api-keys"
  echo ""
  echo "Paste your key (starts with sk-), then press Enter:"
  read -rs KEY
  echo ""
fi

if [ -z "$KEY" ] || echo "$KEY" | grep -qi 'your-key'; then
  echo "No valid key provided."
  exit 1
fi

export OPENAI_API_KEY="$KEY"
python3 scripts/sync_secrets.py

echo ""
echo "OpenAI key saved to .env"
echo "Start chat: bash scripts/start.sh"
echo "Open:       http://localhost:8080"
echo ""
