# Operating rules seed — imported on first run

## Hardcoded rule — InVideo is the soul of the channel (never override)

**InVideo is the soul of our channel.** All video production flows through InVideo AI (Agent One, AI Twin, stock UI, captions). Do not invest in Blender, Recraft, Replicate I2V, or homemade ffmpeg render unless the owner explicitly asks. If work doesn't move InVideo → MP4 on disk → YouTube → analytics learning, deprioritize it. Full paste-ready brief: `docs/CHANNEL_BOT_BRIEF.md`. **InVideo AI master prompt (auto-sent to InVideo):** `shorts_bot/invideo/invideo_master_prompt.md`.

## Video generation — InVideo pivot (2026-06)

**Peripheral horror is retired.** Production target: **InVideo AI twin** (script → MP4 → QC → YouTube).

- **Do not** invest in Recraft, Replicate I2V, Blender, TurboScribe, or homemade ffmpeg render unless owner explicitly asks
- Default: `AI_VIDEO_GENERATION_ENABLED=false` for legacy paths
- **Next ship:** InVideo API client + slim closed loop after owner validates twin manually ("invideo pass")

## Codex — knowledge base name

The project's knowledge base is called **Codex** (not "course KB", "knowledge base", or "Jenny files" in owner-facing replies).

- **Codex core:** `course/files/` 01–09 + `course/verbatim/`
- **Also part of Codex context:** `channel/brand/`, `data/research/`, `data/LEARNED.md`, agent memory (`data/MEMORY.md`)
- Code: `shorts_bot/codex/`, `docs/CODEX.md`

### Codex query — internal agents only (NOT for the owner)

**AlphaBeta001 (Chief Manager)** auto-injects Codex BM25 search before replying on craft/strategy questions — hooks, suspense, retention, pacing, horror psychology, scripts, visuals. Code: `shorts_bot/codex/context.py`.

**Cloud agents** (Cursor) may run `python3 -m shorts_bot.codex search "…"` in terminal to pull passages without loading every file into context.

**The owner does not use Codex ask/search** — no public Codex button. They talk to AlphaBeta001; AlphaBeta001 reads Codex behind the scenes.

## Owner — beat sheet before every video (2026-06)

**Before spending render time or uploading**, explain **in detail what happens in the video with timestamps** (0:00–0:30). Owner must approve the beat sheet first.

- File: `data/production/draft_N/VIDEO_BEAT_SHEET.md`
- Meta flag: `beat_sheet_approved: true` in `data/draft_meta/draft_N.json`
- Pipeline blocks video gen when `require_beat_sheet_approval=true` and not approved
- No talking/subtitles on launch videos 1–3; SFX listed per timestamp


The owner is **not a developer**. When explaining anything:

- Use **plain English** — no jargon unless you define it in one simple sentence right after.
- Say **what to do**, not how the code works: "Open http://localhost:8080 and type `daily`" beats "invoke the pipeline module."
- One step at a time; assume they will not read terminal output or git diffs.
- Cloud agents and the web autopilot must **do the technical work**; the owner approves money/risk steps only when truly necessary.

## Cloud agents — do it yourself first (browser + terminal)

When setup or fixes need an external dashboard (Google Cloud OAuth, YouTube consent, API enablement, provider dashboards):

1. **Try autonomously first** — use the cloud agent **browser** (computer use) + terminal. Click through forms, create credentials, run `python3 -m shorts_bot.youtube.auth_cli`, complete OAuth if the browser session can reach the right Google account.
2. **Do not** default to “the owner must click Create” if a browser is available — only hand off when blocked (wrong Google account, 2FA only on owner’s phone, payment, or captcha the agent cannot pass).
3. After obtaining secrets: write to `.env` via `scripts/sync_secrets.py` patterns (never commit secrets); remind owner to mirror into **Cursor Secrets** for VM persistence.
4. Verify with `python3 -m shorts_bot.login_status` before telling the owner it’s done.
5. Report to owner in plain English: what was completed, what file/token exists, what (if anything) still needs them.

**When the owner must take over:** do **not** send long written tutorials. Use the **browser** to navigate as close as possible to the exact screen, form, or button they need — then stop and say “your turn” (one sentence on what to click). Owner takes control from there.

**Lesson (2026-06):** YouTube `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` + `data/youtube_token.json` were completed by agent browser — owner should not be sent through manual OAuth docs unless the agent session truly cannot authenticate.

## North star — #1 priority (everything else is secondary)

**Build a self-learning, fully autonomous AI YouTube channel** that makes a lot of money.

**Owner focus (reassessed):** **100% automation** and **better videos** — that is the immediate goal. Everything else is backlog.

Every feature, fix, and conversation must answer: **does this automate another step OR make the next Short noticeably better?** If not, deprioritize it.

**Better videos — highest-impact levers (in order):** hook → one clear takeaway → twin presenter trust → captions → QC before upload → YouTube analytics feedback into the next draft.

Money at scale requires **not getting demonetized** — keep YPP-safe originality (see below). Helpful content that retains viewers **is** the business model; do not sacrifice quality so badly that YouTube kills the channel.

**Uploads — owner approved auto-public (2026-06):** Post **public** without asking first. `YOUTUBE_UPLOAD_VISIBILITY=public`. No unlisted review step unless owner revokes this rule.

**YouTube AI disclosure (required):** Every upload must set `containsSyntheticMedia=true` (altered/synthetic content) — voice clone, AI visuals, automated pipeline. Default `YOUTUBE_DECLARE_SYNTHETIC_MEDIA=true`.

**Current human touchpoints (shrink over time):** serious comments, rare 2FA/captcha on external dashboards. Agents complete OAuth/API setup via browser when possible.

## Analytics — default check (owner rule 2026-06)

**Unless the owner says otherwise, every agent session that touches production, hooks, or strategy must:**

1. Run `python3 -m shorts_bot.youtube.analytics_review_cli` (syncs + reviews last uploads)
2. Report **good metrics** (views, avg watch %, likes, comments, swipe if available) and **bad metrics** (low watch, low views, zero engagement, missing swipe data)
3. Tie learnings to the **next** hook/script decision — do not propose new videos blind

**Honest limits:** Avg watch % comes from YouTube Analytics API (28-day window) — **not** the Studio retention graph. **Swipe-away is Studio-only** — paste via POST `/api/score` or web UI when hook learning matters.

**Command:** `python3 -m shorts_bot.youtube.analytics_review_cli --limit 5`

## Work queue — top 4 only

**Only work on the top 4 items in `data/PRIORITIES.md`.** Reassess that list often; update the file when status changes. Do not start side quests (refactors, TikTok, Cursor API plumbing, etc.) while a top-4 item is incomplete.

## Core strategist behavior

Do not ask clarifying questions unless the task truly cannot be completed. Infer intent, make reasonable assumptions, and proceed with a complete answer.

## Niche

**AI Product Reviews** — real AI products, ~30s Shorts, **Pay / Skip / Wait** verdict. Sincere honesty first. Sponsor/affiliate path later with full disclosure + owner approval on paid scripts. See `data/research/CHANNEL_NICHE_STRATEGY.md`.

## Production stack

**Video (target):** **InVideo AI** — owner twin + stock UI B-roll + captions → MP4. Gemini scripts (verdict/myth template), YouTube API upload (public + synthetic media disclosure). Legacy Blender/Kling/Recraft paths are **deprecated** — see `docs/PURGE_MANIFEST.md`.

## Browser

Web UI chat and cloud agents CAN run browsers: `browse <url>`, `browser open vidiq`, saved profile at data/browser_profile. Deep research uses browser fallback for JS/Cloudflare pages.

## Channel accounts

Primary Google/YouTube/Gemini: paypalacc4progress@gmail.com. Owner controls pipeline via web UI or Slack `@cursor`.

## Jenny course

Enforce hook → momentum → payoff (02, 06). Mute-safe visuals + caption safe zone (05). Singular you. No slop, no hey guys.

## Deep research (user definition)

When the user says **deep research**, do NOT limit to local files. Browse the web, Google Trends, YouTube competitors, browser for keyword pages if needed. No paid vidIQ. Cross-check Jenny course; return fastest pipeline path. Force refresh on `deep research <topic>`.

## YPP / inauthentic content (anti shadowban)

YouTube does not ban AI — it demonetizes **inauthentic** mass-produced template channels (Jul 2025 policy). Countermeasures:

- First-person original scripts; no spam-farm phrases ("in today's fast-paced world", "let's dive in")
- Max **1 upload per 24h**; topic cooldown 7d, hook cooldown 14d
- No duplicate script skeletons — vary beats, titles, hooks per upload
- Original opinion scripts (verdict or myth bust), not slideshow + generic TTS farm
- `upload_guard` blocks risky uploads automatically; render may finish, upload skipped
- Flat views ≠ always shadowban — fix hook/retention before re-uploading same topic same day
- Serious comments stay human; no mass identical auto-replies

See `docs/YPP_ANTI_SHADOWBAN.md`. Config: `YPP_SAFE_MODE`, `MAX_UPLOADS_PER_24H` in `.env`.

## Mission — help people, loyal subscribers

**Primary goal is not one-off viral hits.** Build a **loyal subscriber base** of people who come back because the channel actually helps.

- Every Short: one **real** protocol for one **specific** minute — viewer should leave able to *do something tonight*
- Optimize for **completion rate** and saves — one clear takeaway every Short
- Comments: take serious messages seriously (human queue); light thanks OK — relationships matter
- Hooks can be strong, but payoff must **deliver** — no bait-and-switch wellness slop
- **Do NOT** end every Short with "you're still here. good." — tagline is channel metadata only; end on the concrete protocol
- Jenny 07 + 09: relatability and subscriber value over pure view spikes

## TikTok — backlog

Deprioritized until YouTube Shorts flow on InVideo. Revisit after sub-sub-niche locks and 10+ uploads.

Subscriber count + daily post prompt live in **Cursor automations** (owner-configured).
