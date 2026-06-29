#!/usr/bin/env bash
# Capture phone screen + UI text (+ optional Gemini describe) — cloud agent can run via hub_run.sh
# Usage: bash scripts/hub_phone_screen.sh phone_1
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SLOT="${1:-phone_1}"
DESCRIBE="${PHONE_SCREEN_DESCRIBE:-1}"

# WSL hub: USB phone is visible to Windows adb, not Linux adb
if [[ -z "${PHONE_HUB_ADB:-}" ]]; then
  WIN="$HOME/android-sdk/platform-tools/adb"
  WIN_EXE="/mnt/c/Users/isaac/android-sdk/platform-tools/adb.exe"
  if [[ -x "$WIN_EXE" ]]; then
    export PHONE_HUB_ADB="$WIN_EXE"
  elif [[ -x "$WIN" ]]; then
    export PHONE_HUB_ADB="$WIN"
  fi
fi

ARGS=(--slot "$SLOT")
if [[ "$DESCRIBE" == "0" ]]; then
  ARGS+=(--no-describe)
fi

python3 -m shorts_bot.phone_hub.cli screen-report "${ARGS[@]}"
