#!/usr/bin/env bash
# Write hub-only credentials (gitignored). Usage:
#   bash scripts/save_agent_credentials.sh
# Or set vars and run once on hub.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/data/agent_credentials.env"
mkdir -p "$(dirname "$OUT")"
if [[ -f "$OUT" ]]; then
  echo "Already exists: $OUT (not overwriting — edit manually on hub)"
  exit 0
fi
cat >"$OUT" <<'EOF'
# GITIGNORED — agent + course logins. Never commit.
# Add matching keys to Cursor Secrets for cloud agents (new run after edit).

# Agent email (owner-assigned)
AGENT_EMAIL=
AGENT_EMAIL_PASSWORD=

# Momentum Academy — https://app.momentumacademy.co
COURSE_SITE_URL=https://app.momentumacademy.co
COURSE_LOGIN_EMAIL=
COURSE_LOGIN_PASSWORD=

# Discord web (Playwright profile — separate from desktop app)
DISCORD_LOGIN_EMAIL=
DISCORD_LOGIN_PASSWORD=
EOF
chmod 600 "$OUT"
echo "Template written: $OUT — fill on hub only"
