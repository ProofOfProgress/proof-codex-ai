# YouTube channel polish — paste when logged in

Use after `auth_cli` or manual Studio login. No images required yet — text + Canva later.

## Automatic name + description (bot)

Edit `channel/brand/youtube_copy.txt`, then run **one** of:

```bash
python3 -m shorts_bot.youtube.brand_cli
```

- Web UI → **Learning** → **Apply name & description to YouTube**
- Web chat: `apply brand`
- Chat/agent: `apply_channel_branding` tool

Requires a saved YouTube login in `data/browser_profile` (same session as channel setup).

## Channel name

**Soft Continuity** (or keep your existing name — brand voice still applies)

## Handle ideas

`@softcontinuity` · `@stilllistening` · `@quietindex`

## Description (paste into Studio → Customization → Basic info)

```
Small fixes for heavy days.

Calm, faceless Shorts — sleep, focus, boundaries, and the quiet stuff nobody explains well.
One idea. One action. No noise.

You're still here. Good.
```

## Links line

`Web tools: (add later)` · `Business: (optional email)`

## Default upload settings

- **Visibility: Private** (bot uploads here; you flip to Public when ready — the only manual step per video)
- Category: Education
- Shorts: always 9:16, under 60s
- Comments: on (learn from feedback)
- License: Standard

## Banner (until custom art)

1. Open `channel/brand/assets/banner.svg` in browser
2. Screenshot at full width OR import to Canva → export 2560×1440
3. Upload to Studio → Branding → Banner

## Profile icon

Use Canva: soft circle gradient + thin ring (see `identity.md` colors)

## First 3 playlists

1. Sleep
2. Focus
3. Boundaries

## Pinned comment template

"Which topic should the next Short solve? One sentence only."
