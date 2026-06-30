#!/usr/bin/env bash
# Cloud agent: type a message into Cursor chat on the hub and click Send.
set -euo pipefail

MSG="${1:-Hub CEO test message from cloud agent.}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/data/desktop_hub/helper.env"

WIN="$(grep nameserver /etc/resolv.conf | awk '{print $2}')"
URL="http://${WIN}:9876/v1/command"
AUTH="Authorization: Bearer ${DESKTOP_HELPER_TOKEN}"

PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
COORDS="$("$PS" -NoProfile -ExecutionPolicy Bypass -File "$ROOT/scripts/hub_cursor_window_coords.ps1" | tr -d '\r')"
read -r IX IY SX SY <<< "$COORDS"

post() {
  curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" -d "$1" "$URL"
}

echo "Cursor coords: input=${IX},${IY} send=${SX},${SY}"
post "$(python3 -c "import json; print(json.dumps({'action':'click','x':${IX},'y':${IY},'button':'left'}))")" >/dev/null
sleep 0.5
post "$(python3 -c "import json; print(json.dumps({'action':'type','text':'''${MSG}'''}))")" >/dev/null
sleep 0.5
post "$(python3 -c "import json; print(json.dumps({'action':'click','x':${SX},'y':${SY},'button':'left'}))")"
echo ""
echo "Sent via desktop helper."
