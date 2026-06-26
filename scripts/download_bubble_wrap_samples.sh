#!/usr/bin/env bash
# Download owner bubble wrap sample PNGs from Google Drive (gitignored locally).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/data/research/course/_media/bubble_wrap/samples"
mkdir -p "$DEST"
python3 -m gdown --folder \
  "https://drive.google.com/drive/folders/1drt1xcaakCDMQ2ABJsJpeOYW7XDnHqDB" \
  -O "$DEST"
echo "Samples in: $DEST"
