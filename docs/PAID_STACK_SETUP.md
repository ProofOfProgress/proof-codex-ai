# Paid stack setup — buy today, wire today

Fully automated daily Shorts: **Gemini brain → Resemble voice clone → AssemblyAI transcript sync → stick figure frames → ffmpeg → YouTube upload (unlisted)**.

**Default:** `REQUIRE_PAID_STACK=true` — all video generation (`finish`, `make video`, `daily`) uses **Resemble + AssemblyAI** (API key, no browser). TurboScribe browser remains available via `TRANSCRIPT_PROVIDER=turboscribe`. No silent edge-tts or script-timing fallbacks unless you set `ALLOW_FREE_TTS_FALLBACK=true` or `ALLOW_SCRIPT_TIMING_FALLBACK=true`.

## 1. Buy & subscribe (today)

| Service | Plan | Cost | What you get |
|---------|------|------|--------------|
| **Google AI Studio** | Pay-as-you-go billing on | ~$1–3/mo | Gemini scripts + humanize |
| **Resemble AI** | Flex + Pro voice clone | ~$5/mo clone + ~$3–10 API | Your cloned voice |
| **AssemblyAI** | Pay-as-you-go | **~$0.01–0.05/Short** | Word-level timestamps via API (default) |
| **TurboScribe** (optional) | Unlimited (annual) | **$10/mo** | Browser Whale mode — legacy fallback |
| **Replicate** (optional) | Pay-per-image | **~$0.003–0.015/image** | Only if `VISUAL_STYLE=ai` — default is stick figures (free) |
| **Fal.ai** (optional) | Pay-per-image | **~$0.003–0.02/image** | Set `IMAGE_PROVIDER=fal` + `VISUAL_STYLE=ai` |

You do **not** need ElevenLabs, CapCut Pro, Runway, or Epidemic for the automated pipeline.

## 2. Create your voice clone (Resemble)

1. Sign up: https://app.resemble.ai
2. Load Flex credits (pay-as-you-go).
3. **Pro voice clone** ($5/mo per voice): upload 5–30 min of your clear speech.
4. Copy **API key**: Account → API
5. Copy **Voice UUID** from your clone.

```bash
python3 -m shorts_bot.production.voice_clone_cli list
python3 -m shorts_bot.production.voice_clone_cli test
```

## 3. AssemblyAI transcript sync (recommended)

1. Sign up: https://www.assemblyai.com/dashboard/signup
2. Copy API key from dashboard
3. Set in `.env`:

```
TRANSCRIPT_PROVIDER=assemblyai
ASSEMBLYAI_API_KEY=...
```

No browser login required — the bot uploads `voiceover.mp3` and gets word-level timestamps.

### TurboScribe (optional legacy)

1. Subscribe: https://turboscribe.ai/pricing ($10/mo billed yearly)
2. Set `TRANSCRIPT_PROVIDER=turboscribe` and log in via Desktop:

```bash
python3 -m shorts_bot.login_handoff --only turboscribe
```

## 4. Replicate image API (recommended)

1. Sign up: https://replicate.com
2. Create API token: https://replicate.com/account/api-tokens
3. Default model: `black-forest-labs/flux-schnell` (~$0.003/image at 9:16)
4. Test one frame:

```bash
python3 -m shorts_bot.production.image_cli
```

**Fal.ai alternative:** get key at https://fal.ai/dashboard/keys → set `IMAGE_PROVIDER=fal` and `FAL_API_KEY`.

## 5. Cursor Secrets (add these)

```
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash-lite
RESEMBLE_API_KEY=...
RESEMBLE_VOICE_UUID=...
TTS_PROVIDER=resemble
TRANSCRIPT_PROVIDER=assemblyai
ASSEMBLYAI_API_KEY=...
AUTO_PUBLISH_HOURS=0
AUTO_APPROVE_DRAFTS=true
AUTO_UPLOAD_YOUTUBE=true
YOUTUBE_UPLOAD_VISIBILITY=unlisted
VISUAL_STYLE=stickfigure
# Optional AI stills instead of stick figures:
# VISUAL_STYLE=ai
# IMAGE_PROVIDER=replicate
# REPLICATE_API_TOKEN=...
# REPLICATE_IMAGE_MODEL=black-forest-labs/flux-schnell
```

Then sync:

```bash
python3 scripts/sync_secrets.py
```

## 6. YouTube upload OAuth (one-time re-auth)

Upload needs the `youtube.upload` scope:

```bash
YOUTUBE_OAUTH_UPLOAD=1 python3 -m shorts_bot.youtube.auth_cli
```

## 7. Run one Short (full pipeline)

```bash
python3 -m shorts_bot.production.daily_cli
```

Or finish an existing draft:

```bash
python3 -m shorts_bot.production.finish_cli --draft-id 6 --upload
```

## 8. Daily cron (optional)

```cron
0 7 * * * cd /path/to/repo && python3 -m shorts_bot.production.daily_cli
```

## Pipeline order (automatic)

1. Humanize script (Gemini + local AI detect)
2. **Resemble** → `voiceover.mp3` (your clone)
3. **TurboScribe Whale** → `turboscribe_transcript.txt`
4. Rebuild **stick figure** frames (default) synced to real audio timing + ASS captions
5. ffmpeg → `final_short.mp4`
6. YouTube API upload (if `AUTO_UPLOAD_YOUTUBE=true`)

## Verify everything

```bash
python3 -m shorts_bot.login_status
make test
```
