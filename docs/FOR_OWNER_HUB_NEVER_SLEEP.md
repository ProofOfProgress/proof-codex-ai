# Hub laptop — never sleep, never hibernate (agent must stay reachable)
#
# Run once as Administrator on the HP hub (Windows):
#   scripts\INSTALL_HUB_NEVER_SLEEP.bat
#
# Keeps the machine awake on AC power. Pair with INSTALL_HUB_AUTOSTART.bat.
# Laptop should stay **plugged in** 24/7.

## What it does

- **Sleep:** OFF on AC (and battery)
- **Hibernate:** OFF
- **Monitor:** stays on on AC (hub can run headless — plug in power)
- **Fast Startup:** OFF (fewer WSL/Tailscale surprises after “shutdown”)
- **Scheduled task:** re-runs **START HUB** when you **unlock** Windows (after lock screen)

## What it does NOT do

- Cannot stop **manual lock** (Win+L) — you still unlock once
- Cannot stop **physical power button** hold / power loss
- Cannot bypass **Windows Update forced restart** — set Active Hours

## One-time install (hub laptop)

1. Right-click **`scripts\INSTALL_HUB_NEVER_SLEEP.bat`** → **Run as administrator**
2. Also run **`INSTALL_HUB_AUTOSTART.bat`** if you have not
3. Windows **Settings → Accounts → Sign-in options** → “If you’ve been away…” → **Never** (if available)

## After install

Hub should recover after unlock without clicking START HUB. If agent still offline:

```bash
cd ~/proof-codex-ai && bash scripts/hub_one_click_start.sh
```

## Related

- `FOR_OWNER_HUB_GET_AGENT_IN.md`
- `FOR_OWNER_HUB_START_BUTTON.md`
