# Cursor secrets checklist

Add these in **Cursor → Cloud Agent → Secrets** (or workspace secrets).  
On the VM, `bash scripts/install.sh` runs `scripts/sync_secrets.py` and copies them into `.env`.

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

---

## Cursor API — cloud agents + headless CLI

| Secret name | Cursor type | Value type | Example (filler) | Where to get it |
|-------------|-------------|------------|------------------|-----------------|
| `CURSOR_API_KEY` | Runtime Secret | User API key (string, shown once at create) | `________________________________` | https://cursor.com/dashboard → API Keys |

Powers Cloud Agent API (`https://api.cursor.com/v1/…`) and headless `agent` CLI via `CURSOR_API_KEY`.

---

## Recommended

| Secret name | Cursor type | Value type | Example (filler) | Notes |
|-------------|-------------|------------|------------------|-------|
| `WEB_API_TOKEN` | Runtime Secret | Random token (string, 32+ chars, you generate) | `sc________________________________` | Locks mutating `/api/*` on web UI |
| `RESEMBLE_PROJECT_UUID` | Runtime Secret | UUID (string) | `________-____-____-____-____________` | Optional Resemble project |
| `TTS_PROVIDER` | Environment Variable | Enum: `resemble` \| `edge` | `resemble` | Voice backend |
| `REPLICATE_API_TOKEN` | Runtime Secret | API token (string, starts `r8_`) | `r8________________________________` | Only if `VISUAL_STYLE=ai` |

---

## Optional

| Secret name | Cursor type | Value type | Example (filler) | Notes |
|-------------|-------------|------------|------------------|-------|
| `OPENAI_API_KEY` | Runtime Secret | API key (string, starts `sk-`) | `sk-________________________________` | Backup chat |
| `OPENAI_MODEL` | Environment Variable | Model slug (string) | `gpt-4o-mini` | |
| `ASSEMBLYAI_API_KEY` | Runtime Secret | API key (string, 32+ chars) | `________________________________` | Skip unless `TRANSCRIPT_PROVIDER=assemblyai` |
| `DISCORD_BOT_TOKEN` | Runtime Secret | Bot token (string) | `________________________________` | Discord Developer Portal |
| `DISCORD_PUBLIC_KEY` | Runtime Secret | Hex string (64 chars) | `________________________________________________` | Discord app → General |
| `DISCORD_OWNER_ID` | Environment Variable | Snowflake ID (numeric string, 17–20 digits) | `__________________` | `!myid` in Discord |
| `DISCORD_NOTIFY_IDS` | Environment Variable | Comma-separated snowflake IDs | `__________________,__________________` | Extra DM targets |
| `FAL_API_KEY` | Runtime Secret | API key (string) | `________________________________` | If `IMAGE_PROVIDER=fal` |
| `IMAGE_PROVIDER` | Environment Variable | Enum: `replicate` \| `fal` | `replicate` | |
| `VISUAL_STYLE` | Environment Variable | Enum: `ai_video` \| `hybrid` \| `ai` \| `calm_stills` | `ai_video` | Default = free AI horror motions |
| `TAVILY_API_KEY` | Runtime Secret | API key (string, starts `tvly-`) | `tvly-____________________________` | Deep web research |

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
