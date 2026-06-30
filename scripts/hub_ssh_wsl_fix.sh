#!/usr/bin/env bash
# WSL hub: fix sshd so Tailscale SSH works (listen on all interfaces).
set -euo pipefail

echo "=== Hub SSH fix (WSL) ==="

sudo apt-get install -y -qq openssh-server 2>/dev/null || true

CFG="/etc/ssh/sshd_config"
if grep -q '^ListenAddress' "$CFG" 2>/dev/null; then
  sudo sed -i 's/^ListenAddress.*/ListenAddress 0.0.0.0/' "$CFG"
else
  echo 'ListenAddress 0.0.0.0' | sudo tee -a "$CFG" >/dev/null
fi

sudo service ssh stop 2>/dev/null || true
sleep 1
sudo service ssh start
sleep 2

echo ""
echo "--- ssh status ---"
sudo service ssh status | head -5 || true
echo ""
echo "--- port 22 ---"
ss -ltn | grep ':22' || echo "WARNING: nothing listening on 22"
echo ""
echo "--- tailscale ip ---"
tailscale --socket=/var/run/tailscale/tailscaled.sock ip -4 2>/dev/null || echo "(tailscale not up)"
echo ""
echo "If port 22 shows LISTEN and tailscale has an IP, tell agent: try now"
echo "Then run: cd ~/proof-codex-ai && bash scripts/hub_one_click_start.sh"
