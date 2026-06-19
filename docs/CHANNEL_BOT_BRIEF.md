# Channel bot brief — paste this to any new agent

Copy everything inside the block below into Cursor chat when starting a fresh agent or after a long break.

---

```
CHANNEL CONTEXT — read fully before doing anything

## Hardcoded rule (never override)

**InVideo is the soul of our channel.**

All video production flows through InVideo AI (Agent One + AI Twin + stock UI + captions).
Do NOT invest in homemade render (Blender, Recraft, Replicate I2V, ffmpeg pipelines) unless the owner explicitly asks.
If a task doesn't move InVideo → finished MP4 → YouTube upload → analytics learning, deprioritize it.

---

## North star

100% AI-automated YouTube Shorts channel that makes money.
One channel, AI/tech rebrand. Self-learning from YouTube analytics.
Owner is NOT a developer — plain English, exact steps, do the technical work yourself.

---

## Niche (locked)

- **Big:** AI / Tech
- **Format:** ~30 second YouTube Shorts
- **Sub-niche:** Honest AI product reviews — one real product per video
- **Verdict:** Pay / Skip / Wait (clear call at the end)
- **Tone:** Skeptical but fair. No hype-bro. Sincere honesty first.
- **Presenter:** Owner's **InVideo AI Twin** (face + voice) — not stock actors
- **Retired:** Peripheral horror, jumpscares, CCTV grammar, homemade video stack

---

## Production pipeline (how videos get made)

1. **Brief, not script** — agent sends a creative *prompt* to InVideo; InVideo writes the script
2. **InVideo generates** — twin on camera + tight app UI B-roll + captions (9:16 Shorts only)
3. **MP4 on disk** — browser download OR owner pastes Google Drive link (see blockers)
4. **YouTube upload** — API, public, synthetic media disclosed
5. **Analytics → learn** — winners get reused; losers get avoid rules

Key commands:
- Start project: `python3 -m shorts_bot.invideo.generate_cli --draft-id N --open-browser`
- Browser download: `python3 -m shorts_bot.invideo.download_cli --draft-id N`
- Import from link: `python3 -m shorts_bot.invideo.fetch_url_cli --draft-id N 'DRIVE_URL'`
- Upload: `python3 -m shorts_bot.production.upload_canonical_cli --draft-id N --video data/production/draft_N/final_short.mp4`
- Agent One chat: `python3 -m shorts_bot.invideo.agent_one_cli --open-browser "brief here"`

InVideo MCP returns a **project URL only** — no MP4 API. Browser or Drive link closes the gap.

---

## InVideo Shorts rules (learned from v1 test)

- 9:16 vertical ONLY — no widescreen stock cropped into vertical (looked wonky on v1)
- Twin fullscreen for most shots; tight mobile/desktop UI — not wide desk stock
- 4–5 beats max, hook in first 2 seconds
- Bold captions, bottom third, Shorts safe zone
- Default brief template: `shorts_bot/invideo/prompts.py`

Twin must exist in InVideo before quality renders — owner sets up via webcam once.

---

## Owner constraints (critical)

- **Cannot attach files in Cursor** — use Google Drive/Dropbox links or agent browser fetch
- **Phone broken** — all 2FA/SMS goes to dead phone; TikTok OAuth paused; InVideo VM login blocked until Google 2FA bypass (backup codes, passkey, or InVideo email login)
- **Low energy** — minimize owner steps; browser handoff to exact screen, then "your turn"
- **YouTube works** — OAuth on VM is done; upload without owner
- **No new paid I2V** — `AI_VIDEO_GENERATION_ENABLED=false` unless owner asks

**Broken-phone MP4 path:** laptop (may still be logged into InVideo) → Download → Drive → paste link → `fetch_url_cli`

---

## Top 4 priorities only (see docs/PRIORITIES.md)

1. InVideo pipeline — prompt → twin + stock → MP4 on disk
2. Niche lock + script templates — real product names, Pay/Skip/Wait
3. Daily closed loop — topic → InVideo → QC → YouTube, no Studio clicks
4. Analytics learning — hooks/topics from data, not horror Codex baggage

Backlog until top 4 done: TikTok, long-form, multi-channel, code purges, refactors.

---

## Compliance

- YPP-safe: max 1 upload / 24h, original opinions, no template farm slop
- Declare synthetic media on every upload
- Uploads go **public** without pre-review (owner approved)
- Do NOT upload QA iteration builds to YouTube

---

## What "done" looks like

Owner says "make a video about [product]" → agent sends InVideo brief → MP4 lands in draft folder → YouTube post → analytics sync → next video improves from data.

InVideo is not a nice-to-have tool. It IS the channel's production engine.
```

---

Saved in repo so agents can read: `python3 -m shorts_bot.codex read docs/CHANNEL_BOT_BRIEF.md`
