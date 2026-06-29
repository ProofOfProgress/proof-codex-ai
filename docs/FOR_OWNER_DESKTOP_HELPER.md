# Desktop + phone hub control

**Two lanes on the owner hub laptop:**

| Lane | Tool | Controls |
|------|------|----------|
| **Bubble phones (4)** | ADB | Android screens — TikTok inbox, Mackenzie, publish |
| **Windows PC** | Desktop helper | Keyboard typing, mouse click, screenshots — Zernio dashboard, TikTok web, file dialogs |

Cloud agent reaches both via **SSH to WSL** (`hub_run.sh`). Phones use `adb` in WSL. PC uses a **small Windows app** you leave running while logged in.

---

## Easy start (owner — double-click)

1. **One-time:** copy `data/desktop_hub/helper.env.example` → `data/desktop_hub/helper.env`  
   Paste the same token as **Cursor → Cloud Agent → Secrets → `DESKTOP_HELPER_TOKEN`**.

2. **One-time:** install deps (PowerShell in repo folder):

```powershell
pip install -r scripts/desktop_helper/requirements.txt
```

3. **Every time** (or after reboot): double-click:

```
scripts/START_DESKTOP_HELPER.bat
```

Helper runs **in the background** (no window to keep open). Log: `data/desktop_hub/daemon.log`

Windows may ask for **accessibility permission** once — allow it.

---

## Daily click (same time every 24 hours)

While the helper is running, it can **click one spot on screen** once per day at a fixed time (default timezone **PST**).

**Set the spot and time** (from WSL or ask the agent):

```bash
python3 -m shorts_bot.desktop_hub.cli schedule set-click \
  --hour 12 --minute 0 --x 640 --y 360 --enable --label "keep-alive"
```

**View schedule:**

```bash
python3 -m shorts_bot.desktop_hub.cli schedule show
```

Edit by hand: `data/desktop_hub/schedule.json` (see `schedule.json.example`).

Clicks are logged in `data/desktop_hub/schedule_log.jsonl`.

**Find x/y:** ask the agent to run `screenshot`, then pick coordinates from the image — or use Windows mouse position tools once.

---

## Agent can start the helper for you

From **cloud agent** (needs hub SSH secrets):

```bash
python3 -m shorts_bot.desktop_hub.cli ensure --via-hub
```

Or on **hub WSL**:

```bash
bash scripts/desktop_helper_ensure.sh
```

Requires: Windows **logged in**, WSL open at least once after reboot.

---

## What the agent can do (desktop)

```bash
python3 -m shorts_bot.desktop_hub.cli ensure --via-hub   # start if down
python3 -m shorts_bot.desktop_hub.cli ping
python3 -m shorts_bot.desktop_hub.cli type "Hello Zernio"
python3 -m shorts_bot.desktop_hub.cli hotkey ctrl l
python3 -m shorts_bot.desktop_hub.cli click 640 360
python3 -m shorts_bot.desktop_hub.cli screenshot --out data/desktop_hub/screen.png
```

**Keyboard is preferred** — typing and shortcuts, not clicking an on-screen keyboard.

---

## What the agent can do (phones — ADB)

```bash
python3 -m shorts_bot.phone_hub.cli status
python3 -m shorts_bot.phone_hub.cli tick              # dry-run
python3 -m shorts_bot.phone_hub.cli tick --confirm    # real device steps
```

---

## Unified status

```bash
python3 -m shorts_bot.hub_control.cli status
```

---

## Secrets (Cursor Cloud Agent)

| Secret | Purpose |
|--------|---------|
| `DESKTOP_HELPER_TOKEN` | Auth between agent and Windows helper |
| `DESKTOP_HELPER_HOST` | Optional — default auto-detects Windows IP from WSL |
| `DESKTOP_HELPER_PORT` | Optional — default `9876` |
| `HUB_SSH_*` + `TAILSCALE_AUTH_KEY` | SSH into hub (existing) |

After adding secrets → **start a new agent run**. Same token goes in `data/desktop_hub/helper.env` on the laptop.

---

## Architecture

```
Cloud agent (CEO)
    │  ensure --via-hub  →  SSH  →  WSL launches Windows helper
    │  Tailscale + SSH
    ▼
Hub laptop WSL ──► adb ──► 4 Android phones (bubble TikTok)
    │
    │  HTTP to Windows host IP :9876
    ▼
Windows desktop helper ──► keyboard + mouse + daily scheduled click
```

---

## Related

- Phone map: `FOR_OWNER_PHONE_HUB.md`
- Remote SSH: `FOR_OWNER_REMOTE_HUB_SSH.md`
- Secrets: `docs/CURSOR_SECRETS.md`
