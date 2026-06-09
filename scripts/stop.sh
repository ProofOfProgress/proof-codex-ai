#!/usr/bin/env bash
# Stop Shorts Bot web + Discord if running locally
set -euo pipefail
pkill -f "python3 -m shorts_bot.web" 2>/dev/null && echo "Stopped web" || echo "Web not running"
pkill -f "python3 -m shorts_bot.discord_bot" 2>/dev/null && echo "Stopped Discord" || echo "Discord not running"
