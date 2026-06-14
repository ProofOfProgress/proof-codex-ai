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
| 5 | Shader / geo nodes in Python | **in progress** | `bpy_lab` 10; `_relink_environment_textures()` |
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

### Part 5 — Nodes (critical for our bug)
- Image Texture node → link to Principled Base Color
- Relink `img.filepath` + `img.reload()` when FBX paths break
- **Why draft #2 looked unchanged:** textures 0×0, not missing geometry

### Part 6 — Geometry / import
- `bpy.ops.import_scene.fbx` / `import_scene.gltf`
- Parent imported roots, scale env, fit bounds

---

## Next actions

1. Finish CG Python Part 5 exercises → improve `_relink_environment_textures()` until preview shows pumps/signs
2. Part 3 → wire `scene_layout.json` offsets into wave animation (when workspace work resumes)
3. Re-render draft #2 only after preview frame passes owner bar (LIGHTS ARE OFF)
