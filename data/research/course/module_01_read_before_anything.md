# Read Before Anything
## Rules & Violations

Four rules that govern everything, then a full list of what gets your account banned.

## The 4 Rules

1. Disclose all videos as AI generated.
2. Only post 8-10 times per day until your account reaches Platinum Tier.
3. Go through all systems prior to starting. Do not skip steps.
4. Watch the brief video guides to see the exact workflow before you post anything.

## Video Do's

- Highly legible text
- Correct scale of product
- Matching lighting between product and environment
- Product not moving
- Unique environments
- Arc camera movement around the product at a reasonable speed
- Product in a non-cluttered environment

## Video Don'ts — Violation Triggers

⚠️ Compiled from months of trial and error. If you see any of these — regenerate immediately. Do not post.

- Moving water
- Moving fire
- Steam
- Dirt, sand, or powder
- Pulsing light
- Electronic screens with movement
- Mismatching lighting between product and environment
- Same lighting as the TikTok Shop listing image
- Hieroglyphic or illegible text
- Warped or mis-scaled product sizing
- Humans or human appendages
- Living beings — pets or animals
- Overly moving foliage
- Moving products
- Mis-colored products
- Supplement or beauty product boxes
- Peptides
- Weight loss products with claims on packaging
- Cluttered environments
- Product not in frame 80%+ of video
- Product not entirely in frame during image generation
- Unrealistic environments (cartoon, spaceship, abstract)
- Static camera movement
- Exaggerated human bobbing or movement
- Camera movement in only 1 axis
- Same environment as the listing image
- Other brand titles in frame
- Prices or retail messaging in background
- Mirrors or human reflections
- Levitating products
- Physics-breaking product orientation

## Posting Do's & Don'ts

### ✓ Do

- Use hashtags provided by brands or for seasonal promotion
- Use sounds and text that are evergreen
- On-screen text that contrasts the environment in color
- Product is 90% of the video frame

### ✕ Don't

- Do NOT turn on Ad Authorization on all videos individually. This is only required when a brand requests a spark code for a specific video.
- Videos under 7 seconds
- Using sounds that say "Triple Discount," "Double Discount," "Flash Sale," "Coupon Glitch," or anything that may not be true now or in the future
- Inappropriate language in your on-screen text
- Inappropriate language or visuals in the videos themselves
- Posting any sooner than 30 minutes apart
- Posting more than 30 times a day
- Posting the same product more than once in a day

---

## Bot enforcement (mandatory)

Before **every** upload, the factory runs Module 1 QC (`shorts_bot/tiktok_shop/module1_qc.py`).

- **Zero tolerance** for any Video Don't or Posting Don't above.
- Upload is **blocked** until violations = 0 (regenerate video if needed).
- CLI: `python3 -m shorts_bot.tiktok_shop.factory_cli qc --video PATH --product NAME --caption "..."`
- No skip unless owner explicitly disables `MODULE1_QC_ENABLED` in `.env` (emergency only).
