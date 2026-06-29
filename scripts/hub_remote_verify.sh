#!/usr/bin/env bash
# Cloud agent: join tailnet (if configured) and SSH test to owner hub.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TS_SOCKET="${TS_SOCKET:-/var/run/tailscale/tailscaled.sock}"
TS_STATE="${TS_STATE:-/var/lib/tailscale/tailscaled.state}"
TS_SOCKS="${TS_SOCKS:-127.0.0.1:1055}"

# Load .env if present (local VM)
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env 2>/dev/null || true
  set +a
fi

# Cursor secret typo seen in the wild: TALESCALE_AUTH_KEY (missing "I").
TAILSCALE_AUTH_KEY="${TAILSCALE_AUTH_KEY:-${TALESCALE_AUTH_KEY:-}}"

tailscale_cli() {
  tailscale --socket="$TS_SOCKET" "$@"
}

normalize_openssh_key() {
  python3 - "$1" <<'PY'
import sys
from pathlib import Path

raw = Path(sys.argv[1]).read_text()
begin = "-----BEGIN OPENSSH PRIVATE KEY-----"
end = "-----END OPENSSH PRIVATE KEY-----"
lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
body: list[str] = []
seen_begin = False
seen_end = False
for ln in lines:
    if ln == begin:
        if not seen_begin:
            body.append(ln)
            seen_begin = True
        continue
    if ln == end:
        if not seen_end:
            body.append(end)
            seen_end = True
        continue
    if seen_begin and not seen_end:
        body.append(ln)
if body and body[0] == begin and (len(body) == 1 or body[-1] != end):
    body.append(end)
Path(sys.argv[1]).write_text("\n".join(body) + "\n")
PY
}

start_tailscaled() {
  sudo mkdir -p /var/run/tailscale /var/lib/tailscale
  sudo pkill tailscaled 2>/dev/null || true
  sleep 1

  local tun_mode="tailscale0"
  if [[ ! -e /dev/net/tun ]]; then
    echo "No /dev/net/tun — using Tailscale userspace-networking (cloud VM)"
    tun_mode="userspace-networking"
  fi

  if [[ "$tun_mode" == "userspace-networking" ]]; then
    sudo tailscaled \
      --tun=userspace-networking \
      --socks5-server="localhost:${TS_SOCKS##*:}" \
      --outbound-http-proxy-listen="localhost:${TS_SOCKS##*:}" \
      --state="$TS_STATE" \
      --socket="$TS_SOCKET" &
  else
    if command -v systemctl >/dev/null 2>&1 && systemctl is-system-running >/dev/null 2>&1; then
      sudo systemctl start tailscaled
    else
      sudo tailscaled --state="$TS_STATE" --socket="$TS_SOCKET" &
    fi
  fi

  for _ in $(seq 1 30); do
    if [[ -S "$TS_SOCKET" ]]; then
      return 0
    fi
    sleep 1
  done
  echo "ERROR: tailscaled did not start (no socket at $TS_SOCKET)"
  exit 1
}

join_tailscale() {
  if [[ -z "${TAILSCALE_AUTH_KEY:-}" ]]; then
    echo "TAILSCALE_AUTH_KEY not set — skip tailscale join (hub may still work if VM already on tailnet)"
    return 0
  fi
  if ! command -v tailscale >/dev/null 2>&1; then
    echo "Installing tailscale on cloud VM..."
    curl -fsSL https://tailscale.com/install.sh | sh
  fi
  if ! tailscale_cli status >/dev/null 2>&1; then
    start_tailscaled
    sudo tailscale_cli up \
      --auth-key="${TAILSCALE_AUTH_KEY}" \
      --hostname=cursor-cloud-agent \
      --accept-routes
  fi
  echo "Cloud VM Tailscale IP: $(tailscale_cli ip -4 2>/dev/null || echo unknown)"
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
  # shellcheck disable=SC2064
  trap "rm -f '$keyfile'" EXIT
  printf '%s\n' "$HUB_SSH_PRIVATE_KEY" > "$keyfile"
  normalize_openssh_key "$keyfile"
  chmod 600 "$keyfile"
  if ! ssh-keygen -y -f "$keyfile" >/dev/null 2>&1; then
    echo "ERROR: HUB_SSH_PRIVATE_KEY is invalid (check for duplicate BEGIN/END lines in Cursor Secrets)"
    exit 1
  fi

  local -a ssh_opts=(
    -i "$keyfile"
    -o StrictHostKeyChecking=accept-new
    -o ConnectTimeout=20
  )
  if [[ ! -e /dev/net/tun ]] && [[ -S "$TS_SOCKET" ]]; then
    ssh_opts+=(-o "ProxyCommand=tailscale --socket=$TS_SOCKET nc %h %p")
  fi

  echo "SSH test → ${user}@${host} ..."
  ssh "${ssh_opts[@]}" \
    "${user}@${host}" \
    'echo "Hub OK: $(hostname) $(uname -a)"; command -v python3 && python3 --version; test -d proof-codex-ai && echo "repo: ~/proof-codex-ai exists" || echo "repo: not cloned yet (run git clone)"'
  echo "Hub remote access: OK"
}

join_tailscale
ssh_hub
