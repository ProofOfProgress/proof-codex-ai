# Project status snapshot — 2026-06-30

**Purpose:** Save where we are when cloud ↔ hub keeps breaking. Read this at the start of any new agent chat.

---

## North star (unchanged)

- **Affiliate revenue** — 8–10 Module-1-GOOD posts/day on purchased account
- **Week 1:** $1k commission in 7 calendar days → $500 course bonus
- **Bubble wrap** — 4 growth accounts parallel (does not block affiliate)
- **5 phones + 5 SIMs + hub laptop** — one account per phone per IP

---

## What works today

| Item | Status |
|------|--------|
| **Cloud agent (this chat / VM)** | Works — code, Gemini, coach docs, uploads in chat |
| **Repo / pipeline code** | Built — Kling, QC, bubble-batch, phone hub scripts, Discord intel (PRs open) |
| **Hub laptop when YOU use it** | Ubuntu, git, START HUB script, phone_1 ADB bound |
| **Tailscale ping hub** | Often works (`desktop-ler4vhb` 100.83.89.25) |
| **Desktop helper** | Worked when hub was up — typed into Cursor on laptop |
| **Purchased account** | Bought — **5-day warmup in progress** (GROUP_CALLS) |
| **Coach call 2026-06-30** | Recorded — **transcript not processed yet** (need file path or upload) |

---

## What is broken (blocker)

| Item | Status |
|------|--------|
| **Cloud → hub SSH** | **FAIL** — Tailscale ping OK but SSH banner timeout / reset |
| **WSL sshd + Tailscale** | Finicky — `service ssh start` shows OK but agent still can't connect |
| **Hub after sleep/lock** | Tailscale goes offline; hub unreachable until manual fix |
| **FastMoss API scout** | Stub — product research automation blocked until API wired |
| **phone_2–5** | Not all bound; SIMs not active yet |

**Root pain:** Cloud agent needs **SSH to hub WSL**. That path is unreliable. Not a “you pasted wrong window” issue — it's **WSL SSH + Tailscale + sleep**.

---

## Hub vs main PC (laptup)

| Option | Verdict |
|--------|---------|
| **Hook cloud agent to main PC instead of hub** | **No** — same Tailscale/SSH/WSL problems; you don't want agent on main anyway |
| **Cursor ON hub laptop** | **Yes — backup when cloud SSH fails** — open repo in Cursor on HP, chat there |
| **Hub-only for phones + posting** | **Yes — correct design** |

---

## Easy hub start (owner — when cloud is down)

**Do these in order on the HP:**

1. **Windows:** Tailscale tray → **Connected**
2. **Ubuntu — one block:**
   ```bash
   grep -q '^ListenAddress 0.0.0.0' /etc/ssh/sshd_config 2>/dev/null || echo 'ListenAddress 0.0.0.0' | sudo tee -a /etc/ssh/sshd_config
   sudo service ssh restart
   cd ~/proof-codex-ai && bash scripts/hub_one_click_start.sh
   ```
3. Wait for **HUB READY** → tell new agent: **“Read PROJECT_STATUS.md — try hub verify”**

**One-time (admin):** `scripts\INSTALL_HUB_NEVER_SLEEP.bat` — no sleep on AC, hub restart on unlock

**If SSH still fails:** Use **Cursor on the hub laptop** — no remote SSH required for local work.

**Next engineering fix (agent backlog):** Merge `hub_ssh_wsl_fix.sh` + harden SSH/Tailscale; consider Windows OpenSSH → WSL port forward doc.

---

## Open PRs (not all merged)

- Hub START button, QC, one-phone setup, sudo fix, Discord/course intel, never-sleep, coach transcribe

---

## Waiting on owner (no code)

- Coach call **video file** path or upload in chat
- **Course filters / product research** notes from course site
- **FastMoss** subscribe + API keys when ready
- **5 SIMs** before live posting (affiliate = phone_5 dedicated SIM)
- **Launch Date** not set

---

## Next agent priorities

1. Fix hub SSH path (or document Cursor-on-hub as primary)
2. Transcribe coach call → GROUP_CALLS + PRODUCT_RESEARCH filters
3. FastMoss scout OR course product-research bot ingest
4. Merge hub reliability PRs to main; pull on hub laptop

---

## Owner frustration note

Hub remote access has burned hours. **Work that does NOT need hub:** uploads in chat, course notes, clip QC on cloud, docs, coach transcript once file uploaded. **Work that NEEDS hub:** ADB phones, grab recording from laptop disk, browser Discord/course login sync.
