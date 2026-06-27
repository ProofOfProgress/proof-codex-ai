# Image generation — pay as you go (no subscription)

The bot can generate still images for **bubble wrap slides** and (later) **affiliate product stills**. You only pay per image — no monthly plan required.

---

## Pick one provider (both already wired in code)

| Provider | Billing | Best for | Sign up |
|----------|---------|----------|---------|
| **Fal.ai** (recommended) | Pay per image (~fractions of a cent on Flux Schnell) | Bubble wrap + fast tests | https://fal.ai/dashboard/keys |
| **Replicate** | Pay per run (add card, buy credits) | Same; you may already have a token | https://replicate.com/account/api-tokens |

**Do not use Kling for images** — Kling is **image → video** only (Module 5). Images = Module 4 / bubble wrap stills.

---

## Setup — Fal.ai (easiest)

### 1. Account

1. Open https://fal.ai  
2. Sign up → **Billing** → add a payment method (pay-as-you-go)  
3. **Dashboard → API Keys** → create key  

### 2. Cursor secrets

**Cursor → Cloud Agent → Secrets:**

| Secret | Type | Value |
|--------|------|--------|
| `FAL_API_KEY` | Runtime Secret | your Fal key |
| `IMAGE_PROVIDER` | Environment Variable | `fal` |

### 3. New agent run

Secrets load at agent start. After saving → **start a new cloud agent run**, then:

```bash
bash scripts/install.sh
python3 scripts/test_image_gen.py
```

You should get a test PNG under `data/tiktok_shop/bubble_wrap/_test/`.

---

## Setup — Replicate (alternative)

### 1. Account

1. https://replicate.com/account/billing — add payment method  
2. https://replicate.com/account/api-tokens — create token (starts with `r8_`)  

### 2. Cursor secrets

| Secret | Type | Value |
|--------|------|--------|
| `REPLICATE_API_TOKEN` | Runtime Secret | `r8_...` |
| `IMAGE_PROVIDER` | Environment Variable | `replicate` |
| `REPLICATE_IMAGE_MODEL` | Environment Variable | optional Flux model slug from Replicate catalog |

### 3. New agent run + test

Same as Fal: `bash scripts/install.sh` then `python3 scripts/test_image_gen.py`.

**Note:** If you get “Unauthenticated”, the token is wrong or expired — create a **new** token at Replicate and replace the secret.

---

## Use for bubble wrap slides

After test passes:

```bash
python3 scripts/make_bubble_wrap_slides.py --subject orange
```

That runs **one generation per slide** (no regen), saves prompts in the output folder, overlays captions from owner sample positions.

---

## Costs (rough)

- **Flux Schnell** (Fal or Replicate): on the order of **$0.003–0.01 per image**  
- Bubble wrap post = **2 images** → well under a few cents per post  
- No subscription — you stop paying when you stop generating  

---

## What the course uses (affiliate, later)

Module 4 uses **Higgsfield + NanoBanana** in the browser. The bot API path above is for **automation** (bubble wrap + future batch stills). Creative prompts still follow `PROMPT_BUILDER.md` / `BUBBLE_WRAP.md`.
