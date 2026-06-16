# Facebook setup — Peripheral (Lost Boy shorts)

**Goal:** Post the same Shorts to **Facebook Reels** for the older Facebook crowd. No Facebook API is wired in the bot yet — this is the owner checklist + what the agent opens in the browser.

---

## What to create (recommended)

| Step | What | Why |
|------|------|-----|
| 1 | **Personal Facebook account** (or use existing) | Required to manage a Page |
| 2 | **Facebook Page** named **Peripheral** (or "Peripheral Horror") | Reels post from Pages, not personal profiles |
| 3 | **Page → Professional dashboard → Reels** | Where Shorts get uploaded |
| 4 | Link **Instagram** (optional) | Cross-post Reels later |

**Category:** Entertainment · **Bio:** `Scary micro-stories from the woods. don't blink.`

---

## Agent browser handoff

```bash
python3 -m shorts_bot.integrations.facebook_handoff_cli --open-browser
```

Opens Desktop browser tabs:

1. Facebook sign-up / log in  
2. Create Page  
3. Meta Business Suite (optional — scheduling Reels)

**You must finish:** email/phone verify, password, Page name. Agent cannot complete 2FA or identity checks alone.

---

## Posting workflow (manual until API)

After a Short renders on disk (`data/production/draft_N/final_short.mp4`):

1. Open [facebook.com](https://www.facebook.com) → your **Page**
2. **Create** → **Reel**
3. Upload `final_short.mp4`
4. Caption (copy from `upload_metadata.json` or use hook + hashtags):
   - `If a child waves at you on this trail, do not wave back. 👀`
   - `#horror #scarystories #creepy #lostinthewoods`
5. **Share now** or schedule in Meta Business Suite

**Tip for older Facebook:** Big readable caption, creepy still as cover frame (Lost Boy between trees).

---

## Secrets (future automation)

When Meta Graph API is added, these will live in Cursor Secrets:

| Secret | Purpose |
|--------|---------|
| `FACEBOOK_PAGE_ID` | Page to post Reels |
| `META_ACCESS_TOKEN` | Long-lived page token |

Not required for manual posting today.

---

## Status

```bash
python3 -m shorts_bot.integrations.facebook_handoff_cli --status
```
