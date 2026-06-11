# Shorts alignment — camera, captions, audio sync

Research-backed layout for **1080×1920** Soft Continuity stick-figure Shorts.

## The three layers (must not fight each other)

| Layer | What it is | Our implementation |
|-------|------------|-------------------|
| **Camera / subject** | Stick figure + props in the “safe action” band | Upper ~35–55% of frame, left of right UI rail |
| **Captions** | Burned ASS via ffmpeg (default) | Lower-middle band **above** Shorts title/like rail |
| **Audio sync** | Cut when voice changes | TurboScribe Whale timestamps → fallback script scaled to MP3 length |

Do **not** bake captions into PNGs when `CAPTION_MODE=ffmpeg` (double captions).

## YouTube Shorts safe zones (2025–2026)

Sources: [Poster.ly safe zone](https://www.poster.ly/tools/youtube-shorts-safe-zone-checker), [Koro dimensions](https://getkoro.app/blog/youtube-shorts-dimensions), [cross-platform subtitle guide](https://github.com/stkzlv/ContentEngineAI/blob/main/docs/subtitle-best-practices.md).

| Edge | Keep clear (1080×1920) |
|------|-------------------------|
| Top | ~120–380 px (status, search) |
| Bottom | **380–480 px** (title, channel, subscribe, progress) |
| Right | **120 px** (like, comment, share) |
| Left | ~60 px |

**Safe content box:** roughly **900×1160 px** centered — use for logos; stick figures use upper portion, captions use lower-middle.

### Caption placement (burned-in)

- **Wrong:** bottom 320 px margin → captions sit at **y≈1600**, inside the UI rail (covered by title/buttons).
- **Right:** anchor caption block with bottom edge ~**380–420 px** above frame bottom → ASS `\an2\pos(540,1500)` on 1920-tall canvas.
- Cross-post tip: TikTok needs **bottom 480 px** clear — if you expand to TikTok later, raise captions slightly (center Y ~1280).

### Subject / “camera” (stick figure)

- Place action **above** caption band: center Y ~**700–900 px** (not bottom half).
- Offset X **slightly left of center** (~42% width) so arms/props miss the right action rail.
- Keep bottom **40%** of frame visually quiet for captions + platform UI.

## Audio ↔ picture sync

| Method | Quality | When |
|--------|---------|------|
| **TurboScribe Whale** | Best — word-level timestamps | Default when browser session logged in |
| **Script scaled to MP3 duration** | Good — sentence cuts match total runtime | Fallback when TurboScribe fails |
| **Raw script WPS estimate** | Weak — drift vs real VO | Old fallback only |

Pipeline order: Resemble VO → measure `voiceover.mp3` → TurboScribe OR `segments_from_script_for_duration()` → render.

## Video quality (ffmpeg)

| Issue | Fix |
|-------|-----|
| Soft PNG concat | `scale=1080:1920:flags=lanczos` on every frame |
| Blocky gradients | `crf` 18–20, `preset` slow/medium |
| Wrong pixel format | `yuv420p` + `faststart` for mobile |
| Quiet voice | AAC 192k |

Config: `VIDEO_CRF`, `VIDEO_PRESET` in `.env`.

## Checklist before upload

1. Mute play — does each **cut** match the spoken line?
2. Captions readable and **not** under Shorts title?
3. Stick figure not under like/comment buttons?
4. Upload `captions.srt` in Studio (SEO) even when burned-in (both is best practice).
5. Review on phone if possible — safe zones vary slightly by device.

## Constants (code)

All tunables live in `shorts_bot/production/framing.py` — single source of truth for ASS, PIL fallback, and stick placement.
