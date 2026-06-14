#!/usr/bin/env bash
# Download Proscenium Blender addon (real motion AI — not Gemini/Cursor).
# Usage:
#   bash scripts/install_proscenium.sh          # Blender 5.0+ (default)
#   bash scripts/install_proscenium.sh --blender4   # Blender 4.2–4.4
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/channel/tools/proscenium"
mkdir -p "$DEST"

BLENDER4=false
if [[ "${1:-}" == "--blender4" ]]; then
  BLENDER4=true
fi

if $BLENDER4; then
  URL="https://github.com/animatica-ai/proscenium-blender/releases/download/v0.3.2/proscenium-blender-v0.3.2.zip"
  OUT="$DEST/proscenium-blender-v0.3.2.zip"
  VER="Blender 4.2–4.4"
else
  URL="https://github.com/animatica-ai/proscenium-blender/releases/download/v0.4.0/proscenium-blender-0.4.0.zip"
  OUT="$DEST/proscenium-blender-0.4.0.zip"
  VER="Blender 5.0+"
fi

echo "Downloading Proscenium for $VER..."
curl -fsSL "$URL" -o "$OUT"
echo "Ready: $OUT"
echo ""
echo "In Blender ($VER):"
echo "  Edit → Preferences → Add-ons → Install from Disk… → pick zip above"
echo "  Search: Proscenium → enable Proscenium — AI Motion Generation"
echo "  Sign in at animatica.ai — see docs/FOR_OWNER_PROSCENIUM.md"
