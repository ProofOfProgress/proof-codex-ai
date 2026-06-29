#!/usr/bin/env bash
# Cloud agent: join tailnet (if configured) and SSH test to owner hub.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Load .env if present (local VM)
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env 2>/dev/null || true
  set +a
fi

join_tailscale() {
  if [[ -z "${TAILSCALE_AUTH_KEY:-}" ]]; then
    echo "TAILSCALE_AUTH_KEY not set — skip tailscale join (hub may still work if VM already on tailnet)"
    return 0
  fi
  if ! command -v tailscale >/dev/null 2>&1; then
    echo "Installing tailscale on cloud VM..."
    curl -fsSL https://tailscale.com/install.sh | sh
  fi
  if ! tailscale status >/dev/null 2>&1; then
    sudo tailscale up --auth-key="${TAILSCALE_AUTH_KEY}" --hostname=cursor-cloud-agent --accept-routes
  fi
  echo "Cloud VM Tailscale IP: $(tailscale ip -4 2>/dev/null || echo unknown)"
}

ssh_hub() {
  local host user keyfile
  host="${HUB_SSH_HOST:-}"
  user="${HUB_SSH_USER:-}"
  if [[ -z "$host" || -z "$user" ]]; then
    echo "ERROR: Set HUB_SSH_HOST and HUB_SSH_USER in Cursor Secrets"
    exit 1
  fi
  if [[ -z "${HUB_SSH_PRIVATE_KEY:-}" ]]; then
    echo "ERROR: Set HUB_SSH_PRIVATE_KEY in Cursor Secrets"
    exit 1
  fi
  keyfile="$(mktemp)"
  trap 'rm -f "$keyfile"' EXIT
  printf '%s\n' "$HUB_SSH_PRIVATE_KEY" > "$keyfile"
  chmod 600 "$keyfile"

  echo "SSH test → ${user}@${host} ..."
  ssh -i "$keyfile" \
    -o StrictHostKeyChecking=accept-new \
    -o ConnectTimeout=15 \
    "${user}@${host}" \
    'echo "Hub OK: $(hostname) $(uname -a)"; command -v python3 && python3 --version; test -d proof-codex-ai && echo "repo: ~/proof-codex-ai exists" || echo "repo: not cloned yet (run git clone)"'
  echo "Hub remote access: OK"
}

join_tailscale
ssh_hub
