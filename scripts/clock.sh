#!/usr/bin/env bash
# Agent clock — quick time check (UTC + owner local).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m src.clock "$@"
