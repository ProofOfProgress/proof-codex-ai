#!/usr/bin/env bash
# Ping desktop helper; start it on Windows if down. Run on hub WSL (or via hub_run.sh from cloud).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if python3 -m shorts_bot.desktop_hub.cli ping 2>/dev/null; then
  echo "Desktop helper already running."
  exit 0
fi

echo "Desktop helper not running — launching on Windows..."
python3 -c "from shorts_bot.desktop_hub.launcher import launch_windows_helper; launch_windows_helper()"

for _ in 1 2 3 4 5; do
  sleep 2
  if python3 -m shorts_bot.desktop_hub.cli ping 2>/dev/null; then
    echo "Desktop helper started."
    exit 0
  fi
done

echo "Helper launch attempted but ping failed — is Windows logged in?" >&2
exit 1
