# Hub always-on — one guide (read this, not five others)

**Goal:** Cloud agent reaches your HP hub **without you clicking buttons every day**.  
**You only touch the laptop for:** Windows PIN after reboot · Google login · API keys · Tailscale login (once).

---

## Why it kept breaking

| Problem | Cause |
|---------|--------|
| Agent online but **SSH fails** | WSL `sshd` not listening — classic “banner timeout” |
| **Tailscale ping OK**, SSH dead | WSL Tailscale up, SSH layer broken |
| Laptop **locked** | WSL sleeps; WSL-only Tailscale flaky |
| **START HUB** did nothing | `.pyw` silent fail, or script exited before pause |

**Fix:** SSH through **Windows** (port **2222**) + **watchdog** every 3 min + **never sleep**.

---

## One-time setup (30 minutes, do once)

Do these **in order** on the **HP hub laptop**.

### A — Ubuntu (normal window, not admin)

Open **Ubuntu**, paste:

```bash
cd ~/proof-codex-ai
git pull
bash scripts/hub_owner_fix_once.sh
```

Enter Ubuntu password if asked **once**. Wait for **HUB READY**.

### B — Windows (Run as Administrator)

In repo `scripts` folder, double-click **each** (right-click → Run as administrator if needed):

1. **`INSTALL_HUB_NEVER_SLEEP.bat`** — no sleep on AC power  
2. **`INSTALL_HUB_GATEWAY.bat`** — Windows SSH → WSL on port **2222**  
3. **`INSTALL_HUB_WATCHDOG.bat`** — fixes hub every 3 min + after unlock  
4. **`INSTALL_HUB_AUTOSTART.bat`** — starts hub 45s after login  

### C — Tailscale on Windows (not just WSL)

1. Install: `winget install Tailscale.Tailscale` (or tailscale.com)  
2. Tray icon → **Log in** once  
3. Note the **Windows** Tailscale IP (e.g. `100.x.x.x`) — script prints it after gateway install  

### D — Cursor Cloud Agent secrets (then **new agent run**)

Run **`hub_print_secrets_for_cursor.ps1` on the HP hub only** — not on your main PC (`laptup`).

| Secret | Value |
|--------|--------|
| `HUB_SSH_HOST` | **HP hub** Windows Tailscale IP (machine name `desktop-ler4vhb`) — **not** `laptup` |
| `HUB_SSH_PORT` | **`2222`** |
| `HUB_SSH_USER` | Your **Windows** username on the **HP hub** (PowerShell `whoami`) |
| `HUB_SSH_PRIVATE_KEY` | Unchanged (same key from setup) |
| `TAILSCALE_AUTH_KEY` | Unchanged |

**Do not use your main laptop's Tailscale IP** — cloud agent SSH goes to the bedroom hub only.

Optional in hub `.env` (never paste in chat):

```
HUB_LOCAL_TAILSCALE_AUTH_KEY=tskey-auth-...
```

### E — Windows sign-in (stops lock pain)

**Settings → Accounts → Sign-in options**

- “If you’ve been away…” → **Never** (if available)  
- Disable **Dynamic Lock** if on  

Keep laptop **plugged in** 24/7.

### F — Desktop shortcut

After `git pull`, copy to Desktop:

- **`HUB_RECOVERY.bat`** — emergency fix when agent says offline  

---

## After every Windows reboot

1. Log in (PIN) — **only step that must be you**  
2. Wait ~1 minute (autostart + watchdog)  
3. If agent still offline → double-click **HUB RECOVERY** on Desktop  

---

## What the agent can do once this works

| Yes | No |
|-----|-----|
| Run code on hub | Type Windows PIN |
| `adb` phones on USB | Unlock lock screen for you |
| Generate bubble batches | Google login in browser (you) |
| Pull repo, QC, pipeline | Paste API keys (you, once) |

**Phone linking** = hub + USB + this SSH path. Same fix.

---

## If cloud agent still offline

1. Double-click **`HUB_RECOVERY.bat`** (green/yellow window — stays open)  
2. Tell agent: **“try hub verify”**  
3. If gateway not installed → run **INSTALL_HUB_GATEWAY.bat** as admin  

Log files:

- `data/desktop_hub/hub_start.log`  
- `data/desktop_hub/hub_watchdog.log`  

---

## Backup when SSH is dead: Cursor on the HP

1. Open **Cursor** on the hub laptop  
2. Open folder `proof-codex-ai`  
3. Chat there — no remote SSH needed  

Use this while fixing gateway — not as permanent solution.

---

## Running the business in 4 days

| Track | Needs hub SSH? |
|-------|----------------|
| Affiliate clips, QC, queue (cloud) | **No** |
| Zernio posting prep | **No** |
| **Phone cart + ADB posting** | **Yes** |
| Discord/course browser intel on hub | **Yes** |

**Do gateway setup this week** so launch isn’t blocked on phone posting.

---

## Related (detail docs)

- `FOR_OWNER_HUB_GET_AGENT_IN.md` — older paths  
- `FOR_OWNER_HUB_NEVER_SLEEP.md` — sleep settings  
- `FOR_OWNER_REMOTE_HUB_SSH.md` — SSH secrets detail  

**This file wins** if anything conflicts.
