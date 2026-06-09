#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
STAMP=$(date -u +%Y%m%d-%H%M%S)
DEST="data/backups"
mkdir -p "$DEST"
if [ -f data/shorts_bot.db ]; then
  cp data/shorts_bot.db "$DEST/shorts_bot-$STAMP.db"
  echo "Backed up to $DEST/shorts_bot-$STAMP.db"
else
  echo "No database yet — nothing to backup"
fi
