# Blender Python course — progress log

**Course:** [Blender Python for Artists](https://www.skool.com/cgpython/classroom/60a44c1e) (CG Python Academy, free)

**Started:** 2026-06-14

---

## Part checklist

| Part | Topic | Status | Applied to pipeline |
|------|-------|--------|---------------------|
| 1 | Python basics in Blender | **done** | `bpy_lab` 01–02 + course ex 1.01–1.02 PASS |
| 2 | First operator + panel | **done** | course ex 2.01 register/run operator PASS |
| 2.5 | VSCode / external scripts | **done (VM)** | headless `build_and_render.py` |
| 3 | Working with objects | **done (applied)** | course ex 3.01–3.05 PASS; raised lunge POV + `_camera_point_at()` |
| 4 | Custom operators + UI | pending | — |
| 5 | Shader / geo nodes in Python | **done (applied)** | `_relink_environment_textures()` — 68 fixed, 0 missing on draft #2 |
| 6 | Geometry / meshes | **in progress** | `bpy_lab` 11; gas-station FBX import |

---

## Lab scores

| Date | Score | Notes |
|------|-------|-------|
| 2026-06-14 | **12/12 PASS** | bpy_lab all modules |
| 2026-06-14 | **8/8 PASS** | CG Python course exercises Parts 1–3 (incl. 3.05 elevated lunge POV) |

Run: `blender --background --python shorts_bot/production/blender/bpy_lab.py`

---

## Notes per part

### Part 1 — Basics
- `bpy.data.objects` / `bpy.context.active_object` — never instantiate Mesh() directly
- Materials: `mat.use_nodes = True`, grab `Principled BSDF`

### Part 2 — Operator (add-on tutorial exercise)
- `bpy.types.Operator`, `register()` / `unregister()`, `bpy.ops.peripheral.move_x()`
- Headless: register → run → unregister (no GUI keymaps needed)

### Part 3 — Objects — APPLIED 2026-06-14
- `obj.location`, keyframes, collections, linked duplicates
- **`_camera_point_at()`** via TRACK_TO constraint (course: constraints → applied rotation)
- **`_lunge_camera_height()`** + **`_creature_lunge_camera_positions()`** — raised POV for micro jumpscare (owner: camera higher)
- Wave camera: `(0, -5.5, 1.55)` → looks at creature at pumps; no procedural trees when FBX loaded
- Run: `blender --background --python shorts_bot/production/blender/course_exercises.py`

### Part 5 — Nodes (critical for our bug) — APPLIED 2026-06-14
- Image Texture node → link to Principled Base Color
- Relink `img.filepath` + `img.reload()` when FBX paths break
- **Result:** `Environment textures: fixed=68 ok=71 missing=0`
- **Mouth emissive (2026-06-14):** `_apply_creature_mouth_emissive()` — red UV mouth glows at lunge peak
- **Preview:** `data/production/draft_2/blender_preview_wave.png` — scene-only (no creature); road/trees visible
- **Gemini vision QC (2026-06-14):** score **2.5/10 FAIL** — see `data/research/GEMINI_SCENE_REVIEW_draft_2.md`. Pumps/canopy not readable; camera must frame gas station hero; add flicker lighting
- Night grade: skip albedo crush when texture nodes are live

### Part 6 — Geometry / import
- `bpy.ops.import_scene.fbx` / `import_scene.gltf`
- Parent imported roots, scale env, fit bounds

---

## Owner direction (2026-06-14)

**Scene first, creature later.** Monster removed from default renders until the gas-station lot reads like LIGHTS ARE OFF. Course is authority; owner notes are input.

- Default: `BLENDER_INCLUDE_CREATURE=0` (scene-only)
- Restore creature: `BLENDER_INCLUDE_CREATURE=1`
- Scene preview: `blender ... build_and_render.py -- --draft-id 2 --preview --scene-only`

## Next actions

1. **Camera + framing (Part 3):** point at pump island `(0, -8, 2.2)` so canopy/signs read — Gemini flagged this as #1 gap
2. **Part 5/6:** emissive pump signs, streetlight flicker, fog readability
3. Re-render scene-only wave → Gemini QC again before owner still approval
4. Part 4 operators — creature returns only after set passes QC
