#!/usr/bin/env bash
# Ping desktop helper from WSL (Windows host IP auto-detected).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 -m shorts_bot.desktop_hub.cli ping "$@"
