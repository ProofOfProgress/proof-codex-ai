# Cloud motion for Blender (no Animatica waitlist)

**Locked stack:** Cloud service makes motion → you drop **FBX** in the repo → **cloud bot** EEVEE-renders in Blender. Your PC never renders. **No Kling. No local GPU motion.**

Animatica / Proscenium is still the long-term pick — use the options below until early access opens.

---

## Pick one (all cloud)

| Service | How it works | Sign-up | Best for draft #2 |
|---------|--------------|---------|-------------------|
| **[Mixamo](https://www.mixamo.com)** ⭐ start here | Browser — pick preset animation, download FBX | Free Adobe account | Wave, creepy walk, lunge presets |
| **[Uthana](https://uthana.com)** | Text or video → motion; Blender plugin + API | “Start for free” on site | English prompts like Proscenium |
| **[DeepMotion](https://www.deepmotion.com/)** | Upload video or text → 3D animation | Free tier to try | Film yourself doing a slow wave |
| **[Plask](https://plask.ai/)** | Video → mocap in browser | Free tier | Same — act out the wave on phone video |

All export **FBX** (or GLB). Our bot imports either.

---

## Fastest path tonight: Mixamo (15 min)

1. Go to https://www.mixamo.com — sign in with Adobe (free).
2. **Upload Character** → try `channel/assets/creatures/scp_096/scp_096.fbx`.  
   If Mixamo rejects it, upload any **humanoid** FBX — motion still works; we match camera in Blender.
3. Search and preview:
   - **open clip:** “zombie walk” or “creepy walk”
   - **wave clip:** “waving” or “zombie idle” (pick the uncanny one)
   - **lunge clip:** “running” or “zombie attack” (short, aggressive)
4. For each animation, set **Overdrive** / **Character Arm-Space** until it looks wrong enough for horror.
5. Download **FBX**, **Without Skin**, **30 FPS**.
6. Rename and put in the project:

```
channel/assets/motion_exports/draft_2_open.fbx
channel/assets/motion_exports/draft_2_wave.fbx
channel/assets/motion_exports/draft_2_lunge.fbx
```

7. Tell the agent: **“Cloud motion FBX ready for draft 2”** → cloud re-render.

---

## If you want text prompts (Proscenium-like): Uthana

1. https://uthana.com → **Start for free**
2. Install **Blender plugin** from their site (Blender 5.1 OK)
3. Text prompt example: *“slow uncanny wave, right arm, wrist bent backward, horror”*
4. Export FBX → same `motion_exports/` folder names as above

Optional later: agent can call Uthana API with `UTHANA_API_KEY` for full automation (not wired yet).

---

## Video reference path: DeepMotion or Plask

Good when text presets feel too “normal”:

1. Film yourself on your phone — slow wave, then a lunge toward camera (10 seconds each).
2. Upload to DeepMotion or Plask in the browser.
3. Export FBX → `motion_exports/` → tell the agent.

---

## What the cloud bot does (unchanged)

```
Cloud motion site → FBX files in motion_exports/
Cloud VM → Blender EEVEE → 3×10s clips → stitch → horror SFX → upload
```

Procedural stiff animation is only used when **no FBX** is on disk.

---

## When Animatica lets you in

Switch to Proscenium — same FBX folder, better control on your SCP armature. See `docs/FOR_OWNER_PROSCENIUM.md`.
