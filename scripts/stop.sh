#!/usr/bin/env bash
set -euo pipefail
pkill -f "python3 -m shorts_bot.web" 2>/dev/null && echo "Stopped web UI" || echo "Web UI not running"
