#!/usr/bin/env bash
# Cloud agent: join tailnet (if configured) and SSH test to owner hub.
set -euo pipefail

# shellcheck disable=SC1091
source "$(dirname "$0")/hub_lib.sh"
hub_lib_init

hub_ensure_connected || exit 1
hub_verify_ssh
