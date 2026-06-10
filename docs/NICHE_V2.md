# Niche v2 + deep research

## The Minute Before

Run before every daily Short:

```bash
python3 -m shorts_bot.production.research_cli
python3 -m shorts_bot.production.daily_cli
```

Research caches to `data/research/<topic-slug>.json` and injects into draft generation.

## Caption framing (Jenny 05)

YouTube Shorts overlays **title + buttons** on the bottom ~15–18% of the frame. Burned-in captions were at 80px from bottom — covered by the UI.

**Fix:** captions now sit **320px above bottom**; AI stills compose subject in **upper 60%**.

Source: Jenny Hoyos course file `05_visuals_silent_clarity.md` — rule of thirds, safe zone, mute review.

Constants: `shorts_bot/production/framing.py`

## Captions (v2 — ffmpeg default)

Old: PIL bar on every PNG (buggy wrap, double captions with ASS).

New: **clean stills + ffmpeg ASS burn-in** at render time.

```bash
CAPTION_MODE=ffmpeg   # default — recommended
CAPTION_MODE=frame    # PIL fallback only
```

## Fresh start (purge old videos)

```bash
python3 -m shorts_bot.youtube.purge_cli          # delete all YT videos + local drafts
python3 -m shorts_bot.youtube.purge_cli --dry-run
```

**YouTube delete** needs `youtube.force-ssl` on your token. Re-auth once:

```bash
rm -f data/youtube_token.json
YOUTUBE_OAUTH_UPLOAD=1 python3 -m shorts_bot.youtube.auth_cli
python3 -m shorts_bot.youtube.purge_cli --youtube-only
```

Or delete the 3 test Shorts manually in YouTube Studio → Content.
