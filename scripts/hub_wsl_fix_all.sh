#!/usr/bin/env bash
# WSL hub hardening — sshd listen + keep services up. Safe to run repeatedly.
set -uo pipefail

QUIET=0
[[ "${1:-}" == "--quiet" || "${1:-}" == "-q" ]] && QUIET=1

log() { [[ "$QUIET" == 1 ]] || echo "$*"; }
warn() { echo "[!] $*" >&2; }

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TS_SOCKET="${TS_SOCKET:-/var/run/tailscale/tailscaled.sock}"

try_sudo() {
  if sudo -n "$@" 2>/dev/null; then
    return 0
  fi
  sudo "$@" 2>/dev/null
}

log "=== Hub WSL fix ==="

try_sudo apt-get install -y -qq openssh-server 2>/dev/null || true

CFG="/etc/ssh/sshd_config"
if grep -q '^ListenAddress' "$CFG" 2>/dev/null; then
  try_sudo sed -i 's/^ListenAddress.*/ListenAddress 0.0.0.0/' "$CFG"
else
  echo 'ListenAddress 0.0.0.0' | try_sudo tee -a "$CFG" >/dev/null
fi

try_sudo service ssh stop 2>/dev/null || true
sleep 1
try_sudo service ssh start 2>/dev/null || try_sudo systemctl start ssh 2>/dev/null || true
sleep 2

if ss -ltn 2>/dev/null | grep -q ':22 '; then
  log "[OK] sshd listening on 0.0.0.0:22"
else
  warn "sshd NOT listening on port 22"
fi

# WSL tailscale (backup path — Windows gateway is preferred after INSTALL_HUB_GATEWAY)
if [[ -x "$ROOT/scripts/hub_tailscale_start.sh" ]]; then
  bash "$ROOT/scripts/hub_tailscale_start.sh" >/dev/null 2>&1 || true
fi
if command -v tailscale >/dev/null 2>&1; then
  if [[ -f "$ROOT/.env" ]]; then
    # shellcheck disable=SC1091
    source "$ROOT/.env" 2>/dev/null || true
  fi
  TS_AUTH="${HUB_LOCAL_TAILSCALE_AUTH_KEY:-${TAILSCALE_AUTH_KEY:-}}"
  if try_sudo tailscale --socket="$TS_SOCKET" status >/dev/null 2>&1; then
    log "[OK] WSL Tailscale up"
  elif [[ -n "$TS_AUTH" ]]; then
    try_sudo tailscale --socket="$TS_SOCKET" up --auth-key="$TS_AUTH" >/dev/null 2>&1 \
      && log "[OK] WSL Tailscale up (auth key)" \
      || warn "WSL Tailscale up failed"
  else
    warn "WSL Tailscale down — use Windows Tailscale after gateway install"
  fi
fi

log "=== done ==="
