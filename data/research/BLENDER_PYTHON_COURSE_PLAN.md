# Blender Python course — coding-first (agent syllabus)

**Owner ask (2026-06):** Learn Blender properly — find a course that shows the **coding side** a lot.

**Primary course (FREE, code-heavy):** [**Blender Python for Artists**](https://www.skool.com/cgpython/classroom/60a44c1e) — CG Python Academy on Skool.

**Intro video:** https://www.youtube.com/watch?v=KZAT7jElCRk

---

## Why this course (not random YouTube)

| Course | Cost | Coding depth | Verdict |
|--------|------|--------------|---------|
| **CG Python — Blender Python for Artists** | **Free** (Skool) | **Highest** — operators, panels, objects, shader/geo nodes, exercises | **PRIMARY** |
| Blender Studio — Scripting for Artists | €17/mo | High — copy UI → Python, batch automation | Secondary (paid) |
| Blender Guru EEVEE | Free | Low — artist clicks, not bpy | Visual craft only |
| Official API Quickstart | Free | Reference, not a course | Always open while coding |

CG Python is built for **writing scripts and add-ons**, not “click this button in the UI.” That matches our cloud pipeline (`build_and_render.py`, headless `blender --background --python …`).

---

## Course map (Skool classroom → our pipeline)

Work in order. After each part: run matching `bpy_lab` module + apply one fix to `build_and_render.py`.

| Part | CG Python topic | What you learn in code | Our drill | Apply to Peripheral |
|------|-----------------|------------------------|-----------|---------------------|
| **1 — Basics** | Variables, loops, functions | Python inside Blender text editor | `bpy_lab` 01–02 | `_mat()`, scene graph |
| **2 — First operator + panel** | `bpy.types.Operator`, `register()` | Custom tools like Blender buttons | (read + mirror patterns) | Future: “Re-render draft” operator |
| **2.5 — VSCode** | External editor + Blender | Same scripts we run headless on VM | `blender --background --python` | All production |
| **3 — Working with objects** | Location, rotation, scale, collections | Move cameras/creatures in code | `bpy_lab` 06, 09 | `scene_layout`, camera path |
| **4 — Custom operators + UI** | Menus, properties | Batch tools | — | Mixamo fetch CLI patterns |
| **5 — Nodes** | Shader + geometry nodes in Python | **Materials & textures in code** | `bpy_lab` 10 | Fix gas-station texture relink |
| **6 — Geometry** | Meshes, bmesh | Ground, pumps, trees procedural | `bpy_lab` 11 | Environment import + scale |

**YouTube extras (same instructor):**

- [Beginner Blender Python Scripting Practice](https://www.youtube.com/playlist?list=PLB8-FQgROBmmeCnCfuJEGzP0nH0u3tz7j)
- [Beginner Python for the Anxious CG Artist](https://www.youtube.com/playlist?list=PLjdX5s0F2DqZYcjKn2QIlNKorQ2E3Lws5)

---

## Official reference (always open)

| Doc | URL | Use when |
|-----|-----|----------|
| Python API Quickstart | https://docs.blender.org/api/current/info_quickstart.html | First week |
| API Overview | https://docs.blender.org/api/current/info_overview.html | Headless / register |
| Add-on Tutorial | https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html | Operators |
| `bpy.ops` vs data API | https://blender.stackexchange.com/questions/2848/why-avoid-bpy-ops | Performance |

**Headless rule (our stack):** `blender --background --python script.py -- --args`

---

## Secondary course (optional, official)

**Blender Studio — [Scripting for Artists](https://studio.blender.org/training/scripting-for-artists/)** (Sybren Stüvel, core Blender dev). Strong on “copy what the UI does into Python” and batch jobs. Paid subscription — use if we need deeper automation patterns after CG Python Part 4.

---

## Pass criteria (before claiming “we know Blender”)

1. CG Python Parts **1–3 + 5** complete (notes in `BLENDER_COURSE_PROGRESS.md`)
2. `bpy_lab.py` → **12/12 PASS** (includes texture + env drills)
3. Draft #2 preview PNG: gas station **readable**, creature **lit**, not grey block-out
4. One paragraph in progress log: what Part 5 (shader nodes) changed in our relink code

---

## Commands

```bash
# Lab after each course part
blender --background --python shorts_bot/production/blender/bpy_lab.py

# Progress log
cat data/research/BLENDER_COURSE_PROGRESS.md
```

**Visual craft** (after coding basics): Blender Guru EEVEE + LIGHTS ARE OFF refs — see `LIGHTS_ARE_OFF_BLENDER_REFERENCE.md`.
