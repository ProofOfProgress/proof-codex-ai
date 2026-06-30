# Discord + course site intel — read-only setup

**Your preferred path:** Hub laptop stays logged into **Discord (browser tab)** + **course site**. Agent reads text — **never sends messages**.

Discord **desktop app** = for you. **discord.com in Chrome/Edge on hub** = for the agent (same account, fine per your read).

---

## Lock-in plan (3 tracks)

| Track | Primary tool | Free credits? |
|-------|--------------|---------------|
| **Bubble wrap** | Our `bubble-batch` (Gemini slides) | Uses Gemini |
| **Bubble bonus** | Course **Bubble AI Video Creator** (~10/day) | **Free on course site** |
| **Product research** | FastMoss (paid) + course **Product Research Bot** (free) | FastMoss API still wiring |

**Rule for course-tool videos:** Download → run **Module 1 QC** → only post if pass. Creator-trained ≠ auto-upload.

---

## Track A — Hub browser (Discord + course) — **do this first**

### One-time login on hub laptop (~10 min, can do between Rocket League games)

**1. Fix Tailscale** (Ubuntu on hub):

```bash
sudo tailscale --socket=/var/run/tailscale/tailscaled.sock up
```

Open the link it prints in **Windows browser** if asked. Status must show **`active`**, not **`offline`**:

```bash
tailscale --socket=/var/run/tailscale/tailscaled.sock status | head -3
```

**2. Log into Discord web** (agent reads this — not the desktop app):

```bash
cd ~/proof-codex-ai
python3 -m shorts_bot.browser.cli open discord --minutes 15 --block
```

Log in at discord.com. Leave tab on your main channels.

**3. Log into course site** — paste your dashboard URL:

```bash
python3 -m shorts_bot.browser.cli open "YOUR_COURSE_URL" --minutes 15 --block
```

**4. Optional — course site as desktop app (Windows):**

Chrome → course URL → ⋮ menu → **Install page as app…** → pin to taskbar.

**5. Add URLs to Cursor Secrets** (new agent run after):

| Secret | Example |
|--------|---------|
| `COURSE_SITE_URL` | Dashboard URL |
| `COURSE_BUBBLE_TOOL_URL` | Bubble AI video creator page |
| `DISCORD_GUILD_ID` | Server ID |
| `DISCORD_CHANNEL_IDS` | `channel1,channel2` |

### Agent sync (after login + secrets)

On hub:

```bash
bash scripts/hub_browser_intel_sync.sh
```

Writes `data/research/course/inbox/hub-browser-sync-YYYY-MM-DD.md` — Discord channel text + course pages.

---

## Track B — Discord bot (optional backup)

If browser scrape is flaky, add a **read-only bot** (never Send Messages):

```bash
python3 -m shorts_bot.integrations.discord_cli sync
```

See bot setup in section below. **Hub browser is primary; bot is optional cron backup.**

### Bot setup (optional)

1. [discord.com/developers](https://discord.com/developers/applications) → New Application → Bot
2. Permissions: **View Channels + Read Message History only**
3. `DISCORD_BOT_TOKEN` in Cursor Secrets
4. Invite bot to server

---

## Track C — FastMoss (product research — blocking gap)

**Today:** API client is a **stub** — full scout not shipped yet.

| Step | You | Agent |
|------|-----|-------|
| Subscribe | [fastmoss.com](https://www.fastmoss.com/) ~$59/mo | — |
| API keys | [developers.fastmoss.com](https://developers.fastmoss.com/) → Cursor Secrets | `scout_cli ping` |
| Until API works | Pick in FastMoss app OR use course **Product Research Bot** | Ingest via hub browser sync |

**Training loop:** Course bot output + coach calls → `GROUP_CALLS.md` → `product-researcher` agent rules.

---

## Course free tools (creator-built)

| Tool | Use |
|------|-----|
| **Bubble AI Video Creator** | ~10 free vids/day — QC before post |
| **Product Research Bot** | Research training data until FastMoss API live |
| **New growth account instructions** | Owner paste or hub sync → `GROUP_CALLS.md` |

Paste new growth instructions in chat or save to `data/research/course/inbox/` after the coach upload.

---

## What we will NOT do

- Send Discord messages (browser = read-only; bot = GET-only)
- Auto-post course-tool videos without QC
- Share repo/architecture with course creator (`GROUP_CALLS.md` IP rule)

---

## While you play — zero-focus checklist

- [ ] Windows **Tailscale** app → Connected
- [ ] Ubuntu: `tailscale up` → status **active**
- [ ] Message agent: **course URL + bubble tool URL** (no passwords)

That's it until you have a break.

---

## Related

- `data/research/course/BUBBLE_WRAP.md`
- `docs/FOR_OWNER_FASTMOSS_SETUP.md`
- `docs/FOR_OWNER_HUB_GET_AGENT_IN.md`
