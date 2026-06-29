#!/usr/bin/env bash
# Auto-connect cloud agent to owner hub (Tailscale + SSH ready). Idempotent.
set -euo pipefail

HUB_QUIET=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --quiet|-q) HUB_QUIET=1; shift ;;
    -h|--help)
      echo "Usage: bash scripts/hub_connect.sh [--quiet]"
      echo "Joins Tailscale (if configured) so hub SSH works. Safe to run repeatedly."
      exit 0
      ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

# shellcheck disable=SC1091
source "$(dirname "$0")/hub_lib.sh"
hub_lib_init

if ! hub_secrets_configured; then
  hub_log "Hub secrets not configured — nothing to connect"
  exit 0
fi

hub_ensure_connected
