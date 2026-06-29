# Get the cloud agent in without START HUB working

**Honest answer:** I **cannot** fix your laptop until **something** on your side opens the door once. There is no magic back door — but these paths are easier than a crashing button.

---

## Path 1 — FIX HUB ONCE (easiest, do this now)

1. Log into **Windows**
2. File Explorer → repo **`scripts`** folder
3. Double-click **`FIX_HUB_ONCE.bat`**

That opens **Ubuntu** with a guided script. Enter your **Ubuntu password once** if asked. Leave the window open until it says **HUB READY**.

Then tell the agent: **“try now”**

Also copies to Desktop if you run **`INSTALL_HUB_AUTOSTART.bat`** (see Path 2).

---

## Path 2 — Auto-start at login (no button after setup)

After Path 1 worked once:

1. Double-click **`INSTALL_HUB_AUTOSTART.bat`**
2. Hub starts **45 seconds after Windows login** automatically

Optional: put a **reusable Tailscale auth key** in hub `.env` so Tailscale never needs a browser after reboot:

```
HUB_LOCAL_TAILSCALE_AUTH_KEY=tskey-auth-...
```

Create key at https://login.tailscale.com/admin/settings/keys — **do not paste in chat.**

---

## Path 3 — Cursor on the laptop (no cloud SSH)

If cloud agent keeps failing:

1. Install **Cursor** on the HP (if not already)
2. Open the **`proof-codex-ai`** folder in Cursor
3. Chat with the agent **there** — it runs on your machine, no Tailscale/SSH needed

Good for fixing START HUB, running `bubble-batch`, editing files.

---

## Path 4 — Ubuntu only (copy-paste)

Open **Ubuntu** from Start menu, paste:

```bash
cd ~/proof-codex-ai
git pull
bash scripts/hub_owner_fix_once.sh
```

---

## What I still cannot do

| Cannot | Why |
|--------|-----|
| Log into Windows PIN | Microsoft lock screen |
| Type Ubuntu password from cloud | Only you at the keyboard |
| Connect while Tailscale is down | No route to your laptop |

**One successful FIX HUB ONCE** → cloud agent works until the next big break.

---

## Related

- START HUB button: `FOR_OWNER_HUB_START_BUTTON.md`
- Remote SSH: `FOR_OWNER_REMOTE_HUB_SSH.md`
