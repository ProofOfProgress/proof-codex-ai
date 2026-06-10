# Channel branding — Jenny-informed setup

**Jenny Hoyos course alignment:**
- **File 03 (Blue Ocean):** niche positioning — we use *The Minute Before* (specific moments, not generic sleep tips)
- **File 09 (Growth/CTA):** brand integration — name + description match what viewers see in the first 3 seconds
- **File 05 (Visuals):** safe-zone framing for captions; banner/profile should stay calm, not cluttered

## Automated (API — no browser)

```bash
python3 -m shorts_bot.brand.assets   # or Discord: generate assets
python3 -m shorts_bot.youtube.brand_cli   # API name + description + banner
```

Discord: `apply brand` or `!applybrand`

Assets:
- `channel/brand/assets/profile.png` — 800×800
- `channel/brand/assets/banner.png` — 2560×1440
- Copy: `channel/brand/youtube_copy.txt`

## Manual (one-time)

**Profile picture:** Studio → Customization → Branding → upload `profile.png`  
(YouTube Data API v3 does not set channel avatar reliably.)

## Strong name + description (v2)

**Name:** Soft Continuity  
**Series hook:** The Minute Before  
**Description:** see `youtube_copy.txt` — specific moments, faceless calm Shorts, no hustle noise.
