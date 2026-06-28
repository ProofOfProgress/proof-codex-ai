# Mini PC install — plain English

**What you’re installing:** this repo (`proof-codex-ai`) on the small computer that sits next to the phones.

**What’s NOT ready yet:** the **phone hub worker** (program that auto-taps Mackenzie on each phone). That gets built after your hardware arrives. Today you can still install the base bot + verify phones with ADB.

---

## What runs where

| Machine | Installs repo? | Does what |
|---------|----------------|-----------|
| **Cursor cloud agent** | Already has repo | Affiliate pipeline, scout, Kling, Zernio MP4 posts |
| **Your mini PC** | **Yes — this doc** | Controls phones (when worker is built); runs overnight jobs |
| **Your laptop** | Optional | Remote in via Tailscale to watch mini PC |

---

## Mini PC — before you start

- **OS:** Linux (Ubuntu 22.04+ recommended) or Windows 11 + WSL2 Ubuntu  
- **Hardware:** **Old laptop is fine** — wipe and reuse (saves buying a mini PC). Needs USB ports or a hub for 4 phones.  
- **Network:** Wi‑Fi or ethernet; add **Tailscale** later so you can remote in  
- **USB:** powered hub for 4–5 phones  
- **Accounts:** GitHub access to clone the repo (or copy files from a zip)

---

## Have your PIN? Skip the wipe

If the laptop **turns on and you can log in**, do **not** wipe it. Use the machine as-is.

| OS you see after login | What to do |
|------------------------|------------|
| **Windows 10/11** | Install **WSL2 + Ubuntu** (Step 0 below), then Steps 1–4 inside Ubuntu |
| **Already Linux** | Skip Step 0 — go straight to Step 1 |

You only wipe if login is broken and recovery is the only option (see bottom of doc).

---

## Step 0 — Windows only: add Ubuntu (WSL2)

On the laptop (Windows):

1. Open **PowerShell as Administrator**
2. Run: `wsl --install -d Ubuntu-22.04`
3. Restart if prompted
4. Open **Ubuntu** from Start menu — create a Linux username/password
5. All commands below run **inside that Ubuntu window**

Install Linux tools once:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git adb
```

**USB note:** phones plug into the **Windows** USB ports; WSL2 sees them after `adb` is set up — if `adb devices` is empty, ask the agent (usbipd on Windows helps).

---

## Step 1 — Get the repo

```bash
git clone https://github.com/ProofOfProgress/proof-codex-ai.git
cd proof-codex-ai
```

(If the repo is private, log into GitHub on the mini PC first, or copy the folder from a USB stick.)

---

## Step 2 — Install the bot (one command)

```bash
bash scripts/install.sh
```

That installs Python packages, creates `.env`, syncs secrets if they’re in the environment, and runs tests.

**First time on a fresh PC** you may need:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git adb
```

---

## Step 3 — Add secrets on the mini PC

The mini PC needs at least:

| Secret / `.env` key | Why on mini PC |
|-------------------|----------------|
| `ZERNIO_API_TOKEN` | Send bubble inbox drafts (when built) |
| *(optional)* `GEMINI_API_KEY` | If worker runs QC locally |

**Affiliate keys** (EchoTik, Kling) can stay on **cloud agent only** — affiliate posting doesn’t require the mini PC.

**Easiest:** create `.env` by hand on the mini PC:

```bash
nano .env
```

Paste (with real values):

```
ZERNIO_API_TOKEN=your_key_here
ECHOTIK_USERNAME=...
ECHOTIK_PASSWORD=...
```

Or copy `.env` from a machine where `bash scripts/install.sh` already ran.

Check:

```bash
python3 -m shorts_bot.zernio.auth_cli
python3 -m shorts_bot.tiktok_shop status
```

---

## Step 4 — Android phones + ADB

On **each phone:**

1. Enable **Developer options** → **USB debugging**  
2. Plug into hub → mini PC  
3. Accept “Allow USB debugging” on the phone screen  

On mini PC:

```bash
adb devices
```

You should see one line per phone (e.g. `ABC123    device`).

**Label which serial is which slot** — stick a note: phone_1 = gspgsgsorip1, etc. We’ll map serial → `phone_hub_slot` in config when the worker is built.

Linux udev (so you don’t need `sudo adb` every time): see Android developer docs for `udev` rules, or ask the agent when hardware is in hand.

---

## Step 5 — Remote access *(optional: let cloud agent run commands)*

**Full guide:** `docs/FOR_OWNER_REMOTE_HUB_SSH.md`

Quick version — inside **Ubuntu on the HP**, after WSL is installed:

```bash
bash scripts/hub_remote_setup.sh
```

Add printed secrets to **Cursor → Cloud Agent → Secrets**, start a **new agent run**, then ask the agent to run `bash scripts/hub_remote_verify.sh`.

**Tailscale only (you remote in, no agent SSH):** install Tailscale on Windows from https://tailscale.com

---

## Step 6 — Phone hub worker *(not installed yet)*

When we build it, install will look like:

```bash
# future — not available today
python3 -m shorts_bot.phone_hub.worker
# or a systemd service that starts on boot
```

Until then, bubble posts still need **manual** Mackenzie on the right phone after Zernio inbox draft (or we build the worker first).

---

## Cloud agent (me) — already installed

On Cursor cloud runs, bootstrap is:

```bash
bash scripts/install.sh
python3 -m shorts_bot.cloud_secrets
python3 -m shorts_bot.tiktok_shop status
```

Secrets go in **Cursor → Cloud Agent → Secrets**, then **start a new agent run**.

---

## Quick health check (any machine)

```bash
bash scripts/install.sh          # or skip if already done
python3 -m shorts_bot.tiktok_shop status
python3 -m shorts_bot.zernio.auth_cli
python3 -m pytest tests/ -q
```

---

## Order for your launch

```
1. Buy mini PC + phones + SIMs + affiliate account
2. Mini PC: clone repo → bash scripts/install.sh → secrets → adb devices
3. Log one TikTok per phone; connect accounts in Zernio
4. Tailscale so you can remote in
5. We build + install phone hub worker
6. Turn on paid stack → first posts
```

Questions: `docs/LAUNCH_CHECKLIST.md` · `docs/FOR_OWNER_PHONE_HUB.md`

---

## Wipe only if you cannot log in

**Unknown password / locked out?**

1. Try **F11** at boot → HP Recovery → reset without keeping files  
2. Or **Ubuntu USB** → Install → **Erase disk**  
3. Boot menu on many HPs: **Esc** then **F9** to pick USB  

If you **have the PIN and can log in**, skip this section entirely.
