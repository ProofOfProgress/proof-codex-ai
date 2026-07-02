#!/usr/bin/env bash
# Run product scout ON the hub (Kalodata UI needs hub browser session).
# Cloud CEO: bash scripts/scout_on_hub.sh run --preset middle_core --limit 10
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ "${1:-}" == "run" ]]; then
  shift
  REMOTE=(python3 -m shorts_bot.tiktok_shop.scout_cli run "$@")
else
  REMOTE=(python3 -m shorts_bot.tiktok_shop.scout_cli "${1:-status}")
  shift || true
fi

exec python3 -m shorts_bot.hub_remote run -- "${REMOTE[@]}"
