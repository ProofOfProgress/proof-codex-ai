# Blender folder — for you (owner)

You **can** help with lighting, textures, and camera in Blender on your PC. The cloud agent runs the same files — you edit, we re-render.

---

## Browse online (no install)

| What | Link |
|------|------|
| **Blender code folder** | https://github.com/ProofOfProgress/proof-codex-ai/tree/main/shorts_bot/production/blender |
| **3D assets** (gas station, creature, motion) | https://github.com/ProofOfProgress/proof-codex-ai/tree/main/channel/assets |
| **Quality refs (LIGHTS ARE OFF)** | `data/research/LIGHTS_ARE_OFF_BLENDER_REFERENCE.md` in the repo |

---

## Download everything to open in Blender

On the cloud machine (or ask the agent):

```bash
python3 -m shorts_bot.production.blender.owner_pack_cli --draft-id 2
```

That creates:

`data/production/draft_2/OWNER_BLENDER_PACK_draft_2.zip`

**In Cursor:** click that zip in the file tree → **Download**. Unzip on your PC.

Inside the zip:

| File / folder | What it is |
|---------------|------------|
| `peripheral_draft_2.blend` | Full scene (if `--with-blend` was used) — open in **Blender 4.x** |
| `assets/environments/` | Gas station FBX + textures |
| `assets/creatures/` | Form 2 creature model |
| `assets/motion_exports/` | Wave / lunge / open animations (Mixamo FBX) |
| `HOW_TO_HELP.md` | Short checklist |

---

## Open the scene in Blender (your PC)

1. Install [Blender 4.x](https://www.blender.org/download/) (free).
2. Unzip `OWNER_BLENDER_PACK_draft_2.zip`.
3. Double-click `peripheral_draft_2.blend` (or File → Open).
4. Press **0** on the numpad (or View → Camera) to see what the Short will look like.
5. Fix what looks wrong — lighting, materials, camera angle, gas station scale.
6. **File → Save** and send the `.blend` back (Google Drive, Discord, or tell the agent the path if you cloned the repo).

Tell the agent: *“I fixed draft 2 blend — use `path/to/peripheral_draft_2.blend`”* and we wire it into the next render.

---

## Folder map (plain English)

```
shorts_bot/production/blender/
  build_and_render.py     ← builds the gas-station scene + renders clips (the main one)
  produce_cli.py          ← full 30s Short (3 clips + stitch)
  owner_pack_cli.py       ← zip for you to download
  bpy_lab.py              ← agent training drills (ignore unless curious)

channel/assets/
  environments/gas_station/   ← CC0 gas station 3D model + Textures/
  creatures/scp_096/          ← Form 2 creature
  motion_exports/             ← draft_2_open.fbx, wave, lunge

data/production/draft_2/
  final_short.mp4             ← finished video
  preview_frames/             ← PNG stills (easy to check without video player)
  clips/                        ← 3×10s Blender clips
```

---

## Best ways you can help

1. **Lighting** — scene too dark or flat? Add a fill light or tweak streetlight color in Blender.
2. **Textures** — gas station looks grey? In Shading workspace, check image textures point to the `Textures/` folder.
3. **Camera** — frame the pumps + creature like the LIGHTS ARE OFF Shorts (refs in `data/research/LIGHTS_ARE_OFF_BLENDER_REFERENCE.md`).
4. **Scale** — creature too small/big vs pumps? Select `Form2Rig` and scale.
5. **Send back** — saved `.blend` or screenshots of what you changed.

You do **not** need to edit Python. Blender UI is enough.

---

## Ask the agent

- `make owner blender pack for draft 2` — zip ready to download  
- `save blend file for draft 2` — `.blend` in `data/production/draft_2/`  
- `re-render draft 2 after my blend fix` — cloud render using your file
