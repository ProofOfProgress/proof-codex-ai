# Blender self-reinforcement learning

**What it is:** Like Minecraft diamond-finding, but for **Blender render knobs**. The agent tries camera/mouth/light settings, **Gemini vision QC scores the clip**, then **nudges params** and tries again — no human clicking sliders each time.

This is **not** neural-net weight training. It is **trial → reward → update params → repeat**, stored in `data/production/draft_N/blender_rl/`.

---

## Run it (plain English)

```bash
python3 -m shorts_bot.production.blender.self_train_cli --draft-id 2 --trials 5
```

Each trial:
1. Renders the 3s micro jumpscare with a param set
2. Gemini vision QC scores it (0–10)
3. Issues like “too dark” or “mouth not red” **automatically bump** the matching knobs
4. Best trial wins → copied to `final_short.mp4` + saved as `best_params.json`

Watch progress: `data/production/draft_2/blender_rl/trials.jsonl`

Preview best: http://127.0.0.1:8080/preview/draft/2?file=final_short.mp4

---

## Knobs it learns (env vars)

| Param | What it controls |
|-------|------------------|
| `camera_z` | POV height |
| `face_scale` | How big the face is at lunge peak |
| `mouth_emissive` | Red glow inside mouth |
| `focal_mm` | Lens width (in-your-face) |
| `exposure` | Scene brightness |
| `samples` | EEVEE quality (slower = sharper) |

---

## Settings (`.env`)

```
BLENDER_SELF_TRAIN_ENABLED=true
BLENDER_SELF_TRAIN_TRIALS=5
BLENDER_SELF_TRAIN_TARGET_SCORE=7.5
BLENDER_SELF_TRAIN_SAMPLES=24
```

Stop early when score hits target. Use `--trials 3` for a quick pass.

---

## How it connects to self-learning

After a run, **`reflect_after_blender_rl`** writes:
- `applied:blender-draft-N` in training config (best params summary)
- A **learning episode** so AlphaBeta001 remembers what worked

YouTube analytics rewards still handle **upload performance**; this handles **render craft before upload**.

---

## vs full RL (Minecraft-style)

| Minecraft RL | Blender self-train |
|--------------|-------------------|
| Millions of game steps | 3–10 renders per session |
| Sparse diamond reward | Vision QC score every trial |
| Learn policy network | Learn **param vector** + heuristics from issue text |
| Needs GPU farm | One cloud VM + Gemini |

Future: bandit over param groups, preview-only frames for faster trials, auto-run after every `--force` render fail.
