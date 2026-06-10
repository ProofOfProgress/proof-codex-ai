# Cursor secrets checklist

Add these in **Cursor → Cloud Agent → Secrets** (or your workspace secrets).  
On the VM, `bash scripts/install.sh` runs `scripts/sync_secrets.py` and copies them into `.env`.

**Do not paste real values in chat or commit them to git.**

## Required — full Shorts autopilot

| Secret name | Example / format | Where to get it |
|-------------|------------------|-----------------|
| `GEMINI_API_KEY` | `AIzaSy…` (long) | https://aistudio.google.com/apikey |
| `GEMINI_MODEL` | `gemini-2.5-flash-lite` | Default; chat + transcript + vision QC |
| `RESEMBLE_API_KEY` | `…` (32+ chars) | https://app.resemble.ai → Account → API |
| `RESEMBLE_VOICE_UUID` | `xxxxxxxx-xxxx-…` | Resemble → your voice clone |
| `GOOGLE_CLIENT_ID` | `123….apps.googleusercontent.com` | Google Cloud Console → OAuth client (Desktop) |
| `GOOGLE_CLIENT_SECRET` | `GOCSPX-…` | Same OAuth client |

## Cursor API — cloud agents + headless CLI

| Secret name | Example / format | Where to get it |
|-------------|------------------|-----------------|
| `CURSOR_API_KEY` | `key_…` or user API key from dashboard | https://cursor.com/dashboard → API Keys (or Integrations → User API Keys) |

Used for Cloud Agent API (`https://api.cursor.com/v1/…`) and `agent -p` with `CURSOR_API_KEY`.  
Treat like a password — never commit or share publicly.

## Recommended

| Secret name | Example / format | Where to get it |
|-------------|------------------|-----------------|
| `WEB_API_TOKEN` | `sc_…` (long random string) | You generate — protects mutating `/api/*` on web UI |
| `RESEMBLE_PROJECT_UUID` | `…` | Resemble project (optional) |
| `TTS_PROVIDER` | `resemble` | Usually auto via defaults |
| `REPLICATE_API_TOKEN` | `r8_…` | Only if `VISUAL_STYLE=ai` — https://replicate.com/account/api-tokens |

## Optional

| Secret name | Example / format | Notes |
|-------------|------------------|-------|
| `OPENAI_API_KEY` | `sk-…` | Fallback chat if Gemini unavailable |
| `OPENAI_MODEL` | `gpt-4o-mini` | |
| `ASSEMBLYAI_API_KEY` | `…` | Only if `TRANSCRIPT_PROVIDER=assemblyai` (default is `gemini`) |
| `DISCORD_BOT_TOKEN` | `…` | Discord control |
| `DISCORD_PUBLIC_KEY` | hex | Discord slash commands |
| `DISCORD_OWNER_ID` | `123456789012345678` | Your Discord user id |
| `DISCORD_NOTIFY_IDS` | `id1,id2` | Extra notify targets |
| `FAL_API_KEY` | `…` | If `IMAGE_PROVIDER=fal` |
| `IMAGE_PROVIDER` | `replicate` or `fal` | |
| `VISUAL_STYLE` | `stickfigure` | Default stick figures (free) |
| `TAVILY_API_KEY` | `tvly-…` | Deep web research (optional) |

## Not secrets — one-time at home

| Step | Command | Notes |
|------|---------|-------|
| Sync secrets → `.env` | `bash scripts/install.sh` | After adding Cursor secrets |
| YouTube OAuth (upload scope) | `python3 -m shorts_bot.youtube.auth_cli` | System browser Google sign-in once; saves `data/youtube_token.json` |
| Verify | `python3 -m shorts_bot.login_status` | Want **YouTube API upload — Ready** |

## Defaults (auto-written by sync — no secret needed)

`TRANSCRIPT_PROVIDER=gemini`, `TRANSCRIPT_ALWAYS_FRESH=false`, `VISION_QC_ENABLED=true`, `AUTO_PUBLISH_HOURS=0`, `YOUTUBE_UPLOAD_VISIBILITY=unlisted`, etc.
