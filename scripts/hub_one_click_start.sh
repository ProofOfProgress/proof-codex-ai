#!/usr/bin/env bash
# One-click hub wake — SSH + Tailscale + desktop helper. Run from WSL on owner laptop.
# Tolerant of partial failures — prints a clear summary instead of vanishing.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env" 2>/dev/null || true
  set +a
fi

TS_SOCKET="${TS_SOCKET:-/var/run/tailscale/tailscaled.sock}"
LOG_FILE="$ROOT/data/desktop_hub/hub_start.log"
mkdir -p "$(dirname "$LOG_FILE")"

SSH_OK=0
TS_OK=0
HELPER_OK=0

log() {
  echo "$*" | tee -a "$LOG_FILE"
}

step_ok() { log "[OK] $*"; }
step_warn() { log "[!] $*"; }
step_fail() { log "[FAIL] $*"; }

log ""
log "=============================================="
log "  PROOF CODEX — HUB START $(date -Iseconds 2>/dev/null || date)"
log "=============================================="
log ""

try_sudo() {
  # Run sudo; return 0 on success. Never abort the whole script.
  if sudo -n "$@" 2>/dev/null; then
    return 0
  fi
  step_warn "Need Ubuntu password for: sudo $*"
  if sudo "$@"; then
    return 0
  fi
  return 1
}

ssh_listening() {
  ss -ltn 2>/dev/null | grep -q ':22 ' || netstat -ltn 2>/dev/null | grep -q ':22 '
}

hub_tailscale_ip() {
  sudo -n tailscale --socket="$TS_SOCKET" ip -4 2>/dev/null \
    || tailscale --socket="$TS_SOCKET" ip -4 2>/dev/null \
    || true
}

tailscale_connected() {
  [[ -n "$(hub_tailscale_ip)" ]] && return 0
  sudo -n tailscale --socket="$TS_SOCKET" status >/dev/null 2>&1 && return 0
  tailscale --socket="$TS_SOCKET" status >/dev/null 2>&1 && return 0
  return 1
}

# --- SSH (cloud agent needs this) ---
if ssh_listening; then
  step_ok "SSH already listening on port 22"
  SSH_OK=1
elif try_sudo service ssh start; then
  step_ok "SSH running"
  SSH_OK=1
else
  step_fail "SSH did not start — open Ubuntu and run: sudo service ssh start"
fi

# --- Tailscale daemon + login ---
if tailscale_connected; then
  step_ok "Tailscale already connected"
  TS_OK=1
else
  if [[ -x "$ROOT/scripts/hub_tailscale_start.sh" ]]; then
    step_warn "Starting Tailscale daemon (may take ~20 seconds)..."
    if bash "$ROOT/scripts/hub_tailscale_start.sh" >>"$LOG_FILE" 2>&1; then
      step_ok "Tailscale daemon running"
    else
      step_warn "Tailscale daemon slow — continuing anyway (see $LOG_FILE)"
      tail -5 "$LOG_FILE" 2>/dev/null || true
    fi
  fi
  if try_sudo tailscale --socket="$TS_SOCKET" up; then
    step_ok "Tailscale connected"
    TS_OK=1
  else
    TS_AUTH="${HUB_LOCAL_TAILSCALE_AUTH_KEY:-${TAILSCALE_AUTH_KEY:-}}"
    if [[ -n "$TS_AUTH" ]]; then
      step_warn "Trying Tailscale with auth key from .env (no browser)..."
      if try_sudo tailscale --socket="$TS_SOCKET" up --auth-key="$TS_AUTH"; then
        step_ok "Tailscale connected (auth key)"
        TS_OK=1
      fi
    fi
  fi
  if [[ "$TS_OK" != 1 ]]; then
    step_fail "Tailscale up failed — open Ubuntu and run:"
    log "  sudo tailscale --socket=$TS_SOCKET up"
    log "  Or add HUB_LOCAL_TAILSCALE_AUTH_KEY to .env (reusable key from tailscale.com)"
    if [[ -f /tmp/tailscaled.log ]]; then
      log "  tailscale log: /tmp/tailscaled.log"
      tail -8 /tmp/tailscaled.log 2>/dev/null | tee -a "$LOG_FILE" || true
    fi
  fi
fi

TS_IP=""
TS_IP="$(hub_tailscale_ip)"
if [[ -n "$TS_IP" ]]; then
  log "     Hub Tailscale IP: $TS_IP"
  TS_OK=1
fi

# --- Desktop helper (keyboard/mouse + KeyFreeze unlock path) ---
log ""
log "Starting desktop helper on Windows..."
if bash "$ROOT/scripts/desktop_helper_ensure.sh" >>"$LOG_FILE" 2>&1; then
  step_ok "Desktop helper ready"
  HELPER_OK=1
else
  step_warn "Desktop helper did not respond — try scripts\\START_DESKTOP_HELPER.bat"
fi

log ""
log "=============================================="
if [[ "$SSH_OK" == 1 && "$TS_OK" == 1 ]]; then
  log "  HUB READY — cloud agent can connect"
  if ! sudo -n true 2>/dev/null; then
    log "  TIP: run FIX HUB ONCE once — then reboot starts won't ask password"
  fi
elif [[ "$SSH_OK" == 1 ]]; then
  log "  PARTIAL — SSH OK, Tailscale still needs fix (see above)"
else
  log "  NOT READY — open Ubuntu, run this script there, enter password if asked"
fi
log "=============================================="
log ""
log "Full log: $LOG_FILE"
log ""

if [[ "$SSH_OK" == 1 && "$TS_OK" == 1 ]]; then
  exit 0
fi
exit 1
