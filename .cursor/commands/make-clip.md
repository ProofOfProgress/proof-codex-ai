Make one affiliate clip for TikTok Shop (Kling → pan loop → Module 6 caption → QC).

Product name from user message (or pick from scout list first).

1. Invoke `/video-pipeline` or run factory CLI.
2. `python3 -m shorts_bot.tiktok_shop.factory_cli make-clip --product "PRODUCT_NAME"`
3. Run QC; report pass/fail and file path to `*_final.mp4`.

Private test post only if user asks: `ZERNIO_TIKTOK_PRIVACY=SELF_ONLY` + `post --account affiliate_test --confirm`.
