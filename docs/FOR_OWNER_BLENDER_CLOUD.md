# Blender on a weak PC — what you need to know

**You never have to run Blender** — but you **can** if you want to fix lighting, textures, or camera yourself. All cloud rendering still works without your PC.

---

## Get the Blender folder (owner access)

| Method | What to do |
|--------|------------|
| **Browse on GitHub** | [shorts_bot/production/blender](https://github.com/ProofOfProgress/proof-codex-ai/tree/main/shorts_bot/production/blender) · [channel/assets](https://github.com/ProofOfProgress/proof-codex-ai/tree/main/channel/assets) |
| **Download a zip** | Ask agent: `make owner blender pack for draft 2` — or run `python3 -m shorts_bot.production.blender.owner_pack_cli --draft-id 2 --with-blend` on cloud → download `data/production/draft_2/OWNER_BLENDER_PACK_draft_2.zip` from Cursor file tree |
| **Shared 3D workspace (best)** | Start web UI → open **http://127.0.0.1:8080/workspace/draft/2** — drag creature/camera in browser, live sync, click Save |
| **Open in Blender Desktop** | Unzip → open `peripheral_draft_2.blend` in [Blender 4.x](https://www.blender.org/download/) → fix scene → save → send `.blend` back |

Full map: `shorts_bot/production/blender/README_FOR_OWNER.md`

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

- `make owner blender pack for draft 2` — zip of 3D assets (+ optional .blend) to download
- `re-render draft 2 in blender` — full cloud render
- `show me a wave preview` — one clip test (~12 min cloud)
- `make the creature wave creepier` — edits English motion prompt, re-renders
- `I fixed the blend file` — after you edited lighting/textures in Blender Desktop

You do **not** need to open Blender unless you **want** to help with the scene craft.

---

## Speed settings (cloud only)

In `.env` on the cloud (agent manages this):

- `BLENDER_SAMPLES=16` — fast enough, decent quality
- `BLENDER_SAMPLES=32` — slower, slightly cleaner

Your home PC specs do not matter for rendering.
