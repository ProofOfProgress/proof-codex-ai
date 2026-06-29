#!/usr/bin/env bash
# Start Tailscale on WSL (userspace networking — no systemd required).
set -euo pipefail

TS_STATE="${TS_STATE:-/var/lib/tailscale/tailscaled.state}"
TS_SOCKET="${TS_SOCKET:-/var/run/tailscale/tailscaled.sock}"
TS_LOG="${TS_LOG:-/tmp/tailscaled.log}"

sudo pkill tailscaled 2>/dev/null || true
sudo mkdir -p /var/run/tailscale /var/lib/tailscale

echo "Starting tailscaled (WSL userspace mode)..."
sudo tailscaled \
  --tun=userspace-networking \
  --state="$TS_STATE" \
  --socket="$TS_SOCKET" \
  >>"$TS_LOG" 2>&1 &

for _ in $(seq 1 20); do
  if [[ -S "$TS_SOCKET" ]]; then
    echo "tailscaled OK — socket at $TS_SOCKET"
    echo "Log: $TS_LOG"
    echo ""
    echo "Next:"
    echo "  sudo tailscale --socket=$TS_SOCKET up"
    echo "  # or: sudo tailscale --socket=$TS_SOCKET up --auth-key=tskey-auth-..."
    exit 0
  fi
  sleep 1
done

echo "ERROR: tailscaled did not create $TS_SOCKET"
echo "Last log lines:"
tail -20 "$TS_LOG" 2>/dev/null || true
exit 1
