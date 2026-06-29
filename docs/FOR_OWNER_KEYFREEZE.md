# KeyFreeze — block keyboard + mouse while automation runs

**What this gives:** your HP hub laptop stays on and the cloud agent can still run phone automation — but **you** cannot accidentally bump the keyboard or mouse while it works.

KeyFreeze is a **free Windows app** (small standalone `.exe`). It does **not** sleep the PC or lock the Windows session — only physical keyboard and mouse input.

---

## Download (one time)

1. Search **KeyFreeze** (Jitbit / BlueLife KeyFreeze) — official site: https://www.keyfreeze.com/
2. Extract the zip somewhere permanent, e.g. `C:\Tools\KeyFreeze\KeyFreeze.exe`
3. Optional: add KeyFreeze to **Windows Startup** so it sits in the system tray (padlock icon)

---

## Set your private unlock hotkey (recommended)

Default is **Ctrl+Alt+F**. To change it:

1. Run KeyFreeze once → right-click the **padlock** in the system tray → **Options**
2. Pick a combo **only you know** — do not paste it in chat
3. Write the same combo in `helper.env` (see below)

**Failsafe:** **Ctrl+Alt+Del** still breaks out if you ever get stuck.

---

## Tell the agent where KeyFreeze lives

On the hub, edit `data/desktop_hub/helper.env` (same file as the desktop helper token):

```
DESKTOP_HELPER_TOKEN=your-token-no-spaces
KEYFREEZE_EXE=C:\Tools\KeyFreeze\KeyFreeze.exe
KEYFREEZE_HOTKEY=ctrl+alt+f
```

| Key | Required | Notes |
|-----|----------|-------|
| `KEYFREEZE_EXE` | Yes | Full Windows path to the `.exe` |
| `KEYFREEZE_HOTKEY` | Yes | Same combo as KeyFreeze Options — use `+` between keys |
| `KEYFREEZE_COUNTDOWN_SECONDS` | No | Default `6` — wait after launch before input locks |

**Do not paste your custom hotkey in Cursor chat.** Keep it in `helper.env` on the hub only.

Optional: add `KEYFREEZE_HOTKEY` to **Cursor → Cloud Agent → Secrets** if the agent must unlock from the cloud VM without SSH (same value as `helper.env`).

---

## Prerequisites

- **Desktop helper running** — see `FOR_OWNER_DESKTOP_HELPER.md`
- **Hub SSH** working — see `FOR_OWNER_REMOTE_HUB_SSH.md`

The agent sends the unlock hotkey through the desktop helper (synthetic keyboard). That still works while KeyFreeze blocks your physical keyboard.

---

## What the agent runs

From the cloud (or you, in Ubuntu on the hub):

```bash
# Lock keyboard + mouse (launch KeyFreeze or send lock hotkey)
python3 -m shorts_bot.desktop_hub.cli keyfreeze lock --via-hub

# Unlock when you need the laptop back
python3 -m shorts_bot.desktop_hub.cli keyfreeze unlock --via-hub

# Check process + last known lock state
python3 -m shorts_bot.desktop_hub.cli keyfreeze status --via-hub
```

On the hub directly (Ubuntu):

```bash
cd ~/proof-codex-ai
python3 -m shorts_bot.desktop_hub.cli keyfreeze lock
python3 -m shorts_bot.desktop_hub.cli keyfreeze unlock
```

---

## Typical use

| When | Action |
|------|--------|
| Phones plugged in, agent posting all day | Agent runs **lock** before a batch |
| You need to use the laptop | Say **unlock** or press your private hotkey yourself |
| After reboot | Open Ubuntu once, start desktop helper, KeyFreeze optional in Startup |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `KEYFREEZE_EXE not set` | Add path to `helper.env` |
| Lock works, unlock fails | Desktop helper down — run `START_DESKTOP_HELPER.bat` |
| Agent unlocks but you wanted lock | Hotkey is a toggle — run `keyfreeze status`; use `--force` only if needed |
| Stuck | **Ctrl+Alt+Del** on the physical keyboard |

---

## Related

- Desktop helper: `FOR_OWNER_DESKTOP_HELPER.md`
- Remote hub SSH: `FOR_OWNER_REMOTE_HUB_SSH.md`
- Phone automation: `FOR_OWNER_PHONE_HUB.md`
