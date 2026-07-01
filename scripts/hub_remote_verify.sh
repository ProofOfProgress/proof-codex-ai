#!/usr/bin/env bash
# Cloud agent: join tailnet (if configured) and SSH test to owner hub.
set -euo pipefail

# shellcheck disable=SC1091
source "$(dirname "$0")/hub_lib.sh"
hub_lib_init

hub_ensure_connected || exit 1

port="$(hub_ssh_port)"
if hub_verify_ssh; then
  exit 0
fi

if [[ "$port" == "22" ]]; then
  hub_log "Retrying SSH on port 2222 (Windows gateway)..."
  HUB_SSH_PORT=2222 hub_verify_ssh && exit 0
fi

hub_log ""
hub_log "On the HP laptop (Admin PowerShell):"
hub_log "  powershell -ExecutionPolicy Bypass -File scripts\\INSTALL_HUB_ALL_LOCAL.ps1"
hub_log "Then run: powershell -File scripts\\hub_print_secrets_for_cursor.ps1"
hub_log "Update Cursor secrets → NEW agent run → try hub verify"
exit 1
