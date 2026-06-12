#!/usr/bin/env bash
# Validate Slack Option A secrets, sync .env, send test email to #peripheral-ops.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Slack Option A — Gmail → channel email"
echo ""

missing=0
for k in SLACK_CHANNEL_EMAIL GMAIL_SMTP_USER GMAIL_SMTP_APP_PASSWORD; do
  v="${!k:-}"
  if [ -z "$v" ]; then
    if grep -q "^${k}=." .env 2>/dev/null && ! grep -q "^${k}=your" .env 2>/dev/null; then
      echo "  OK  $k (in .env)"
    else
      echo "  MISSING  $k"
      missing=$((missing + 1))
    fi
  else
    echo "  OK  $k (environment)"
  fi
done

if [ "$missing" -gt 0 ]; then
  echo ""
  echo "Add missing secrets in Cursor → Cloud Agent → Secrets, then re-run:"
  echo "  bash scripts/install.sh && bash scripts/slack-email-ready.sh"
  echo "Guide: docs/FOR_OWNER_SLACK_EMAIL.md"
  exit 1
fi

echo ""
echo "==> Syncing secrets → .env"
python3 scripts/sync_secrets.py

# Defaults for email-only mode when not set
grep -q '^SLACK_POST_MODE=' .env 2>/dev/null || echo 'SLACK_POST_MODE=email' >> .env
grep -q '^SLACK_CHANNEL_NAME=' .env 2>/dev/null || echo 'SLACK_CHANNEL_NAME=peripheral-ops' >> .env
grep -q '^SLACK_NOTIFY_ENABLED=' .env 2>/dev/null || echo 'SLACK_NOTIFY_ENABLED=true' >> .env

echo "==> Sending test message…"
python3 -m shorts_bot.integrations test
echo ""
echo "Check #peripheral-ops in Slack — should see an email from your Gmail."
