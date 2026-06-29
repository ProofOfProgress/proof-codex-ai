---
name: visual-review
description: Gemini visual critique of Module 4 image or Kling render — feedback loop for prompt builder. Use after render when motion or quality looks off.
---

# /visual-review

Invoke **Video Visual Critic** — Gemini watches stills/frames and tells the **prompt builder** what to fix.

Requires **GEMINI_API_KEY**.

## Examples

```
/visual-review
Review data/tiktok_shop/clips/foo_loop.mp4 vs reference image — suggest prompt fixes

/visual-review
Is this Module 4 image ready for Kling? data/tiktok_shop/images/product.jpg
```

## Loop (CEO orchestrates)

1. **product-video-prompt-builder** → Kling prompt  
2. CEO → `factory_cli render`  
3. **video-visual-critic** (background) → `visual_feedback_cli review-and-suggest`  
4. If not good enough → handoff → **product-video-prompt-builder** → regen  
5. **module1-qc-runner** → upload gate (separate)

Docs: `docs/VISUAL_FEEDBACK_LOOP.md`
