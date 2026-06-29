# Remote hub — let the cloud agent run commands on your laptop

**What this gives:** the Cursor cloud agent can **SSH into your HP hub** and run terminal commands (`install.sh`, `adb`, etc.) — **not** mouse/screen control.

**What you still do:** log into Windows, open Ubuntu (WSL) once to run the one-time setup below.

---

## Overview

```
Cursor cloud agent  ──Tailscale──►  Your HP (WSL Ubuntu)  ──USB──►  phones (later)
                         SSH              bash commands only
```

Both machines join **your private Tailscale network** (free tier is fine). No router port-forwarding.

---

## Before you start

- [ ] Windows 11 laptop logged in  
- [ ] **Ubuntu 22.04 (WSL)** installed — see `FOR_OWNER_MINI_PC_INSTALL.md` Step 0  
- [ ] Free **Tailscale** account: https://login.tailscale.com/start  

---

## Part 1 — One-time setup on the HP *(you, inside Ubuntu/WSL)*

Open **Ubuntu** from the Start menu. Run:

```bash
cd ~
curl -fsSL -o /tmp/hub_remote_setup.sh \
  https://raw.githubusercontent.com/ProofOfProgress/proof-codex-ai/main/scripts/hub_remote_setup.sh
bash /tmp/hub_remote_setup.sh
```

If the repo is private or that URL fails, clone the repo first (Step 1 of mini PC install), then:

```bash
cd ~/proof-codex-ai
bash scripts/hub_remote_setup.sh
```

The script will:

1. Install **OpenSSH** + **Tailscale** in WSL  
2. Create an SSH key for the cloud agent  
3. Print **exactly what to paste into Cursor Secrets**  

When it asks you to run **`sudo tailscale up`**, pick one:

| Method | Command |
|--------|---------|
| **Browser login** (easiest) | `sudo tailscale up` → open the link it prints |
| **Auth key** (no browser in WSL) | Create key at https://login.tailscale.com/admin/settings/keys → `sudo tailscale up --auth-key=tskey-auth-...` |

Write down the hub’s Tailscale IP (script prints it, or run `tailscale ip -4`).

---

## Part 2 — Cursor Cloud Agent Secrets

Cursor → **Cloud Agent** → **Secrets** → add these (then **start a new agent run**):

| Secret name | What to put |
|-------------|-------------|
| `TAILSCALE_AUTH_KEY` | Reusable auth key from https://login.tailscale.com/admin/settings/keys *(lets the cloud VM join your tailnet)* |
| `HUB_SSH_HOST` | Hub Tailscale IP, e.g. `100.x.x.x` |
| `HUB_SSH_USER` | Your WSL Linux username (`whoami` in Ubuntu) |
| `HUB_SSH_PRIVATE_KEY` | **Entire** private key block the setup script printed (`-----BEGIN...-----`) |

Optional:

| Secret name | What to put |
|-------------|-------------|
| `HUB_SSH_HOSTNAME` | Tailscale name, e.g. `hp-hub` — use instead of IP if you prefer |

**Do not paste these in chat.** Rotate if exposed.

---

## Part 3 — Tell the agent to connect

Start a **new cloud agent run**. Hub access is **automatic** when secrets are set:

- `bash scripts/install.sh` joins Tailscale on bootstrap
- Any hub task: agent runs `python3 -m shorts_bot.hub_remote ensure --quiet` or `bash scripts/hub_run.sh <command>`

Manual verify anytime:

> “Connect to the hub — run `bash scripts/hub_remote_verify.sh`”

The agent will:

1. Join your Tailscale network  
2. SSH to the hub  
3. Run a test command  

If green, the agent can run install/status/adb on the HP for you.

---

## What the agent can do remotely

| Yes | No |
|-----|-----|
| `bash scripts/install.sh` | Click TikTok on phone screens *(use ADB lane)* |
| `python3 -m shorts_bot.tiktok_shop status` | Move Windows mouse *(use desktop helper)* |
| `adb devices` (when phones plugged in) | Enter your Windows PIN |
| `python3 -m shorts_bot.desktop_hub.cli type "..."` | See desktop without screenshot |
| Clone/pull repo, edit `.env` | |

---

## Keep the hub reachable

After **rebooting Windows**, log in (PIN), then double-click **START HUB (Proof Codex)** on the Desktop.

One-time install: `scripts/INSTALL_HUB_START_BUTTON.bat` — see **`docs/FOR_OWNER_HUB_START_BUTTON.md`**

Manual (same steps inside Ubuntu):

```bash
sudo service ssh start
sudo tailscale up
```

We can add auto-start later; for now that’s enough.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Agent can’t SSH | Hub: `sudo service ssh status` · `tailscale status` · laptop awake + on Wi‑Fi |
| `tailscale up` fails in WSL | Try `sudo tailscale up --accept-routes` or reinstall via setup script |
| WSL IP changed | Use **Tailscale IP** (`100.x.x.x`), not `hostname -I` |
| `adb devices` empty from agent | Phones on USB + usbipd on Windows — ask agent when phones arrive |

---

## Related

- Hub install: `FOR_OWNER_MINI_PC_INSTALL.md`  
- Phone map: `FOR_OWNER_PHONE_HUB.md`  
- Affiliate (cloud only): `LAUNCH_TODO.md`
