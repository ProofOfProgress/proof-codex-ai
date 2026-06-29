#!/usr/bin/env bash
# Ping desktop helper; start it on Windows if down. Run on hub WSL (or via hub_run.sh from cloud).
# Uses curl + PowerShell only — no WSL pip / pydantic required.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

ENV_FILE="$ROOT/data/desktop_hub/helper.env"
if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi
DESKTOP_HELPER_TOKEN="${DESKTOP_HELPER_TOKEN:-}"
DESKTOP_HELPER_TOKEN="${DESKTOP_HELPER_TOKEN// /}"

windows_host() {
  if [[ -n "${DESKTOP_HELPER_HOST:-}" ]]; then
    echo "$DESKTOP_HELPER_HOST"
    return
  fi
  awk '/^nameserver / {print $2; exit}' /etc/resolv.conf 2>/dev/null || echo "127.0.0.1"
}

ping_helper_curl() {
  local host token
  host="$(windows_host)"
  token="${DESKTOP_HELPER_TOKEN:-}"
  if [[ -z "$token" ]]; then
    return 1
  fi
  curl -sf --max-time 5 \
    -X POST "http://${host}:${DESKTOP_HELPER_PORT:-9876}/v1/command" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${token}" \
    -d '{"action":"ping"}' \
    | grep -q '"ok"[[:space:]]*:[[:space:]]*true'
}

launch_windows_helper_ps() {
  local ps repo_win ps1_win
  ps="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
  if [[ ! -f "$ps" ]]; then
    ps="/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/powershell.exe"
  fi
  if [[ ! -f "$ps" ]]; then
    echo "PowerShell not found — run START_DESKTOP_HELPER.bat on Windows" >&2
    return 1
  fi
  repo_win="$("$ps" -NoProfile -Command "wslpath -w '$ROOT'" 2>/dev/null || wslpath -w "$ROOT")"
  ps1_win="$("$ps" -NoProfile -Command "wslpath -w '$ROOT/scripts/desktop_helper_start_background.ps1'" 2>/dev/null || wslpath -w "$ROOT/scripts/desktop_helper_start_background.ps1")"
  "$ps" -NoProfile -ExecutionPolicy Bypass -Command "\$env:DESKTOP_HUB_REPO_WIN='$repo_win'; & '$ps1_win'"
}

if ping_helper_curl; then
  echo "Desktop helper already running."
  exit 0
fi

echo "Desktop helper not running — launching on Windows..."
launch_windows_helper_ps

for _ in 1 2 3 4 5; do
  sleep 2
  if ping_helper_curl; then
    echo "Desktop helper started."
    exit 0
  fi
done

echo "Helper launch attempted but ping failed — is Windows logged in?" >&2
exit 1
