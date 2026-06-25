# Self-learning loop (optional)

**Default: off.** Strategy comes from the **owner's paid course**, not analytics.

Enable only if the owner wants a secondary analytics loop: `SELF_TRAINING_ENABLED=true` in `.env`.

## What runs

1. **Score** — paste TikTok analytics (views, avg watch %, swipe/skip if available)
2. **RewardEngine** — reward / punish vs your channel baseline
3. **ImprovementProposer** — suggests hook/retention/editing tweaks (auto-approved when safe)
4. **Reflect loop** — writes episodes, validates rules, promotes strong rules to agent memory

Config: `SELF_TRAINING_ENABLED=true` (default), `AUTO_APPROVE_IMPROVEMENTS=true`.

## Score a clip (CLI)

```bash
python3 -m shorts_bot.learning.score_cli score \
  --label "Vitamin gummies clip" \
  --swipe 62 \
  --retention 38 \
  --views 2400 \
  --likes 90 \
  --reflect
```

## Score a clip (API)

With web running (`python3 -m shorts_bot.web`):

```bash
curl -s -X POST http://127.0.0.1:8080/api/score \
  -H 'Content-Type: application/json' \
  -d '{"video_label":"Vitamin gummies","viewed_vs_swiped_away":62,"retention_rate":38,"views":2400,"likes":90}'
```

Check status: `GET /api/learning/status`

## Feedback (approve / reject a concept)

```bash
curl -s -X POST http://127.0.0.1:8080/api/feedback \
  -H 'Content-Type: application/json' \
  -d '{"topic":"Generic unboxing hook","reason":"Too slow — product must show in first second","decision":"rejected"}'
```

Rejections become `avoid:*` rules; approvals become `repeat:*` rules for future clips.

## Where data lives

- SQLite: `data/shorts_bot.db` (analytics, rewards, improvements, learning episodes)
- Agent memory export: `data/MEMORY.md`
- Approved improvements log: `data/LEARNED.md`

## Code paths

| Piece | Path |
|-------|------|
| Reward scoring | `shorts_bot/rewards/engine.py` |
| Reflect + promote | `shorts_bot/learning/reflect.py` |
| Draft/clip feedback | `shorts_bot/learning/feedback.py` |
| Improvements | `shorts_bot/training/proposer.py` |
| Memory | `shorts_bot/memory/` |
