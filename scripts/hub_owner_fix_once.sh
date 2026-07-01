#!/usr/bin/env bash
# Owner runs once in Ubuntu when START HUB keeps crashing — leaves window open.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo ""
echo "=============================================="
echo "  PROOF CODEX — FIX HUB (one time)"
echo "=============================================="
echo ""
echo "This will:"
echo "  1. git pull (latest fixes)"
echo "  2. Allow START HUB without password every reboot (sudo setup)"
echo "  3. Start SSH + Tailscale + desktop helper"
if [[ "${HUB_FIX_AUTO:-}" == "1" ]]; then
  echo "(auto mode — skipping Enter prompt)"
else
  echo ""
  read -r -p "Press Enter to continue..."
fi

if git pull origin main 2>/dev/null || git pull 2>/dev/null; then
  echo "[OK] git pull"
else
  echo "[!] git pull skipped — continuing anyway"
fi

if [[ -x "$ROOT/scripts/hub_one_click_sudo_setup.sh" ]]; then
  echo ""
  echo "--- Passwordless sudo (enter Ubuntu password ONCE) ---"
  bash "$ROOT/scripts/hub_one_click_sudo_setup.sh" || echo "[!] sudo setup skipped"
fi

if [[ -f "$ROOT/.env" ]] && grep -q HUB_LOCAL_TAILSCALE_AUTH_KEY "$ROOT/.env" 2>/dev/null; then
  echo "[OK] HUB_LOCAL_TAILSCALE_AUTH_KEY found in .env"
else
  echo ""
  echo "OPTIONAL (recommended): silent Tailscale after reboot"
  echo "  1. tailscale.com/admin/settings/keys → create reusable auth key"
  echo "  2. Add to $ROOT/.env :"
  echo "     HUB_LOCAL_TAILSCALE_AUTH_KEY=tskey-auth-..."
  echo "  (Do not paste the key in chat.)"
  echo ""
fi

if [[ -x "$ROOT/scripts/hub_wsl_fix_all.sh" ]]; then
  bash "$ROOT/scripts/hub_wsl_fix_all.sh"
fi

bash "$ROOT/scripts/hub_one_click_start.sh"
echo ""
if [[ "${HUB_FIX_AUTO:-}" != "1" ]]; then
  read -r -p "Done. Press Enter to close this window..."
fi
