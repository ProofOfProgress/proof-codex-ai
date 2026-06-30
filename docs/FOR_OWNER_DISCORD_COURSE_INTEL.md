# Discord + course site intel — read-only setup

**Goal:** Agent reads Discord + course announcements **without ever sending a message** or burning paid credits.

---

## What exists today

| Capability | Status |
|------------|--------|
| **Discord read sync** | `python3 -m shorts_bot.integrations.discord_cli sync` |
| **Bubble wrap generation (our stack)** | `factory_cli bubble-batch` — uses Gemini, **not** Kling |
| **Course site free tool (~10/day)** | **Not wired yet** — needs URL + one-time login on hub |
| **Browser on hub** | Playwright — owner logs in once, agent reads after |

---

## Part 1 — Discord (read-only bot) — ~15 min

### Create the bot (you, in browser)

1. https://discord.com/developers/applications → **New Application**
2. **Bot** → **Add Bot** → copy **Token** (Runtime Secret: `DISCORD_BOT_TOKEN`)
3. **Bot permissions** — enable ONLY:
   - View Channels
   - Read Message History
4. **Disable** Send Messages, Add Reactions, Manage Messages — everything write-related OFF
5. **OAuth2 → URL Generator** → scopes: `bot` → invite bot to **TikTok Dojo / Momentum** server

### Channel allowlist

Copy channel IDs (Discord: right-click channel → Copy ID — needs Developer Mode on):

| Secret | Example |
|--------|---------|
| `DISCORD_GUILD_ID` | Server ID |
| `DISCORD_CHANNEL_IDS` | `123456789,987654321` (comma-separated) |

Suggested channels: `#tiktok-shop-chat`, content-review, `#violation-appeals` — whatever you actually read.

### Add to Cursor Secrets

| Secret | Type |
|--------|------|
| `DISCORD_BOT_TOKEN` | Runtime Secret |
| `DISCORD_GUILD_ID` | Environment Variable |
| `DISCORD_CHANNEL_IDS` | Environment Variable |

Start a **new cloud agent run** after adding secrets.

### Test

```bash
python3 -m shorts_bot.integrations.discord_cli status
python3 -m shorts_bot.integrations.discord_cli sync
```

Output: `data/research/course/inbox/discord-sync-YYYY-MM-DD.md`

Agent reads that file for coach tips, violation waves, clip feedback — **never posts**.

---

## Part 2 — Course website (free bubble tool) — hub browser

The creator’s **~10 free gens/day** tool lives on the course site. We do **not** have the URL in the repo yet.

### One-time login (hub laptop)

1. **START HUB** / Ubuntu up
2. Open visible browser on hub:

```bash
cd ~/proof-codex-ai
python3 -m shorts_bot.browser.cli open "PASTE_COURSE_URL_HERE" --minutes 20 --block
```

3. Log in with your course account (2FA if needed)
4. Cookies save to `data/browser_profile/` on that machine

### After login (agent, read-only)

Owner sends the exact URLs for:
- Course dashboard
- Free bubble-wrap generator page

Agent can `browse` those URLs headlessly and extract text/quota — **no Generate/Post clicks** until you explicitly ask.

**Important:** We already generate bubble slides in-repo (`bubble-batch`) without course credits. The course tool is **bonus capacity** — wire it when URL + login are confirmed.

---

## Part 3 — What we will NOT do

- **Never send Discord messages** from the bot (code is GET-only)
- **Never demo repo/architecture** to course creator (`GROUP_CALLS.md` IP rule)
- **Never auto-post** from course site without your OK

---

## Hour kill checklist (you)

- [ ] Create Discord bot + invite (read-only perms)
- [ ] Add 3 secrets to Cursor → new agent run
- [ ] Paste course site URL + bubble tool URL in chat (not password)
- [ ] Optional: log into course site on hub via `browser.cli open`

Then tell agent: **“Discord sync test”** or **“wire course site browse for URL X”**

---

## Related

- Bubble format: `data/research/course/BUBBLE_WRAP.md`
- Live updates: `data/research/course/GROUP_CALLS.md`
- Coach call inbox: `data/research/course/inbox/`
