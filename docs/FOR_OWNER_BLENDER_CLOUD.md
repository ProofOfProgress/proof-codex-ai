# Blender on a weak PC — what you need to know

**You never install or run Blender.** All 3D work happens on the **cloud machine** (Cursor agent). Your PC only opens pictures, links, or YouTube.

---

## What the cloud does for you

1. Builds the gas-station horror scene
2. Animates the creature from English descriptions (beat sheet → AI → bones)
3. Renders 3×10 second clips → stitches → 30s Short with SFX
4. Saves preview PNGs you can click in Cursor
5. Writes `data/production/draft_N/WATCH.md` with watch instructions

**Cost:** $0 per video (no Kling/Replicate credits).

---

## How you watch results

| Method | Steps |
|--------|--------|
| **PNG pictures** | Open `data/production/draft_2/preview_frames/full_contact_sheet.png` in Cursor file tree |
| **Browser** | Port-forward 8080 → open `/preview/draft/2` |
| **Google Drive** | Upload `final_short.mp4` → share link → phone |
| **YouTube** | Only when you approve a final upload (not every test) |

---

## What you say to the agent

- `re-render draft 2 in blender` — full cloud render
- `show me a wave preview` — one clip test (~12 min cloud)
- `make the creature wave creepier` — edits English motion prompt, re-renders

You do **not** need to open Blender, install GPU drivers, or download SCP models.

---

## Speed settings (cloud only)

In `.env` on the cloud (agent manages this):

- `BLENDER_SAMPLES=16` — fast enough, decent quality
- `BLENDER_SAMPLES=32` — slower, slightly cleaner

Your home PC specs do not matter for rendering.
