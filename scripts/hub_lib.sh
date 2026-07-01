#!/usr/bin/env bash
# Shared hub remote helpers — Tailscale join + SSH to owner WSL hub.
# Source from hub_connect.sh / hub_remote_verify.sh — do not run directly.

hub_lib_init() {
  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  cd "$ROOT"

  TS_SOCKET="${TS_SOCKET:-/var/run/tailscale/tailscaled.sock}"
  TS_STATE="${TS_STATE:-/var/lib/tailscale/tailscaled.state}"
  TS_SOCKS="${TS_SOCKS:-127.0.0.1:1055}"
  HUB_QUIET="${HUB_QUIET:-0}"

  if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env 2>/dev/null || true
    set +a
  fi

  # Cursor secret typo: TALESCALE_AUTH_KEY (missing "I").
  TAILSCALE_AUTH_KEY="${TAILSCALE_AUTH_KEY:-${TALESCALE_AUTH_KEY:-}}"
}

hub_log() {
  [[ "$HUB_QUIET" == 1 ]] && return 0
  echo "$@"
}

hub_secrets_configured() {
  [[ -n "${HUB_SSH_HOST:-}" && -n "${HUB_SSH_USER:-}" && -n "${HUB_SSH_PRIVATE_KEY:-}" ]]
}

hub_tailscale_cli() {
  tailscale --socket="$TS_SOCKET" "$@"
}

hub_normalize_openssh_key() {
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

hub_start_tailscaled() {
  if [[ -S "$TS_SOCKET" ]] && hub_tailscale_cli status >/dev/null 2>&1; then
    return 0
  fi

  sudo mkdir -p /var/run/tailscale /var/lib/tailscale
  sudo pkill tailscaled 2>/dev/null || true
  sleep 1

  local tun_mode="tailscale0"
  if [[ ! -e /dev/net/tun ]]; then
    hub_log "No /dev/net/tun — using Tailscale userspace-networking (cloud VM)"
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
  hub_log "ERROR: tailscaled did not start (no socket at $TS_SOCKET)"
  return 1
}

hub_join_tailscale() {
  if [[ -z "${TAILSCALE_AUTH_KEY:-}" ]]; then
    hub_log "TAILSCALE_AUTH_KEY not set — skip tailscale join (hub may still work if VM already on tailnet)"
    return 0
  fi
  if ! command -v tailscale >/dev/null 2>&1; then
    hub_log "Installing tailscale on cloud VM..."
    curl -fsSL https://tailscale.com/install.sh | sh
  fi
  if hub_tailscale_cli status >/dev/null 2>&1; then
    hub_log "Tailscale already connected: $(hub_tailscale_cli ip -4 2>/dev/null || echo unknown)"
    return 0
  fi
  hub_start_tailscaled || return 1
  sudo hub_tailscale_cli up \
    --auth-key="${TAILSCALE_AUTH_KEY}" \
    --hostname=cursor-cloud-agent \
    --accept-routes
  hub_log "Cloud VM Tailscale IP: $(hub_tailscale_cli ip -4 2>/dev/null || echo unknown)"
}

hub_prepare_ssh_key() {
  local keyfile
  keyfile="$(mktemp)"
  printf '%s\n' "$HUB_SSH_PRIVATE_KEY" > "$keyfile"
  hub_normalize_openssh_key "$keyfile"
  chmod 600 "$keyfile"
  if ! ssh-keygen -y -f "$keyfile" >/dev/null 2>&1; then
    rm -f "$keyfile"
    hub_log "ERROR: HUB_SSH_PRIVATE_KEY is invalid (check for duplicate BEGIN/END lines in Cursor Secrets)"
    return 1
  fi
  printf '%s' "$keyfile"
}

hub_ssh_port() {
  echo "${HUB_SSH_PORT:-22}"
}

hub_ssh_opts() {
  local -a ssh_opts=(
    -i "$1"
    -p "$(hub_ssh_port)"
    -o StrictHostKeyChecking=accept-new
    -o ConnectTimeout=25
    -o ServerAliveInterval=10
    -o ServerAliveCountMax=2
  )
  # Cloud VM uses userspace-networking — direct dial to 100.x works; tailscale nc breaks (%p → 65535).
  printf '%s\n' "${ssh_opts[@]}"
}

hub_ensure_connected() {
  hub_lib_init
  if ! hub_secrets_configured; then
    hub_log "Hub SSH secrets not configured — skip auto-connect"
    return 1
  fi
  hub_join_tailscale || return 1
  return 0
}

hub_run_ssh() {
  local host user keyfile
  host="${HUB_SSH_HOST:-}"
  user="${HUB_SSH_USER:-}"
  if ! hub_secrets_configured; then
    hub_log "ERROR: Set HUB_SSH_HOST, HUB_SSH_USER, and HUB_SSH_PRIVATE_KEY in Cursor Secrets"
    return 1
  fi
  keyfile="$(hub_prepare_ssh_key)" || return 1
  # shellcheck disable=SC2064
  trap "rm -f '$keyfile'" RETURN

  local -a ssh_opts
  mapfile -t ssh_opts < <(hub_ssh_opts "$keyfile")
  ssh "${ssh_opts[@]}" "${user}@${host}" "$@"
}

hub_verify_ssh() {
  hub_log "SSH test → ${HUB_SSH_USER}@${HUB_SSH_HOST}:$(hub_ssh_port) ..."
  if ! hub_run_ssh \
    'echo "Hub OK: $(hostname) $(uname -a)"; command -v python3 && python3 --version; test -d proof-codex-ai && echo "repo: ~/proof-codex-ai exists" || echo "repo: not cloned yet (run git clone)"'; then
    hub_log ""
    hub_log "Hub SSH failed. Owner fix (one double-click on HP):"
    hub_log "  scripts\\HUB_RECOVERY.bat  (or Desktop copy after git pull)"
    hub_log "One-time admin install: INSTALL_HUB_GATEWAY.bat + INSTALL_HUB_WATCHDOG.bat"
    hub_log "Then set Cursor secret HUB_SSH_PORT=2222 and Windows Tailscale IP in HUB_SSH_HOST"
    hub_log "See docs/FOR_OWNER_HUB_ALWAYS_ON.md"
    return 1
  fi
  hub_log "Hub remote access: OK"
}
