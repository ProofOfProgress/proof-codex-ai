#!/usr/bin/env bash
# Install desktop helper deps (WSL or Windows Python in PATH).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 -m pip install -r scripts/desktop_helper/requirements.txt
echo "Desktop helper deps installed."
