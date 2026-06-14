# Blender-native AI bots (2026) — agent reference

**Owner rule:** Do **not** use Gemini or Cursor to invent bone rotations. Use a **Blender addon made for motion**.

---

## Pick list (animation / “make it move”)

| Tool | Made for | Motion quality | Weak PC? | Cost |
|------|----------|----------------|----------|------|
| **[Proscenium](https://github.com/animatica-ai/proscenium-blender)** ⭐ | Text → motion on **your armature** in Blender 5 | High (Kimodo cloud) | OK — AI runs on Animatica cloud; need Blender 5 UI only | Free account + free addon |
| **[Kimodo Blender Bridge](https://superhivemarket.com/products/kimodoblenderbridge)** | Same Kimodo model, **inside Blender 4+** sidebar | Highest (local) | **No** — needs NVIDIA 8GB+ VRAM | ~$5 addon + free Kimodo |
| **[OpenBlender TXT→RIG](https://pgcrt.github.io/)** | Text → humanoid + motion (generic dummy) | Medium | Heavy — local ComfyUI | Free addon |
| **3D-Agent / Blender MCP** | Modeling + general bpy via Claude | **Not** a motion specialist | Needs desktop Blender + MCP | Varies — still LLM, owner rejected |
| **Mixamo** | Pick preset (wave, walk) | Good for humans | Browser only | Free |

**Peripheral choice:** **Proscenium** — only tool that is (1) built for Blender, (2) text-to-motion on custom rigs, (3) cloud AI so owner GPU does not matter.

---

## Deprecated (do not use)

| Removed approach | Why |
|------------------|-----|
| `BLENDER_MOTION_BACKEND=gemini` | LLM guessing euler angles — stiff, not real animation |
| AlphaBeta `blender motion … \| prompt` → Gemini | Same problem — not a Blender animation product |
| Headless-only pose keys | OK as fallback until Proscenium FBX exists |

---

## Pipeline after Proscenium

```
Owner: Blender 5 + Proscenium → "slow creepy wave" → Accept → export FBX
Cloud bot: import action → EEVEE render clips → stitch → SFX → upload
```

Export path: `channel/assets/motion_exports/draft_{N}_{phase}.fbx`

Install addon zip: `bash scripts/install_proscenium.sh`

Owner doc: `docs/FOR_OWNER_PROSCENIUM.md`

---

## Requirements checklist

- [ ] Blender **5.0+** installed somewhere (not 4.0 on cloud VM today)
- [ ] Proscenium addon installed + Animatica sign-in
- [ ] SCP-096 armature selected in Proscenium
- [ ] Wave + lunge exported to `motion_exports/`
- [ ] Cloud render uses FBX — not Gemini
