# Autonomy handoff — where the closed loop is stuck

**North star:** one command ships a Short (YouTube + Facebook) with no you in the middle.

**Updated:** owner logged into Meta Dev, TurboScribe, and Facebook on Desktop.

---

## Closed loop map

| Step | Status | Blocker |
|------|--------|---------|
| Script + approve | ✓ Works | Still manual approve (gate #4) |
| Resemble voice | ✓ Works | — |
| **TurboScribe timestamps** | ⚠ Partial | **Cloudflare blocks Playwright** — use Desktop export OR cached `turboscribe_transcript.txt` |
| Recraft stills (Lost Boy) | ⚠ Maintenance | Content filter, group shots |
| ffmpeg MP4 + captions.srt | ✓ Works | Clean video + SRT (no burn-in) |
| YouTube upload/schedule | ✓ Works | YPP 1 Short / 24h |
| **Facebook Reel** | ⚠ Almost | Page **Peripheral Horror** created (`id=61590716288819`) — need Meta developer + Page token |
| Daily autopilot | ✗ Not on | Needs stable video factory first |
| Analytics → learn | ✓ Partial | Needs more live videos |

---

## Check status (agent or you)

```bash
python3 -m shorts_bot.production.closed_loop_cli --draft-id 5 --status
python3 -m shorts_bot.login_status
python3 -m shorts_bot.integrations.meta_token_handoff_cli
```

---

## What you still need (~3 min on Desktop)

### Facebook API tokens (unblocks autopost) — ~2 min on Desktop

**Page already created:** Peripheral Horror (`FACEBOOK_PAGE_ID=61590716288819`)

1. Click **Desktop** in Cursor
2. Open https://developers.facebook.com/tools/explorer/
3. Click **Register** (one-time — accept developer terms)
4. Back in Explorer → **Generate Access Token** → pick **Peripheral Horror** Page
5. Permissions: `pages_manage_posts`, `pages_show_list`
6. Copy the **Page access token** (starts with `EAA`)
7. Add to **Cursor → Cloud Agent → Secrets**:
   - `FACEBOOK_PAGE_ID=61590716288819`
   - `META_PAGE_ACCESS_TOKEN=<paste token>`
8. Run: `bash scripts/install.sh`
9. Verify: `python3 -m shorts_bot.integrations.api_setup_cli --status`

### Facebook Page (if not created yet)

Business Suite showed no Pages — create one named **Peripheral** (Entertainment):

```bash
python3 -m shorts_bot.integrations.facebook_handoff_cli --open-browser
```

### TurboScribe (when you want fresher cuts)

Playwright cannot pass Cloudflare on the VM. On Desktop:

1. Upload `data/production/draft_N/voiceover.mp3` to TurboScribe (Whale mode)
2. Export timestamped transcript
3. Save as `data/production/draft_N/turboscribe_transcript.txt`

Or run handoff:

```bash
python3 -m shorts_bot.production.turboscribe_handoff_cli --draft-id 5
```

**Draft 5 already has a good transcript on disk** — no re-export needed unless script changes.

---

## Latest good video (local)

- `data/production/draft_5/final_short.mp4`
- `data/production/draft_5/captions.srt` (timed to voice, not on video)
- YouTube: https://youtube.com/shorts/unpPKed6jQM (scheduled)

---

## One command when tokens are set

```bash
python3 -m shorts_bot.production.closed_loop_cli --draft-id 5 --youtube --facebook
```

Render-only (no upload):

```bash
python3 -m shorts_bot.production.closed_loop_cli --draft-id 5
```
