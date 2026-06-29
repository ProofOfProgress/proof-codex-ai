#!/usr/bin/env bash
# Install Windows Python + desktop helper deps on hub laptop (run via hub SSH / hub_run.sh).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

PS="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
if [[ ! -f "$PS" ]]; then
  PS="/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/powershell.exe"
fi

run_ps() {
  local script_win
  script_win=$(wslpath -w "$1")
  "$PS" -NoProfile -ExecutionPolicy Bypass -File "$script_win"
}

echo "=== Step 1: Windows Python ==="
if "$PS" -NoProfile -Command "python -c 'import sys; print(sys.version)'" 2>/dev/null; then
  echo "Windows Python already OK"
else
  echo "Installing Python on Windows (may take 2-3 min)..."
  run_ps "$ROOT/scripts/desktop_helper/install_windows_python.ps1"
fi

echo "=== Step 2: Desktop helper pip deps ==="
run_ps "$ROOT/scripts/desktop_helper_install.ps1"

echo "=== Step 3: helper.env ==="
ENV_FILE="$ROOT/data/desktop_hub/helper.env"
if [[ ! -f "$ENV_FILE" ]]; then
  cp "$ROOT/data/desktop_hub/helper.env.example" "$ENV_FILE"
  if [[ -n "${DESKTOP_HELPER_TOKEN:-}" ]]; then
    # Strip whitespace from token
    tok=$(echo "$DESKTOP_HELPER_TOKEN" | tr -d '[:space:]')
    sed -i "s/paste-your-token-here-no-spaces/${tok}/" "$ENV_FILE"
    echo "Wrote token from cloud secrets to helper.env"
  else
    echo "WARNING: DESKTOP_HELPER_TOKEN not in cloud env - owner must edit helper.env on hub"
  fi
else
  echo "helper.env already exists"
fi

echo "=== Done ==="
wslpath -w "$ROOT/scripts/START_DESKTOP_HELPER.bat"
