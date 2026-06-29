#!/usr/bin/env bash
# Quick ADB health check — run on hub laptop or via: bash scripts/hub_run.sh bash scripts/hub_adb_check.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0
pass() { echo "  OK   $1"; }
bad()  { echo "  FAIL $1"; fail=1; }
note() { echo "  WARN $1"; }

echo "==> Phone hub ADB check"
echo ""

if command -v adb >/dev/null 2>&1; then
  pass "adb installed: $(adb version 2>/dev/null | head -1)"
else
  bad "adb not installed — run: bash scripts/hub_adb_install.sh"
  exit 1
fi

devices="$(adb devices 2>/dev/null | tail -n +2 | grep -v '^$' || true)"
if [[ -z "$devices" ]]; then
  note "No phones connected (expected until hardware arrives)"
else
  pass "Connected devices:"
  echo "$devices" | sed 's/^/        /'
fi

if [[ -f data/phone_hub/devices.json ]]; then
  pass "devices.json exists"
  unset_serials="$(python3 -c "
import json
from pathlib import Path
rows = json.loads(Path('data/phone_hub/devices.json').read_text()).get('slots', [])
print(sum(1 for r in rows if not (r.get('adb_serial') or '').strip()))
")"
  if [[ "$unset_serials" -gt 0 ]]; then
    note "$unset_serials slot(s) missing adb_serial — fill when phones arrive"
  fi
else
  note "devices.json missing — run: python3 -m shorts_bot.phone_hub.cli init-devices"
fi

python3 -m shorts_bot.phone_hub.cli status 2>/dev/null || note "phone_hub status skipped"

echo ""
if [[ "$fail" -gt 0 ]]; then
  exit 1
fi
echo "ADB check done."
