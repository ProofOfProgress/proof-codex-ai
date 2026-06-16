# Autonomy handoff — closed loop status

**Updated:** June 16, 2026 (owner session)

---

## Done today

| Item | Status |
|------|--------|
| **YouTube draft #5** | **LIVE (public)** — https://youtube.com/shorts/unpPKed6jQM |
| **Facebook Page** | **Peripheral Horror** created (id=`61590716288819`) |
| **Facebook Reel** | Browser upload flow works — caption + Next + Post (check Reels tab) |
| **Recraft pose fix** | Comedy style for action shots; horror style only for face close-up |
| **Captions** | `CAPTION_MODE=off` — clean MP4 + `captions.srt` synced to TurboScribe lines |
| **Facebook analytics module** | `facebook_analytics.py` — needs Page token with `pages_read_engagement` |

---

## When you're back (~2 min)

### Meta API token (for autopost without browser)

1. Desktop → https://developers.facebook.com/tools/explorer/
2. Click **Register** (one-time developer signup — automation can't finish this modal alone)
3. **Generate Access Token** → **Peripheral Horror** Page
4. Permissions: `pages_manage_posts`, `pages_show_list`, `pages_read_engagement`
5. Cursor Secrets:
   - `FACEBOOK_PAGE_ID=61590716288819`
   - `META_PAGE_ACCESS_TOKEN=EAA...`
6. `bash scripts/install.sh`
7. `python3 -m shorts_bot.integrations.api_setup_cli --status`

Then autopost works:

```bash
python3 -m shorts_bot.production.closed_loop_cli --draft-id 5 --facebook
```

---

## Pipeline order (audio-first)

1. Resemble voice → `voiceover.mp3`
2. TurboScribe Whale → `turboscribe_transcript.txt` (Desktop export if Cloudflare blocks bot)
3. Recraft stills (comedy style = poses; horror style = close-up only)
4. ffmpeg render → `final_short.mp4` (no burned captions)
5. `captions.srt` from TurboScribe timing
6. YouTube + Facebook publish

---

## Commands

```bash
python3 -m shorts_bot.production.closed_loop_cli --draft-id 5 --status
python3 -m shorts_bot.integrations.api_setup_cli --status
python3 -m shorts_bot.integrations.facebook_upload_reel_cli --video data/production/draft_5/final_short.mp4
python3 -m shorts_bot.login_status
```

---

## Still manual / blocked

- **TurboScribe automation:** Cloudflare on VM — use Desktop export to `turboscribe_transcript.txt`
- **Meta developer Register:** modal needs one human click to complete signup
- **Facebook profile photo:** Switch into Page → upload `draft_5/images/00.11.png` (automation partial)
- **Page polish:** bio, website, cover — run `api_setup_cli` after Switch works
