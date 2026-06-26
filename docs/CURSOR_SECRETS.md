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
| `GEMINI_MODEL` | Environment Variable | Model slug (string) | `gemini-2.5-flash-lite` | Google AI Studio / docs |
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
| `ECHOTIK_USERNAME` | Runtime Secret | Product scout (later) |
| `ECHOTIK_PASSWORD` | Runtime Secret | Pair with username |

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
