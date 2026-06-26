# New cloud agent — start here

Every **new Cursor Cloud Agent chat** should run this checklist first. Secrets injected at **agent start** — if the owner adds a secret mid-chat, **start a new agent run** or the VM won't see it.

---

## 1. Read context (60 seconds)

| Order | File | Why |
|-------|------|-----|
| 1 | `AGENTS.md` | What we work on, what's dead, commands |
| 2 | `data/research/course/KNOWLEDGE.md` | Course = creative (~90%), repo = automation |
| 3 | `data/PRIORITIES.md` | Top 4 build order |

**Current phase:** **Bubble wrap only** until ~1k followers per account → `data/research/course/BUBBLE_WRAP.md`

**Dead (never suggest):** Fix It Fast, Rapid Tool Review, Ms. Byte, InVideo, Peripheral horror.

---

## 2. Bootstrap the VM (first command)

```bash
bash scripts/install.sh
python3 -m shorts_bot.cloud_secrets
```

**Interpret `cloud_secrets`:**

| Column | Meaning |
|--------|---------|
| **In agent list** | Owner added secret to **Cloud Agent → Secrets** |
| **Injected** | Cursor marked it for this run |
| **On VM** | Actually in environment now |

If a secret is **In agent list: yes** but **On VM: —** → owner must **start a new cloud agent run**.

If secret is **missing** from the table entirely → wrong panel (IDE Settings vs Cloud Agent) or typo in name.

---

## 3. Secrets that matter right now

Add in **Cursor → Cloud Agent → Secrets** (exact names):

| Secret | Purpose |
|--------|---------|
| `GEMINI_API_KEY` | Scripts, QC, image help |
| `ZERNIO_API_TOKEN` | **TikTok posting** (owner uses this name — also accepts `ZERNIO_API_KEY`) |
| `KLING_API_KEY` | Kling video — **affiliate phase only** (after ~1k followers) |
| `ECHOTIK_USERNAME` + `ECHOTIK_PASSWORD` | Product scout — **affiliate phase only** (not needed for bubble wrap) |

Full list: `docs/CURSOR_SECRETS.md`

After adding/changing secrets → **new agent run** → run `bash scripts/install.sh` again.

---

## 4. Verify services

```bash
python3 -m shorts_bot.zernio.auth_cli --json    # TikTok accounts on Zernio
python3 -m shorts_bot.tiktok_shop status        # Posting quotas / queue
python3 -m pytest tests/ -q                     # Smoke tests
```

**Zernio accounts:** should return `"configured": true` and a list of profiles. If `"configured": false` → see step 2.

---

## 5. Bubble wrap workflow (current focus)

| Step | Doc |
|------|-----|
| Format | `BUBBLE_WRAP.md` — **2-photo manual-swipe slideshow** + Mackenzie sound |
| Samples | Owner Drive + `BUBBLE_WRAP_SAMPLES.md` |
| Posting | **Zernio** — `docs/FOR_OWNER_BUBBLE_WRAP_OPS.md` |
| Sound | API can't pick Mackenzie auto — add sound in TikTok app after upload |
| Test uploads | **Always `--private`** via Zernio — draft inbox often doesn't show |

**Do not** export auto-playing MP4 slideshows for bubble wrap — use **photo carousel**.

---

## 6. Owner communication

- Plain English, one step at a time — owner is not a developer.
- Creative rules → **course only** (`data/research/course/`).
- Group-call updates → log in `GROUP_CALLS.md`.

---

## 7. Git / PRs (cloud agents)

- Branch prefix: `cursor/<name>-4484` (or current suffix)
- Run tests before merge
- Merge own PRs when `MERGEABLE` + `CLEAN`

---

## Quick troubleshooting

| Problem | Fix |
|---------|-----|
| "No ZERNIO_API_KEY" but owner says it's set | Secret name must be `ZERNIO_API_TOKEN` or `ZERNIO_API_KEY` in **Cloud Agent** secrets + **new run** |
| Agent talks about horror / Ms. Byte / Fix It Fast | Read `AGENTS.md` — dead lanes |
| Agent invents hooks | Read `data/research/course/` — not config defaults |
| Can't list Zernio profiles | `bash scripts/install.sh` then `python3 -m shorts_bot.zernio.auth_cli --json` |
