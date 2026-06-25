# Channel ops playbook — AI Product Reviews

**Niche:** Real AI products → honest Pay / Skip / Wait (~30s)  
**Video:** InVideo (you) → MP4  
**Publish:** YouTube + TikTok  
**Clone / Facebook:** paused

---

## Who does what

| Step | Agent (me) | You |
|------|------------|-----|
| Pick product + research price/features/catches | ✅ | Optional: comment "review X" |
| Write script (hook + verdict) | ✅ | Approve or say "shorter" |
| Transcribe winning competitor Shorts | ✅ | Send links when you find them |
| Generate video in InVideo | ❌ | Paste script → Generate → Export MP4 |
| Upload YouTube | ✅ (one command) | First-time Google OAuth only |
| Upload TikTok | ✅ (one command) | **Today:** TikTok developer app + OAuth (15 min) |
| Read analytics / learn hooks | ✅ | Glance at views if you want |
| Daily topic queue | ✅ | Nothing on bad days |

**Your minimum day:** export MP4 from InVideo → tell agent "upload draft N" (or run one command).

---

## Phase 0 — Today (TikTok hookup)

**You (required once):**

1. Create TikTok developer app → Content Posting API → Direct Post  
2. Add `TIKTOK_CLIENT_KEY` + `TIKTOK_CLIENT_SECRET` to Cursor Secrets  
3. Run `bash scripts/install.sh`  
4. Follow `docs/FOR_OWNER_TIKTOK_SETUP.md` — OAuth connect  

**Agent (done / in repo):**

- `python3 -m shorts_bot.tiktok.auth_cli` — connect  
- `python3 -m shorts_bot.tiktok.upload_cli` — post MP4  
- YouTube upload already works  

**Check everything:**

```bash
python3 -m shorts_bot.login_status
```

---

## Phase 1 — First video (proof loop)

1. **Agent:** script for product #1 (e.g. ChatGPT Plus)  
2. **You:** InVideo → paste script → Generative Ultra or stock UGC → export MP4  
3. **Save to:** `data/production/draft_1/final_short.mp4`  
4. **Upload YouTube:**

```bash
python3 -m shorts_bot.production.upload_canonical_cli --draft-id 1 \
  --video data/production/draft_1/final_short.mp4
```

5. **Upload TikTok:**

```bash
python3 -m shorts_bot.tiktok.upload_cli data/production/draft_1/final_short.mp4 \
  --title "ChatGPT Plus honest review — Pay or Skip #aitools #chatgpt"
```

6. **Agent:** note hook + product in learning log; tomorrow's topic picks from outliers

---

## Phase 2 — Daily rhythm (low energy)

**Agent overnight / when you ask `daily`:**

- Research next AI product (no purchase — pricing page + Reddit + free tier)  
- Write script  
- Store draft in DB  

**You when you have 20–30 min:**

- InVideo export  
- `upload draft N` to both platforms  

**Target:** 5–7 Shorts/week minimum. Daily when energy allows.

---

## Phase 3 — Increase breakout odds (Jenny + research)

**Weekly (agent):**

1. Transcribe 5 outlier Shorts from small AI review channels  
2. Extract hook patterns → update script templates  
3. Sync YouTube analytics → `avoid:` / `repeat:` rules  

**Jenny rules that still apply:**

- Idea must hook in line 1 (`course/files/02_idea_hook_viral.md`)  
- Payoff = verdict before end (`06_story_retention_payoff.md`)  
- Outlier mining (`04_outlier_idea_generation.md`)  
- Swipe-away / retention = fix hooks, not blame algorithm (`09_growth_cta_analytics.md`)  

**Codex search (agent only):**

```bash
python3 -m shorts_bot.codex search "hook retention payoff short"
```

---

## Phase 4 — Automation (after 5+ videos ship)

- InVideo API when you say **invideo pass**  
- One command: script → (InVideo) → YouTube + TikTok  
- Analytics learning auto-tunes topics  

Not before manual loop works.

---

## Money discipline

| Tool | When to pay |
|------|-------------|
| InVideo free | Now — test |
| InVideo ~$20/mo | After 1 video you'd post publicly |
| InVideo ~$100/mo | Daily posting + credit limits |
| Cursor Pro+ | Job income covers it; downgrade if needed |
| TikTok API | Free |

---

## Commands cheat sheet

```bash
# Status
python3 -m shorts_bot.login_status
python3 -m shorts_bot.tiktok.auth_cli status
python3 -m shorts_bot.youtube.auth_cli status

# Draft + script (agent or you)
python3 -m shorts_bot.production.daily_cli --no-upload   # script only

# Upload
python3 -m shorts_bot.production.upload_canonical_cli --draft-id N --video PATH
python3 -m shorts_bot.tiktok.upload_cli PATH --title "caption #tags"

# Research
python3 -m shorts_bot.codex search "hook outlier short form"
```

---

## Not doing now

- InVideo twin clone  
- Facebook API  
- Homemade Blender/Recraft render  
- Full autopilot before first TikTok + YouTube pair ships  
