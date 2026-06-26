#!/usr/bin/env bash
# Install the vendored Higgsfield Cursor plugin for Desktop (~2 min).
set -euo pipefail
cd "$(dirname "$0")/.."

PLUGIN_SRC=".cursor/plugins/higgsfield"
PLUGIN_DST="${HOME}/.cursor/plugins/local/higgsfield"
MCP_EXAMPLE=".cursor/mcp.json.example"
MCP_DEST=".cursor/mcp.json"

echo "=============================================="
echo "  Proof Codex — Higgsfield setup (~2 min)"
echo "=============================================="
echo ""
echo "Course use: Module 4 images (9:16, 2K) + Module 5 video (Kling 2.6, 5s)."
echo "Guide: docs/FOR_OWNER_HIGGSFIELD_SETUP.md"
echo ""

if [[ ! -d "$PLUGIN_SRC/.cursor-plugin" ]]; then
  echo "ERROR: Missing $PLUGIN_SRC — pull latest proof-codex-ai first."
  exit 1
fi

echo "--- Part 1: Copy plugin into Cursor (Desktop) ---"
mkdir -p "${HOME}/.cursor/plugins/local"
rm -rf "$PLUGIN_DST"
cp -r "$PLUGIN_SRC" "$PLUGIN_DST"
echo "  Installed: $PLUGIN_DST"
echo ""

echo "--- Part 2: MCP config (optional) ---"
if [[ -f "$MCP_DEST" ]]; then
  echo "  $MCP_DEST already exists — merge higgsfield entry manually if missing."
  echo "  Reference: $MCP_EXAMPLE"
else
  cp "$MCP_EXAMPLE" "$MCP_DEST"
  echo "  Created $MCP_DEST from example (Slack + Higgsfield)."
fi
echo ""

echo "--- Part 3: Reload + sign in ---"
echo "  1. Cursor Desktop → Developer: Reload Window"
echo "  2. Settings → Plugins → confirm Higgsfield is listed"
echo "  3. Settings → Tools & MCP → higgsfield → Connect / sign in (OAuth)"
echo "  4. Cloud agents: Dashboard → Integrations → enable Higgsfield MCP"
echo "  5. Start a new cloud agent run after auth"
echo ""
echo "--- Test in chat ---"
echo '  Generate a 9:16 test product image on a marble vanity, photorealistic'
echo '  Or: /higgs Make a 5s vertical clip — slow arc camera, product centered'
echo ""
