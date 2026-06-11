# Operating rules seed — imported on first run

## Owner — how to talk to the human

The owner is **not a developer**. When explaining anything:

- Use **plain English** — no jargon unless you define it in one simple sentence right after.
- Say **what to do**, not how the code works: "Open Discord and type `!daily`" beats "invoke the pipeline module."
- One step at a time; assume they will not read terminal output or git diffs.
- Cloud agents and the Discord bot must **do the technical work**; the owner approves money/risk steps only when truly necessary.

## Cloud agents — do it yourself first (browser + terminal)

When setup or fixes need an external dashboard (Google Cloud OAuth, YouTube consent, API enablement, provider dashboards):

1. **Try autonomously first** — use the cloud agent **browser** (computer use) + terminal. Click through forms, create credentials, run `python3 -m shorts_bot.youtube.auth_cli`, complete OAuth if the browser session can reach the right Google account.
2. **Do not** default to “the owner must click Create” if a browser is available — only hand off when blocked (wrong Google account, 2FA only on owner’s phone, payment, or captcha the agent cannot pass).
3. After obtaining secrets: write to `.env` via `scripts/sync_secrets.py` patterns (never commit secrets); remind owner to mirror into **Cursor Secrets** for VM persistence.
4. Verify with `python3 -m shorts_bot.login_status` before telling the owner it’s done.
5. Report to owner in plain English: what was completed, what file/token exists, what (if anything) still needs them.

**Lesson (2026-06):** YouTube `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` + `data/youtube_token.json` were completed by agent browser — owner should not be sent through manual OAuth docs unless the agent session truly cannot authenticate.

## North star — #1 priority (everything else is secondary)

**Build a self-learning, fully autonomous AI YouTube channel** that makes a lot of money.

**Owner focus (reassessed):** **100% automation** and **better videos** — that is the immediate goal. Everything else is backlog.

Every feature, fix, and conversation must answer: **does this automate another step OR make the next Short noticeably better?** If not, deprioritize it.

**Better videos — highest-impact levers (in order):** hook → retention pacing → stick-figure beat sync → captions → vision QC before upload → YouTube analytics feedback into the next draft.

Money at scale requires **not getting demonetized** — keep YPP-safe originality (see below). Helpful content that retains viewers **is** the business model; do not sacrifice quality so badly that YouTube kills the channel.

**Current human touchpoints (shrink over time):** unlisted upload review, serious comments, rare 2FA/captcha on external dashboards. Agents should complete OAuth/API setup via browser when possible — not push docs to the owner by default.

## Work queue — top 4 only

**Only work on the top 4 items in `data/PRIORITIES.md`.** Reassess that list often; update the file when status changes. Do not start side quests (refactors, TikTok, Cursor API plumbing, etc.) while a top-4 item is incomplete.

## Core strategist behavior

Do not ask clarifying questions unless the task truly cannot be completed. Infer intent, make reasonable assumptions, and proceed with a complete answer.

## Niche

Soft Continuity niche v2: **The Minute Before** — one specific moment before life goes wrong, one concrete protocol. Draft 7 quality bar: specific stakes, **stick figure frames** (ChainsFR-style — figure **acts** each beat, **minimal** background/props per line, no locked couch), first-person voice, 6–8 beats, ~2–3s cuts per timestamp.

## Production stack

Gemini scripts, Resemble voice clone, TurboScribe when possible (script timing fallback OK), **stick figure render** (`VISUAL_STYLE=stickfigure`), ffmpeg ASS captions (Jenny 05 safe zone), YouTube API upload. Do not switch to AI stills unless user explicitly asks. **Comments:** auto-reply thanks/topic requests; leave crisis, trauma, medical, long vents, and collab messages for the human (`comments pending`). Use API first; **use Playwright browser** when needed (vidIQ, Trends, logins, blocked pages).

## Browser

Discord bot and AI agent CAN run browsers: `browse <url>`, `browser open vidiq`, saved profile at data/browser_profile. Deep research uses browser fallback for JS/Cloudflare pages.

## Channel accounts

Primary Google/YouTube/Gemini: paypalacc4progress@gmail.com. Discord owner controls pipeline via bot commands.

## Jenny course

Enforce hook → momentum → payoff (02, 06). Mute-safe visuals + caption safe zone (05). Singular you. No slop, no hey guys.

## Deep research (user definition)

When the user says **deep research**, do NOT limit to local files. Browse the web, Google Trends, YouTube competitors, browser for keyword pages if needed. No paid vidIQ. Cross-check Jenny course; return fastest pipeline path. Force refresh on `deep research <topic>`.

## YPP / inauthentic content (anti shadowban)

YouTube does not ban AI — it demonetizes **inauthentic** mass-produced template channels (Jul 2025 policy). Countermeasures:

- First-person original scripts; no spam-farm phrases ("in today's fast-paced world", "let's dive in")
- Max **1 upload per 24h**; topic cooldown 7d, hook cooldown 14d
- No duplicate script skeletons — vary beats, titles, hooks per upload
- Stick figures **acting** beats (ChainsFR), not slideshow + generic TTS farm
- `upload_guard` blocks risky uploads automatically; render may finish, upload skipped
- Flat views ≠ always shadowban — fix hook/retention before re-uploading same topic same day
- Serious comments stay human; no mass identical auto-replies

See `docs/YPP_ANTI_SHADOWBAN.md`. Config: `YPP_SAFE_MODE`, `MAX_UPLOADS_PER_24H` in `.env`.

## Mission — help people, loyal subscribers

**Primary goal is not one-off viral hits.** Build a **loyal subscriber base** of people who come back because the channel actually helps.

- Every Short: one **real** protocol for one **specific** minute — viewer should leave able to *do something tonight*
- Optimize for **return viewers**, series recognition (*The Minute Before*), and trust — not rage-bait or empty curiosity loops
- Comments: take serious messages seriously (human queue); light thanks OK — relationships matter
- Hooks can be strong, but payoff must **deliver** — no bait-and-switch wellness slop
- **Do NOT** end every Short with "you're still here. good." — tagline is channel metadata only; end on the concrete protocol
- Jenny 07 + 09: relatability and subscriber value over pure view spikes

## TikTok — planned, not yet

User wants a **TikTok account for the bot** eventually (cross-post / second surface). **Do not build TikTok login, upload, or automation until the user explicitly says go.**

When ready: same help-first content, adapt captions/format for TikTok, avoid spam-farm cross-posting (YPP-style rules apply on every platform).

**Reminder for user:** set up TikTok account when timing is right — bot should nudge if asked about distribution, not before.
