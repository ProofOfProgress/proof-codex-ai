# Blender Python course — progress log

**Course:** [Blender Python for Artists](https://www.skool.com/cgpython/classroom/60a44c1e) (CG Python Academy, free)

**Started:** 2026-06-14

---

## Part checklist

| Part | Topic | Status | Applied to pipeline |
|------|-------|--------|---------------------|
| 1 | Python basics in Blender | **in progress** | `bpy_lab` 01–02 PASS |
| 2 | First operator + panel | pending | — |
| 2.5 | VSCode / external scripts | **done (VM)** | headless `build_and_render.py` |
| 3 | Working with objects | **in progress** | `bpy_lab` 06, 09; camera/creature keyframes |
| 4 | Custom operators + UI | pending | — |
| 5 | Shader / geo nodes in Python | **done (applied)** | `_relink_environment_textures()` — 68 fixed, 0 missing on draft #2 |
| 6 | Geometry / meshes | **in progress** | `bpy_lab` 11; gas-station FBX import |

---

## Lab scores

| Date | Score | Notes |
|------|-------|-------|
| 2026-06-14 | **12/12 PASS** | Added Part 5–6 drills: texture relink, shader nodes, FBX env, lamp keyframes |

Run: `blender --background --python shorts_bot/production/blender/bpy_lab.py`

---

## Notes per part

### Part 1 — Basics
- `bpy.data.objects` / `bpy.context.active_object` — never instantiate Mesh() directly
- Materials: `mat.use_nodes = True`, grab `Principled BSDF`

### Part 3 — Objects
- `obj.location`, `obj.rotation_euler`, `obj.keyframe_insert(data_path="location", frame=N)`
- Headless: set active object + mode before `bpy.ops`

### Part 5 — Nodes (critical for our bug) — APPLIED 2026-06-14
- Image Texture node → link to Principled Base Color
- Relink `img.filepath` + `img.reload()` when FBX paths break
- **Result:** `Environment textures: fixed=68 ok=71 missing=0`
- **Preview:** `data/production/draft_2/blender_preview_wave.png` — creature lit, trees visible; camera still needs framing toward pumps (Part 3 next)
- Night grade: skip albedo crush when texture nodes are live

### Part 6 — Geometry / import
- `bpy.ops.import_scene.fbx` / `import_scene.gltf`
- Parent imported roots, scale env, fit bounds

---

## Next actions

1. **Part 3 — camera framing:** wave clip camera must show pumps/canopy (currently trees + grey ground dominate)
2. Re-render 3 clips after camera fix → owner preview before any YouTube
3. Finish CG Python Part 4 (operators) when pipeline stable
