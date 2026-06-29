#!/usr/bin/env bash
# ONE-TIME (owner, inside Ubuntu): allow START HUB without typing password every reboot.
# Run: bash scripts/hub_one_click_sudo_setup.sh
# You will enter your Ubuntu password once during this setup only.
set -euo pipefail

USER_NAME="$(whoami)"
TS_SOCKET="/var/run/tailscale/tailscaled.sock"
DROP="/etc/sudoers.d/proof-codex-hub"

if [[ "$(id -u)" -ne 0 ]] && ! sudo -n true 2>/dev/null; then
  echo "This script needs sudo. You will be asked for your Ubuntu password once."
fi

sudo tee "$DROP" >/dev/null <<EOF
# Proof Codex hub one-click start — ${USER_NAME} only
${USER_NAME} ALL=(ALL) NOPASSWD: /usr/sbin/service ssh start, /usr/sbin/service ssh status, /usr/sbin/service ssh restart
${USER_NAME} ALL=(ALL) NOPASSWD: /usr/sbin/tailscaled
${USER_NAME} ALL=(ALL) NOPASSWD: /usr/bin/tailscale --socket=${TS_SOCKET} *
${USER_NAME} ALL=(ALL) NOPASSWD: /usr/bin/pkill tailscaled
EOF
sudo chmod 440 "$DROP"
sudo visudo -cf "$DROP"

echo ""
echo "OK — passwordless sudo for hub start is configured."
echo "Double-click START HUB on Desktop — should not ask for password anymore."
echo ""
