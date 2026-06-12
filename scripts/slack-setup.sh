#!/usr/bin/env bash
# Print Slack setup steps — owner completes OAuth in browser (~10 min).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=============================================="
echo "  Peripheral — Slack setup (~10 min)"
echo "=============================================="
echo ""
echo "Two integrations (use both):"
echo "  1. @cursor app     — you message Slack → Cloud Agent runs → replies in thread"
echo "  2. Incoming webhook — bot posts pipeline alerts to your channel"
echo ""
echo "--- Part 1: @cursor (main loop) ---"
echo "  1. Open: https://cursor.com/dashboard?tab=integrations"
echo "  2. Connect Slack → install Cursor app in workspace"
echo "  3. Connect GitHub → repo ProofOfProgress/proof-codex-ai"
echo "  4. In Slack: create public channel #dont-blink-ops"
echo "  5. /invite @cursor"
echo "  6. Type: @cursor help → Link Account (OAuth)"
echo "  7. @cursor settings → default repo proof-codex-ai"
echo ""
echo "--- Part 2: Slack MCP (agents post while grinding) ---"
echo "  1. Cursor Desktop → Marketplace → Slack MCP → Connect"
echo "  2. Dashboard → Integrations → enable Slack MCP for Cloud Agents"
echo "  3. Slack admin may need to approve the MCP app"
echo ""
echo "--- Part 3: Webhook (pipeline alerts) ---"
echo "  1. Slack → Apps → Incoming Webhooks → Add to #dont-blink-ops"
echo "  2. Copy webhook URL → Cursor Secrets as SLACK_WEBHOOK_URL"
echo "  3. bash scripts/install.sh"
echo "  4. python3 -m shorts_bot.integrations test"
echo ""
echo "--- Test @cursor ---"
echo '  @cursor agent in proof-codex-ai, read docs/SLACK_CURSOR_SETUP.md and reply OK'
echo ""
echo "Full guide: docs/SLACK_CURSOR_SETUP.md"
echo "Checklist:  data/SLACK_SETUP_CHECKLIST.md"
echo ""

if command -v python3 >/dev/null 2>&1; then
  python3 -m shorts_bot.integrations status 2>/dev/null || true
fi
