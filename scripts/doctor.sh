#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

ok=0
warn=0
fail=0

pass() { echo "  OK   $1"; ok=$((ok + 1)); }
note() { echo "  WARN $1"; warn=$((warn + 1)); }
bad()  { echo "  FAIL $1"; fail=$((fail + 1)); }

echo "==> Shorts Bot doctor"
echo ""

# Python
if command -v python3 >/dev/null 2>&1; then
  pass "python3 $(python3 --version 2>&1 | awk '{print $2}')"
else
  bad "python3 not found"
fi

# Dependencies
if python3 -c "import fastapi, googleapiclient" 2>/dev/null; then
  pass "Python packages installed"
else
  bad "Missing packages — run: bash scripts/install.sh"
fi

# .env
if [ -f .env ]; then
  pass ".env exists"
else
  note ".env missing — run: cp .env.example .env"
fi

# Google credentials
if [ -f .env ] && grep -qE '^GOOGLE_CLIENT_ID=.+' .env 2>/dev/null && ! grep -q 'your-client-id' .env 2>/dev/null; then
  pass "GOOGLE_CLIENT_ID set"
else
  note "GOOGLE_CLIENT_ID not set — see docs/TOMORROW.md"
fi

if [ -f .env ] && grep -qE '^GOOGLE_CLIENT_SECRET=.+' .env 2>/dev/null && ! grep -q 'your-client-secret' .env 2>/dev/null; then
  pass "GOOGLE_CLIENT_SECRET set"
else
  note "GOOGLE_CLIENT_SECRET not set — see docs/TOMORROW.md"
fi

# YouTube token
if [ -f data/youtube_token.json ]; then
  pass "YouTube OAuth token saved"
else
  note "YouTube not connected — run: python3 -m shorts_bot.youtube.auth_cli"
fi

# OpenAI (optional)
if [ -f .env ] && grep -qE '^OPENAI_API_KEY=sk-' .env 2>/dev/null && ! grep -qi 'your-key' .env 2>/dev/null; then
  pass "OPENAI_API_KEY set (smarter chat)"
else
  note "OPENAI_API_KEY not set — offline mode still works"
fi

# Tests
echo ""
echo "==> Running quick tests..."
if python3 -m pytest tests/ -q --tb=no 2>/dev/null; then
  pass "All tests pass"
else
  bad "Tests failed — run: python3 -m pytest tests/ -v"
fi

echo ""
echo "Summary: $ok passed, $warn warnings, $fail failures"
echo ""
if [ "$fail" -gt 0 ]; then
  echo "Fix failures above before starting."
  exit 1
fi
if [ "$warn" -gt 0 ]; then
  echo "Warnings are OK for first run — follow docs/TOMORROW.md"
fi
echo "Start the bot: bash scripts/start.sh"
echo ""
