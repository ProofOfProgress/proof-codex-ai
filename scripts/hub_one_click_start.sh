#!/usr/bin/env bash
# One-click hub wake — SSH + Tailscale + desktop helper. Run from WSL on owner laptop.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TS_SOCKET="${TS_SOCKET:-/var/run/tailscale/tailscaled.sock}"

echo ""
echo "=============================================="
echo "  PROOF CODEX — HUB START"
echo "=============================================="
echo ""

step_ok() { echo "[OK] $*"; }
step_need_sudo() { echo "[!] $* — may ask for your Ubuntu password once"; }

# --- SSH (cloud agent needs this) ---
if sudo -n service ssh start 2>/dev/null; then
  step_ok "SSH running"
else
  step_need_sudo "Starting SSH"
  sudo service ssh start
  step_ok "SSH running"
fi

# --- Tailscale (cloud agent needs this) ---
if [[ -S "$TS_SOCKET" ]] && sudo -n tailscale --socket="$TS_SOCKET" status >/dev/null 2>&1; then
  step_ok "Tailscale already connected"
else
  if [[ -x "$ROOT/scripts/hub_tailscale_start.sh" ]]; then
    step_need_sudo "Starting Tailscale daemon"
    bash "$ROOT/scripts/hub_tailscale_start.sh" || true
  fi
  if sudo -n tailscale --socket="$TS_SOCKET" up 2>/dev/null; then
    step_ok "Tailscale connected"
  else
    step_need_sudo "Connecting Tailscale"
    sudo tailscale --socket="$TS_SOCKET" up
    step_ok "Tailscale connected"
  fi
fi

TS_IP=""
TS_IP="$(sudo tailscale --socket="$TS_SOCKET" ip -4 2>/dev/null || true)"
if [[ -n "$TS_IP" ]]; then
  echo "     Hub Tailscale IP: $TS_IP"
fi

# --- Desktop helper (keyboard/mouse + KeyFreeze unlock path) ---
echo ""
echo "Starting desktop helper on Windows..."
if bash "$ROOT/scripts/desktop_helper_ensure.sh"; then
  step_ok "Desktop helper ready"
else
  echo "[!] Desktop helper did not respond — is Windows logged in?"
  echo "    Try double-click START_DESKTOP_HELPER.bat in scripts\\"
fi

echo ""
echo "=============================================="
echo "  HUB READY — cloud agent can connect"
echo "=============================================="
echo ""
echo "Slides folder:  $ROOT/data/bubble_wrap/slides/"
echo "Agent verify:   python3 -m shorts_bot.hub_remote verify"
echo ""
