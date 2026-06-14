# Blender mastery curriculum (agent training)

**Purpose:** Teach cloud agents to run Peripheral horror Shorts in Blender **headlessly via Python (bpy)** — not manual clicking. Last updated: 2026-06-14.

**Validate on VM:** `blender --background --python shorts_bot/production/blender/bpy_lab.py`

---

## Do free “AI Blender courses” exist?

**Yes, but they are mostly pipelines — not “Blender AI inside the app.”**

| Course / resource | Cost | AI angle | Best for us? |
|-------------------|------|----------|--------------|
| [FindSkill — AI for 3D Design](https://findskill.ai/courses/ai-for-3d-design/) | Free tier lessons | Meshy/Tripo → **Blender cleanup** → Mixamo/DeepMotion animation | **High** — matches import-rig-animate workflow |
| [Proscenium Blender addon](https://github.com/animatica-ai/proscenium-blender) | Free addon, cloud gen | Text-to-motion on armatures (Blender 5+) | Medium — needs Blender 5 + account |
| [Kimodo local pipeline (YouTube)](https://www.youtube.com/watch?v=nNmeuvew8LY) | Free | Text-to-BVH → Rokoko retarget in Blender | **High** for future creature motion |
| [Blender MCP / Claude Connector](https://lecture.nakayasu.com/en/docs/blender/claude-connector/) | Free docs | Natural language → bpy in Blender | **High** — same as our agent approach |
| [CG Python Academy — Blender Python for Artists](https://www.skool.com/cgpython/blender-python-for-artists-course) | Free (Skool) | None — pure bpy | **Highest** for automation |
| [Official Blender Python API](https://docs.blender.org/api/current/) | Free | None | **Required reference** |
| [Blender Guru — How to use Eevee](https://www.youtube.com/watch?v=-gW6vk_OuNQ) | Free YouTube | None | **High** — we render EEVEE 720×1280 |
| [Blender Guru — Lighting for Beginners](https://www.youtube.com/watch?v=Ys4793edotw) | Free YouTube | None | High — fixes “too dark” complaint |

**Bottom line for Peripheral:** There is no single “AI Blender course.” The winning stack is:

1. **bpy scripting** (build scenes, keyframes, render headless) — our `build_and_render.py`
2. **EEVEE lighting** (probes, fill, streetlight) — quality without Cycles cost
3. **AI motion import** (Mixamo, Kimodo, Proscenium) layered on imported rigs — wave/lunge beats

---

## Coding-first curriculum (what agents must master)

Work in order. Each module has a **drill** (run on VM) and **Peripheral application**.

### Module 1 — bpy fundamentals (Official Quickstart)

**Source:** https://docs.blender.org/api/current/info_quickstart.html

| Concept | Rule |
|---------|------|
| Data access | `bpy.data.objects`, `bpy.data.actions` — never `Mesh()` constructor |
| Context | Read-only `bpy.context`; set active via `bpy.context.view_layer.objects.active` |
| Operators | `bpy.ops.mesh.primitive_cube_add()` — check `.poll()` in headless |
| Keyframes | `obj.keyframe_insert(data_path="location", frame=N)` |

**Drill:** `bpy_lab.py` modules 01–02  
**Apply:** `_clear_scene()`, `_add_ground_and_road()`, `_mat()`

### Module 2 — Headless rendering

**Source:** Blender manual — Command Line & Python

| Setting | Peripheral default |
|---------|-------------------|
| Engine | `BLENDER_EEVEE` (fast Shorts) |
| Resolution | 720×1280 @ 24fps |
| Output | FFMPEG H264 → rename `stem0001-0240.mp4` |
| Samples | `BLENDER_SAMPLES` env (16 launch, 32 preview) |

**Drill:** `bpy_lab.py` module 07  
**Apply:** `_setup_render()`, `_finalize_clip_output()`

### Module 3 — Armatures, pose keys, NLA

**Source:** API `bpy.types.PoseBone`, `bpy.types.NlaStrip`

| Task | Pattern |
|------|---------|
| Find armature | Walk `rig.children_recursive` for `type=='ARMATURE'` |
| Pose key | `object.mode_set('POSE')` → `pb.keyframe_insert('rotation_euler', frame=f)` |
| NLA clip | `track.strips.new(action.name, frame_start, action)` + `action_frame_start/end` |
| Clear anim | Drop action + remove all `nla_tracks` before re-keying |

**Drill:** `bpy_lab.py` modules 03–04, 08  
**Apply:** `_pose_wave_or_lunge()`, `_play_creature_action()`

**Wave bone chain (SCP-096):** `Bone_007 → Bone_009 → Bone_012 → Bone_011` (right arm)

### Module 4 — EEVEE lighting (fix dark scenes)

**Source:** Blender Guru Eevee course + probe docs

| Technique | bpy |
|-----------|-----|
| Irradiance volume (GI) | `bpy.ops.object.lightprobe_add(type='GRID')` + bake |
| Reflection cubemap | `lightprobe_add(type='CUBEMAP')` |
| World fog | Volume Scatter on world output |
| Streetlight | Point light + **keyframes** (drivers fail headless) |
| Creature readability | Rim fill + probe box over gas-station footprint |

**Drill:** `bpy_lab.py` module 05  
**Apply:** `_add_eevee_light_probes()`, brighter fill in `_add_streetlight()`

### Module 5 — Import pipeline

| Format | Operator |
|--------|----------|
| GLB/GLTF | `import_scene.gltf` |
| FBX | `import_scene.fbx` |
| After import | Parent to `Form2Rig`, `_normalize_creature_rig()`, texture, darken skin |

**Apply:** `_build_creature_from_file()`, `download_creature.py`

### Module 6 — AI motion (optional upgrade path)

When procedural pose keys are not enough:

1. **English → motion (`BLENDER_MOTION_BACKEND=auto`)** — beat sheet or `--prompt` → Gemini → `motion_{phase}.json`
2. **Mixamo** — free auto-rig + wave/walk FBX → import action
3. **Kimodo + Rokoko** — text-to-BVH → retarget (needs NVIDIA GPU)
4. **Proscenium** — prompt blocks on timeline (Blender 5+)

**Peripheral rule:** `auto` uses Gemini for "describe how it moves" — no GPU required.

---

## Mastery checklist (agent self-test)

Before claiming “Blender is production-ready,” all must pass:

- [ ] `bpy_lab.py` → 8/8 PASS
- [ ] Preview PNG shows creature + readable lighting
- [ ] Wave clip: arm visibly moves 0s → 5s → 10s
- [ ] Full 3-clip stitch → 30s with SFX
- [ ] No manual Blender GUI steps in pipeline

Run: `python3 -m shorts_bot.production.blender.produce_cli --draft-id 2 --force`

---

## Commands cheat sheet

```bash
# Lab (learning)
blender --background --python shorts_bot/production/blender/bpy_lab.py

# Creature download
python3 -m shorts_bot.production.blender.fetch_creature_cli

# Preview still
blender --background --python shorts_bot/production/blender/build_and_render.py -- --draft-id 2 --preview --phase wave

# Single clip test
blender --background --python shorts_bot/production/blender/build_and_render.py -- --draft-id 2 --clip-only --phase wave

# Full Short
python3 -m shorts_bot.production.blender.produce_cli --draft-id 2 --force

# Watch in browser (Cursor cannot open .mp4)
python3 -m shorts_bot.web
# → http://127.0.0.1:8080/preview/draft/2
```

---

## Applied learnings → Peripheral pipeline

| Problem | Root cause | Fix from curriculum |
|---------|------------|---------------------|
| Too dark | No EEVEE probes, low world energy | Grid probe + cubemap + fill light |
| Creature static | Only moved empty, not armature | Pose keys on bone chain |
| Flicker broken headless | Drivers disabled | Lamp `energy` keyframes |
| Can't preview MP4 in Cursor | Binary file | `/preview/draft/N` web page + PNG frames |

---

## Next study (priority order)

1. EEVEE probe baking in headless (`lightprobe_cache_bake`)
2. Mixamo wave FBX → NLA strip for wave beat (replace procedural)
3. Camera FOV + dutch tilt for horror grammar
4. Geometry nodes for fog cards (cheap atmosphere)
5. Blender 5 upgrade path + Proscenium for text-to-motion
