#!/usr/bin/env bash
# Download Proscenium Blender addon (real motion AI — not Gemini/Cursor).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/channel/tools/proscenium"
mkdir -p "$DEST"
URL="https://github.com/animatica-ai/proscenium-blender/releases/download/v0.4.0/proscenium-blender-0.4.0.zip"
OUT="$DEST/proscenium-blender-0.4.0.zip"
echo "Downloading Proscenium addon..."
curl -fsSL "$URL" -o "$OUT"
echo "Ready: $OUT"
echo ""
echo "Next (on a machine with Blender 5.0+):"
echo "  Blender → Edit → Preferences → Add-ons → Install → select zip above"
echo "  Sign in at animatica.ai — see docs/FOR_OWNER_PROSCENIUM.md"
