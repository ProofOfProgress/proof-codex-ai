# Desktop + phone hub control

**Two lanes on the owner hub laptop:**

| Lane | Tool | Controls |
|------|------|----------|
| **Bubble phones (4)** | ADB | Android screens — TikTok inbox, Mackenzie, publish |
| **Windows PC** | Desktop helper | Keyboard typing, mouse click, screenshots — Zernio dashboard, TikTok web, file dialogs |

Cloud agent reaches both via **SSH to WSL** (`hub_run.sh`). Phones use `adb` in WSL. PC uses a **small Windows app** you leave running while logged in.

---

## Desktop helper — one-time setup (Windows)

1. Open **PowerShell** on the hub laptop (Windows, not Ubuntu).
2. Go to the repo (clone if needed):

```powershell
cd \\wsl.localhost\Ubuntu\home\YOUR_USER\proof-codex-ai
# or a Windows clone: cd C:\Users\...\proof-codex-ai
```

3. Install Python deps:

```powershell
pip install -r scripts/desktop_helper/requirements.txt
```

4. Create a secret token (random string). Add **`DESKTOP_HELPER_TOKEN`** in **Cursor → Cloud Agent → Secrets** (same value on Windows):

```powershell
$env:DESKTOP_HELPER_TOKEN = "paste-your-token-here"
```

5. Start the helper (leave this window open while automating):

```powershell
.\scripts\desktop_helper_start.ps1
```

Windows may ask for **accessibility permission** once — allow it so the helper can type and click.

---

## What the agent can do (desktop)

From cloud or WSL:

```bash
python3 -m shorts_bot.desktop_hub.cli ping
python3 -m shorts_bot.desktop_hub.cli type "Hello Zernio"
python3 -m shorts_bot.desktop_hub.cli hotkey ctrl l
python3 -m shorts_bot.desktop_hub.cli press enter
python3 -m shorts_bot.desktop_hub.cli click 640 360
python3 -m shorts_bot.desktop_hub.cli screenshot --out data/desktop_hub/screen.png
```

**Keyboard is preferred** — typing and shortcuts, not clicking an on-screen keyboard.

**Screenshot** → agent can use vision (Gemini) to decide where to click next.

---

## What the agent can do (phones — ADB)

```bash
python3 -m shorts_bot.phone_hub.cli status
python3 -m shorts_bot.phone_hub.cli tick              # dry-run
python3 -m shorts_bot.phone_hub.cli tick --confirm    # real device steps
```

Worker steps: wake → open TikTok → find Inbox/Draft via uiautomator → Mackenzie → publish (Mackenzie/publish still need live phones).

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

After adding secrets → **start a new agent run**.

---

## Architecture

```
Cloud agent (CEO)
    │  Tailscale + SSH
    ▼
Hub laptop WSL ──► adb ──► 4 Android phones (bubble TikTok)
    │
    │  HTTP to Windows host IP :9876
    ▼
Windows desktop helper ──► keyboard + mouse + screenshot
```

---

## Related

- Phone map: `FOR_OWNER_PHONE_HUB.md`
- Remote SSH: `FOR_OWNER_REMOTE_HUB_SSH.md`
- Secrets: `docs/CURSOR_SECRETS.md`
