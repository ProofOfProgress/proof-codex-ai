# Cursor secrets checklist

Add these in **Cursor → Cloud Agent → Secrets** (the **Cloud Agent** panel for this VM — **not** only Cursor IDE → Settings → Secrets).

On the VM, `bash scripts/install.sh` runs `scripts/sync_secrets.py` and copies them into `.env`.

**Check:** after install, `grep GOOGLE_CLIENT .env` must **not** show `your-client-id`. If it still does, run:

```bash
python3 -m shorts_bot.cloud_secrets
```

That shows which secret **names** Cursor sends to this cloud VM. If `GOOGLE_CLIENT_ID` says **In agent list: no**, the keys were saved somewhere else (wrong name, wrong agent, or IDE-only).

**Do not paste real values in chat or commit them to git.**

### Cursor secret types (dashboard dropdown)

| Type | Use for |
|------|---------|
| **Runtime Secret** | Passwords, API keys, tokens — sensitive |
| **Environment Variable** | Model names, enums, non-sensitive config |
| **Build Secret** | Dockerfile build only — **not used** for this project |

---

## Required — full Shorts autopilot

| Secret name | Cursor type | Value type | Example (filler) | Where to get it |
|-------------|-------------|------------|------------------|-----------------|
| `GEMINI_API_KEY` | Runtime Secret | API key (string, 39+ chars, starts `AIza`) | `AIzaSy________________________` | https://aistudio.google.com/apikey |
| `GEMINI_MODEL` | Environment Variable | Model slug (string) | `gemini-2.5-flash-lite` | Cheap OCR/scrape — Google AI Studio |
| `GEMINI_VISION_MODEL` | Environment Variable | Model slug (string) | `gemini-2.5-flash` | Module 1 QC + visual critic (smarter than lite) |
| `GEMINI_IMAGE_MODEL` | Environment Variable | Model slug (string) | `gemini-2.5-flash-image` | Module 4 sample stills |
| `RESEMBLE_API_KEY` | Runtime Secret | API key (string, 32+ chars) | `________________________________` | https://app.resemble.ai → Account → API |
| `RESEMBLE_VOICE_UUID` | Runtime Secret | UUID (string) | `________-____-____-____-____________` | Resemble → your voice clone |
| `GOOGLE_CLIENT_ID` | Runtime Secret | OAuth client ID (string, ends `.apps.googleusercontent.com`) | `__________.apps.googleusercontent.com` | Google Cloud Console → OAuth (Desktop) |
| `GOOGLE_CLIENT_SECRET` | Runtime Secret | OAuth client secret (string, often `GOCSPX-…`) | `GOCSPX-________________________` | Same OAuth client |
| `YOUTUBE_TOKEN_JSON` | Runtime Secret | Full JSON from `data/youtube_token.json` (paste entire file) | `{"token": "...", "refresh_token": "..."}` | Optional — skip OAuth on VM if you auth on home PC first |

---

## Cursor API — cloud agents + headless CLI

| Secret name | Cursor type | Value type | Example (filler) | Where to get it |
|-------------|-------------|------------|------------------|-----------------|
| `CURSOR_API_KEY` | Runtime Secret | User API key (string, shown once at create) | `________________________________` | https://cursor.com/dashboard → API Keys |

Powers Cloud Agent API (`https://api.cursor.com/v1/…`) and headless `agent` CLI via `CURSOR_API_KEY`.

---

## New cloud agent run (read first)

Secrets are injected **when the agent starts**. If you add or change a secret while a chat is running, **start a new cloud agent run** — then on the VM:

```bash
bash scripts/install.sh
python3 -m shorts_bot.cloud_secrets
```

Full checklist: **`docs/CLOUD_AGENT_START.md`**

---

## Recommended — TikTok Shop (current project)

| Secret name | Cursor type | Notes |
|-------------|-------------|-------|
| `ZERNIO_API_TOKEN` | Runtime Secret | **Owner name** for Zernio API key — also accepts `ZERNIO_API_KEY`. TikTok multi-account posting. |
| `GEMINI_API_KEY` | Runtime Secret | QC, scripts, vision |
| `KLING_ACCESS_KEY` | Runtime Secret | Affiliate video (later) |
| `KLING_SECRET_KEY` | Runtime Secret | Pair with access key |
| `KLING_MODE` | Environment Variable | Default `std` (720p, ~$0.21/5s clip). Use `pro` only if you need 1080p later. |
| `SCOUT_PROVIDER` | Runtime Secret | `auto` \| `kalodata` \| `fastmoss` — see `docs/FOR_OWNER_KALODATA_OR_FASTMOSS.md` |
| `KALODATA_PILOT_TOKEN` | Runtime Secret | Kalodata KaloPilot token from kalodata.com/pilot |
| `KALODATA_REGION` | Runtime Secret | Default `US` |
| `FASTMOSS_CLIENT_ID` | Runtime Secret | FastMoss OpenAPI — free trial at developers.fastmoss.com |
| `FASTMOSS_CLIENT_SECRET` | Runtime Secret | Pair with client ID |
| `ECHOTIK_USERNAME` | Runtime Secret | **Legacy — retired.** |
| `ECHOTIK_PASSWORD` | Runtime Secret | **Legacy — retired.** |

## Optional — HP hub remote SSH *(agent runs terminal on your laptop)*

Setup: `docs/FOR_OWNER_REMOTE_HUB_SSH.md` · verify: `bash scripts/hub_remote_verify.sh`

| Secret name | Cursor type | Notes |
|-------------|-------------|-------|
| `TAILSCALE_AUTH_KEY` | Runtime Secret | Reusable key — cloud VM joins your tailnet. **Exact spelling** — not `TALESCALE_AUTH_KEY` (common typo; verify script accepts both) |
| `HUB_SSH_HOST` | Environment Variable | Hub Tailscale IP (`100.x.x.x`) |
| `HUB_SSH_USER` | Environment Variable | WSL Linux username |
| `HUB_SSH_PRIVATE_KEY` | Runtime Secret | Full private key from `hub_remote_setup.sh` |

### Desktop helper (Windows keyboard/mouse)

Setup: `docs/FOR_OWNER_DESKTOP_HELPER.md`

| Secret name | Cursor type | Notes |
|-------------|-------------|-------|
| `DESKTOP_HELPER_TOKEN` | Runtime Secret | Same token set in PowerShell when starting helper on hub |
| `DESKTOP_HELPER_HOST` | Environment Variable | Optional — WSL auto-detects Windows IP |
| `DESKTOP_HELPER_PORT` | Environment Variable | Optional — default `9876` |
| `KEYFREEZE_HOTKEY` | Runtime Secret | Optional — same as hub `helper.env`; agent unlock without SSH |
| `KEYFREEZE_EXE` | Environment Variable | Optional — usually only in hub `helper.env` |

KeyFreeze setup: `docs/FOR_OWNER_KEYFREEZE.md`

## Recommended — other

| Secret name | Cursor type | Notes |
|-------------|-------------|-------|
| `WEB_API_TOKEN` | Runtime Secret | Locks mutating `/api/*` on web UI |
| `RESEMBLE_PROJECT_UUID` | Runtime Secret | Optional Resemble project |
| `TTS_PROVIDER` | Environment Variable | `resemble` \| `edge` |
| `REPLICATE_API_TOKEN` | Runtime Secret | Replicate fallback for Kling |
| `AI_VIDEO_GENERATION_ENABLED` | Environment Variable | Default `false` — owner must ask to enable |
| `KLING_PROVIDER` | Environment Variable | `official` \| `replicate` |
| `KLING_MODEL` | Environment Variable | e.g. `kling-v2-6` |

---

## Optional

| Secret name | Cursor type | Value type | Example (filler) | Notes |
|-------------|-------------|------------|------------------|-------|
| `GOOGLE_DRIVE_FOLDER_ID` | Environment Variable | Drive folder ID (string) | `1a2b3c4d5e6f7g8h9i` | InVideo MP4 inbox — `docs/FOR_OWNER_DRIVE_SETUP.md` |
| `GOOGLE_DRIVE_INBOX_ENABLED` | Environment Variable | `true` / `false` | `true` | Poll Drive folder for new MP4s |
| `OPENAI_MODEL` | Environment Variable | Model slug (string) | `gpt-4o-mini` | |
| `ASSEMBLYAI_API_KEY` | Runtime Secret | API key (string, 32+ chars) | `________________________________` | Skip unless `TRANSCRIPT_PROVIDER=assemblyai` |
| `FAL_API_KEY` | Runtime Secret | API key (string) | `________________________________` | If `IMAGE_PROVIDER=fal` |
| `IMAGE_PROVIDER` | Environment Variable | Enum: `replicate` \| `fal` | `replicate` | |
| `VISUAL_STYLE` | Environment Variable | Enum: `ai_video` \| `hybrid` \| `ai` \| `calm_stills` | `ai_video` | Default = free AI horror motions |
| `TAVILY_API_KEY` | Runtime Secret | API key (string, starts `tvly-`) | `tvly-____________________________` | Deep web research |
| `SLACK_BOT_TOKEN` | Runtime Secret | Bot token `xoxb-...` | `xoxb-...` | [api.slack.com/apps](https://api.slack.com/apps) → AlphaBeta001 app |
| `SLACK_CHANNEL_ID` | Environment Variable | Channel ID `C...` | `C0123456789` | `#peripheral-ops` → channel details |
| `SLACK_WEBHOOK_URL` | Runtime Secret | Incoming webhook URL (optional) | `https://hooks.slack.com/services/...` | Fallback if no bot token |
| `SLACK_CHANNEL_EMAIL` | Environment Variable | Channel inbound email | `peripheral-ops@workspace.slack.com` | Option A — `docs/FOR_OWNER_SLACK_EMAIL.md` |
| `GMAIL_SMTP_USER` | Runtime Secret | Gmail sender address | `paypalacc4progress@gmail.com` | With app password for Slack email |
| `GMAIL_SMTP_APP_PASSWORD` | Runtime Secret | Google App Password | `16-char password` | Not your login password |
| `SLACK_POST_MODE` | Environment Variable | `auto` \| `email` \| `bot` | `email` | Force Gmail path when set |
| `SLACK_CURSOR_LINKED` | Environment Variable | `true` after Link Account | `true` | Set after `@cursor help` → Link Account in Slack |
| `SLACK_APP_TOKEN` | Runtime Secret | Socket Mode `xapp-...` | `xapp-...` | Autonomy bus — `docs/SLACK_AUTONOMY.md` |
| `SLACK_AUTONOMY_ENABLED` | Environment Variable | `true` / `false` | `true` | `[autonomy]` self-talk bus |
| `SLACK_CHANNEL_NAME` | Environment Variable | Channel name (no #) | `peripheral-ops` | Optional label for status/briefing |
| `DISCORD_BOT_TOKEN` | Runtime Secret | Bot token (string) | `________________________________` | **Read-only** — see `docs/FOR_OWNER_DISCORD_COURSE_INTEL.md` |
| `DISCORD_GUILD_ID` | Environment Variable | Server ID (string) | `123456789012345678` | Momentum / TikTok Dojo server |
| `DISCORD_CHANNEL_IDS` | Environment Variable | Comma-separated channel IDs | `111...,222...` | Allowlist — agent never sends |
| `COURSE_SITE_URL` | Environment Variable | HTTPS URL (string) | `https://...` | Dashboard — browse after hub login |
| `COURSE_BUBBLE_TOOL_URL` | Environment Variable | HTTPS URL (string) | `https://...` | Free ~10/day generator page |

**Slack:** Option A email = `SLACK_CHANNEL_EMAIL` + `GMAIL_SMTP_*` (`docs/FOR_OWNER_SLACK_EMAIL.md`). Bot = `SLACK_BOT_TOKEN` + `SLACK_CHANNEL_ID` (`docs/FOR_OWNER_SLACK_BOT.md`). Autonomy bus adds `SLACK_APP_TOKEN` (`docs/SLACK_AUTONOMY.md`). `@cursor` = separate OAuth (`docs/FOR_OWNER_SLACK.md`).

---

## Not secrets — one-time at home

| Step | Type | What you do |
|------|------|-------------|
| Sync secrets → `.env` | Command | `bash scripts/install.sh` |
| YouTube OAuth token | Local file (not a Cursor secret) | `python3 -m shorts_bot.youtube.auth_cli` → saves `data/youtube_token.json` |
| Verify | Command | `python3 -m shorts_bot.login_status` |

---

## Auto defaults (no Cursor secret — sync writes if missing)

| Key | Value type | Default |
|-----|------------|---------|
| `TRANSCRIPT_PROVIDER` | Enum | `gemini` |
| `TRANSCRIPT_ALWAYS_FRESH` | Boolean string | `false` |
| `VISION_QC_ENABLED` | Boolean string | `true` |
| `VISION_QC_BLOCKS_UPLOAD` | Boolean string | `true` |
| `VISION_QC_MIN_SCORE` | Float string | `7` |
| `AUTO_PUBLISH_HOURS` | Integer string | `0` |
| `YOUTUBE_UPLOAD_VISIBILITY` | Enum: `public` \| `unlisted` \| `private` | `unlisted` |
| `AUTO_UPLOAD_YOUTUBE` | Boolean string | `true` |
| `REQUIRE_PAID_STACK` | Boolean string | `true` |
| `ALLOW_SCRIPT_TIMING_FALLBACK` | Boolean string | `false` |
