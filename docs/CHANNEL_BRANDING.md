# Channel branding — The Minute Before

**Channel:** Soft Continuity  
**Series hook:** *The Minute Before* — one specific moment → one concrete fix.

## One command (API + assets)

```bash
python3 -m shorts_bot.brand.assets      # profile.png + banner.png
python3 -m shorts_bot.youtube.brand_cli # name + description + banner via API
```

Discord / chat: `apply brand` or `!applybrand`

## Assets (auto-generated)

| File | Size | Role |
|------|------|------|
| `channel/brand/assets/profile.png` | 800×800 | Clock-at-11:59 avatar (Studio upload if API path can't set it) |
| `channel/brand/assets/banner.png` | 2560×1440 | Hero: *The Minute Before* + tagline |
| `channel/brand/youtube_copy.txt` | — | Name, description, pinned comment |

Visual system matches `channel/brand/identity.md` — void gradient `#0B0D10`, calm blue `#8EB8FF`, oracle purple `#C4A1FF`.

## What the API sets automatically

- Display name **Soft Continuity**
- Channel description (Minute Before positioning + pillars)
- Banner image

## Profile picture

YouTube Data API v3 does not set the channel avatar. `apply brand` tries Playwright Studio upload when `browser_enabled=true` and the browser profile is logged in; otherwise upload `profile.png` once in Studio → Customization → Branding.

## Jenny alignment

- **File 03:** specific niche (*minute before* moments, not generic sleep tips)
- **File 09:** name + description match what viewers see in the first 3 seconds
- **File 05:** banner stays calm — text in YouTube safe zone, no clutter
