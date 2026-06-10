# YouTube comment automation

Light comments get warm auto-replies in channel voice. **Serious** comments are queued for you — the bot never posts on those.

## Auto-reply (bot handles)

- Thanks / positive feedback
- Topic requests ("minute before X")
- Short casual questions

## Left for you

- Crisis / self-harm language
- Trauma, grief, abuse
- Medical or medication questions
- Long personal vents (400+ chars)
- Business / collab / payment
- Spam and links (ignored, not notified)

## Commands

```text
comments              # run triage + auto-reply now
comments pending      # list serious comments waiting
sync                  # also runs comment pass after analytics
```

Discord: `!comments` / `!comments pending`

API: `POST /api/youtube/comments`, `GET /api/youtube/comments/pending`

## Config (`.env`)

```bash
AUTO_REPLY_COMMENTS=true
AUTO_COMMENT_SYNC=true
COMMENT_FETCH_MAX=40
COMMENT_MAX_AUTO_PER_RUN=8
```

OAuth needs upload scope (same as video upload). Re-auth if replies fail:

```bash
YOUTUBE_OAUTH_UPLOAD=1 python3 -m shorts_bot.youtube.auth_cli
```
