#!/usr/bin/env bash
# Run a command on the owner hub. Auto-connects first if needed.
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: bash scripts/hub_run.sh [--] <remote command...>" >&2
  echo "Example: bash scripts/hub_run.sh python3 --version" >&2
  exit 2
fi

if [[ "$1" == "--" ]]; then
  shift
fi

# shellcheck disable=SC1091
source "$(dirname "$0")/hub_lib.sh"
hub_lib_init

hub_ensure_connected || exit 1
hub_run_ssh "$@"
