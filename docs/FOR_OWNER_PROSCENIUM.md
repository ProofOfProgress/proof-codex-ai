# Proscenium — real Blender AI for creature motion

**Stop using Gemini/Cursor to guess bone angles.** Use **Proscenium** — an addon made for Blender that turns English into real animation on your rig.

---

## What Proscenium is

| | Our old way (delete this) | Proscenium |
|--|---------------------------|------------|
| Who moves the character | Gemini writes numbers → often stiff/wrong | **Kimodo motion AI** inside Blender |
| Where it runs | Cloud scripts, no real Blender artist | **Inside Blender 5** — you type, it animates |
| Your weak PC | Cloud render but motion still bad | Motion runs on **Animatica Cloud** (their servers, not yours) |
| You say | (hope the bot understood) | `"slow creepy wave, wrist bent backward"` → **Generate Motion** |

- **Free account:** [animatica.ai](https://animatica.ai)
- **Addon (free, open source):** [Proscenium on GitHub](https://github.com/animatica-ai/proscenium-blender)
- **Needs:** Blender **5.0+** (not 4.x) on a machine that can open Blender — motion itself is cloud, so GPU optional for generation

---

## One-time setup (you, ~15 minutes)

### Step 1 — Install Blender 5

Download **Blender 5.0 or newer** from [blender.org](https://www.blender.org/download/) on the computer that will run Blender (can be a different PC than Cursor if yours is slow).

### Step 2 — Install the addon

On that same machine, in a terminal (or ask the agent to download for you):

```bash
bash scripts/install_proscenium.sh
```

Then in Blender:

1. **Edit → Preferences → Add-ons → Install…**
2. Pick the zip from `channel/tools/proscenium/proscenium-blender-0.4.0.zip`
3. Enable **Proscenium — AI Motion Generation**

### Step 3 — Sign in

1. Create free account at [animatica.ai](https://animatica.ai)
2. In Blender: **Edit → Preferences → Add-ons → Proscenium** → sign in
3. In the 3D view press **N** → **Proscenium** tab → **Connect**

---

## How to animate draft #2 (gas station / SCP wave)

1. Open Blender 5
2. **File → Import** our creature: `channel/assets/creatures/scp_096/scp_096.fbx` (or GLB)
3. Select the **armature** (skeleton)
4. In **Proscenium** panel:
   - Target armature = your SCP rig
   - Timeline prompt block: *"slow uncanny wave with right arm, wrist bent backward, not friendly"*
   - Click **Generate Motion**
   - Preview → **Accept** or **Reject** and try again
5. **File → Export → FBX** (or save `.blend`) into:
   `channel/assets/motion_exports/draft_2_wave.fbx`

Tell the agent: **"Proscenium export is ready for draft 2 wave"** — the bot will use that file on the next cloud render (no Gemini).

---

## If your PC is too slow for Blender 5

| Option | What to do |
|--------|------------|
| **A** | Use any other PC once (library, friend) — only for Proscenium export, not rendering |
| **B** | **Kimodo Bridge** ($5) — only if you get an **NVIDIA GPU** PC (8GB+ VRAM); runs local, no cloud |
| **C** | Skip Blender for now — go back to **Kling** for video (`VIDEO_BACKEND=kling`) until you have Blender 5 somewhere |

---

## What the cloud bot does now

- **No Gemini motion** — procedural wave/lunge only until you export Proscenium FBX
- When FBX lands in `channel/assets/motion_exports/draft_2_wave.fbx`, the next **`blender render 2`** uses it automatically
- Optional: set `BLENDER_MOTION_BACKEND=proscenium_fbx` in `.env` to refuse procedural fallback
- Cloud still stitches SFX + uploads when you approve
- AlphaBeta will ask for Proscenium exports instead of faking animation with AI text

---

## Links

- [Proscenium install docs](https://github.com/animatica-ai/proscenium-blender/blob/main/docs/installation.md)
- [Video tutorials (YouTube playlist)](https://www.youtube.com/watch?v=Wc349qOwjfM&list=PLAJ2UfUYhFQKZpFS8eh1eGUWJ0PAys1n1)
- [Animatica product page](https://animatica.ai)
