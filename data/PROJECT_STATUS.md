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
| **Cloud → hub SSH** | **FAIL** — Tailscale ping OK but SSH banner timeout (WSL sshd) |
| **Root cause** | SSH through **WSL-only** path — breaks when WSL idles or sshd misconfigured |
| **Fix shipped (needs owner install once)** | **Windows gateway** port 2222 + watchdog + `docs/FOR_OWNER_HUB_ALWAYS_ON.md` |
| **FastMoss API scout** | Stub |
| **phone_2–5** | Not all bound; SIMs not active yet |

**Owner one-time:** `INSTALL_HUB_GATEWAY.bat` + `INSTALL_HUB_WATCHDOG.bat` + update `HUB_SSH_PORT=2222` + Windows Tailscale IP in secrets.

**Emergency:** Desktop **`HUB RECOVERY (Proof Codex).bat`**

---

## Hub vs main PC (laptup)

| Option | Verdict |
|--------|---------|
| **Hook cloud agent to main PC instead of hub** | **No** — same Tailscale/SSH/WSL problems; you don't want agent on main anyway |
| **Cursor ON hub laptop** | **Yes — backup when cloud SSH fails** — open repo in Cursor on HP, chat there |
| **Hub-only for phones + posting** | **Yes — correct design** |

---

## Easy hub start (owner — when cloud is down)

**Read first:** **`docs/FOR_OWNER_HUB_ALWAYS_ON.md`**

**Emergency:** double-click **`HUB RECOVERY (Proof Codex).bat`** on Desktop

**One-time admin fix:** `INSTALL_HUB_GATEWAY.bat` + `INSTALL_HUB_WATCHDOG.bat` + `INSTALL_HUB_NEVER_SLEEP.bat`

Then update Cursor secrets on **hub laptop output only**: `HUB_SSH_PORT=2222`, `HUB_SSH_HOST` = **desktop-ler4vhb** Windows Tailscale IP (run `hub_print_secrets_for_cursor.ps1` on hub — **not** laptup) → **new agent run**

**If SSH still fails:** Cursor on the hub laptop locally.

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
