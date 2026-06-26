# Bubble wrap daily ops

**Phase:** 0 → ~1,000 followers per account (`BUBBLE_WRAP.md`)  
**Format:** 2-photo manual-swipe slideshow + Mackenzie sound

---

## One-time setup

```bash
bash scripts/install.sh
cp data/tiktok_shop/accounts.example.json data/tiktok_shop/accounts.json
python3 -m shorts_bot.tiktok_shop.accounts_cli validate
python3 -m shorts_bot.tiktok_shop.factory_cli status
```

Paste Zernio account ids if needed:

```bash
python3 -m shorts_bot.tiktok_shop.accounts_cli sync-zernio
```

---

## Sample images (owner Drive)

Download once (gitignored locally):

```bash
python3 -m gdown --folder \
  "https://drive.google.com/drive/folders/1drt1xcaakCDMQ2ABJsJpeOYW7XDnHqDB" \
  -O "data/research/course/_media/bubble_wrap/samples"
```

List a catalog pair:

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli bubble-sample --pair frog
```

---

## Post a test slideshow (private)

**Always `--private` for tests** — draft inbox via API often does not appear.

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli post-slideshow \
  "data/research/course/_media/bubble_wrap/samples/bubble wrap7.png" \
  "data/research/course/_media/bubble_wrap/samples/bubble wrap10.png" \
  --title "FROG BUBBLE WRAP ASMR" \
  --caption "#asmr #satisfying #bubblewrap #fyp" \
  --account bubble_1 \
  --private \
  --confirm
```

Then on the phone: open TikTok → **private posts** → add **Mackenzie sound** → publish or delete.

Sound: https://www.tiktok.com/music/original-sound-7418286946344340256

---

## Queue + batch

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli enqueue-slideshow \
  slide1.png slide2.png --title "HOOK TEXT" --account bubble_2

python3 -m shorts_bot.tiktok_shop.factory_cli post-slideshow-batch --max 3 --private --confirm
```

---

## Real posts (after testing)

1. Generate **unique** 2-slide pairs per account (Module 2 / ChatGPT workflow)  
2. Post **public** (omit `--private`) — still add Mackenzie sound manually in app  
3. Mix 1 vs 5–10 posts/day across 3–5 accounts until ~1k followers  

---

## When you hit ~1k

Switch to affiliate pipeline: EchoTik scout → Kling clip → Module 1 QC → public post queue.

See `data/PRIORITIES.md` and Modules 3–8 in `data/research/course/`.
