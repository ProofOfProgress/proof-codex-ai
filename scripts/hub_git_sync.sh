#!/usr/bin/env bash
# Pull latest branch on owner hub WSL (after cloud agent pushed).
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck disable=SC1091
source "$(dirname "$0")/hub_lib.sh"
hub_lib_init

BRANCH="${1:-cursor/scout-research-backends-ba97}"
hub_ensure_connected || exit 1

hub_run_ssh "cd ~/proof-codex-ai && git fetch origin ${BRANCH} && git checkout ${BRANCH} && git pull --ff-only origin ${BRANCH} && git log -1 --oneline"
