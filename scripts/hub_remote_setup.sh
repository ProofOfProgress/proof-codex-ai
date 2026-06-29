#!/usr/bin/env bash
# One-time WSL hub setup: SSH + Tailscale + agent key.
# Run inside Ubuntu on the Windows 11 HP laptop.
set -euo pipefail

echo "=== Hub remote setup (WSL) ==="

if ! grep -qi microsoft /proc/version 2>/dev/null; then
  echo "Note: this script targets WSL on Windows. Continuing anyway..."
fi

export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
sudo apt-get install -y -qq openssh-server curl ca-certificates

# SSH
sudo service ssh start || sudo systemctl start ssh || true
sudo service ssh enable 2>/dev/null || true

AGENT_KEY="$HOME/.ssh/cursor_agent_ed25519"
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

if [[ ! -f "$AGENT_KEY" ]]; then
  ssh-keygen -t ed25519 -f "$AGENT_KEY" -N "" -C "cursor-cloud-agent"
fi
chmod 600 "$AGENT_KEY"
touch "$HOME/.ssh/authorized_keys"
grep -qF "$(cat "${AGENT_KEY}.pub")" "$HOME/.ssh/authorized_keys" 2>/dev/null \
  || cat "${AGENT_KEY}.pub" >> "$HOME/.ssh/authorized_keys"
chmod 600 "$HOME/.ssh/authorized_keys"

# Tailscale
if ! command -v tailscale >/dev/null 2>&1; then
  curl -fsSL https://tailscale.com/install.sh | sh
fi

TS_SOCKET="/var/run/tailscale/tailscaled.sock"
IS_WSL=false
if grep -qi microsoft /proc/version 2>/dev/null; then
  IS_WSL=true
fi

echo ""
echo "=== Tailscale login (required once) ==="
if [[ "$IS_WSL" == true ]]; then
  echo "WSL detected — starting Tailscale in userspace mode (no systemd)."
  bash "$(dirname "$0")/hub_tailscale_start.sh"
  echo ""
  echo "Run ONE of:"
  echo "  sudo tailscale --socket=$TS_SOCKET up"
  echo "  sudo tailscale --socket=$TS_SOCKET up --auth-key=tskey-auth-XXXX"
else
  echo "Run ONE of:"
  echo "  sudo tailscale up"
  echo "  sudo tailscale up --auth-key=tskey-auth-XXXX"
fi
echo ""
read -r -p "Press Enter after tailscale up succeeded..."

TS_IP=""
if command -v tailscale >/dev/null 2>&1; then
  if [[ "$IS_WSL" == true ]]; then
    TS_IP="$(sudo tailscale --socket="$TS_SOCKET" ip -4 2>/dev/null || true)"
  else
    TS_IP="$(tailscale ip -4 2>/dev/null || true)"
  fi
fi
USER_NAME="$(whoami)"

echo ""
echo "=============================================="
echo "ADD THESE TO CURSOR → CLOUD AGENT → SECRETS"
echo "(Then start a NEW agent run. Do NOT paste in chat.)"
echo "=============================================="
echo ""
echo "TAILSCALE_AUTH_KEY = reusable key from tailscale.com/admin/settings/keys"
echo "                     (so the cloud VM can join YOUR tailnet)"
echo ""
echo "HUB_SSH_HOST = ${TS_IP:-100.x.x.x}   # or: tailscale ip -4"
echo "HUB_SSH_USER = ${USER_NAME}"
echo ""
echo "HUB_SSH_PRIVATE_KEY = paste entire block below:"
echo "-----BEGIN OPENSSH PRIVATE KEY-----"
cat "$AGENT_KEY"
echo "-----END OPENSSH PRIVATE KEY-----"
echo ""
echo "=============================================="
echo "Then tell the agent: Connect to hub — run hub_remote_verify.sh"
echo "=============================================="
