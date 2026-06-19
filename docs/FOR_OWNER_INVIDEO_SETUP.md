# InVideo setup — plain English

Connect InVideo so the agent can turn your scripts into video projects (you export the MP4).

**Time:** ~10 minutes first time.  
**Works without phone:** log in with **Google** on Desktop.

---

## What this gives you

| Step | Who | What |
|------|-----|------|
| Script | Agent | Writes Pay/Skip/Wait review from product queue |
| Start video | Agent | MCP creates InVideo project from script |
| Finish + export | You | Desktop browser → Generate → Download MP4 |
| Upload | Agent | YouTube API (TikTok later when phone works) |

---

## Step 1 — Log into InVideo (one time)

In Cursor, the agent opens the **Desktop** browser tab.

Or run:

```bash
python3 -m shorts_bot.invideo.handoff_cli
```

1. Click **Desktop** tab in Cursor  
2. Log in with **Google** (or email)  
3. Set up your **AI twin** if InVideo asks (face + voice clone)

Check:

```bash
python3 -m shorts_bot.invideo.auth_cli status
```

You want `Browser logged in: True` and `MCP ready: True`.

---

## Step 2 — (Optional) API key

Not required for MCP projects. Add later for higher limits:

1. InVideo → **Settings** → **Developers** → copy API key  
2. Cursor → Cloud Agent → **Secrets** → add `INVIDEO_API_KEY`  
3. On VM: `bash scripts/install.sh`

---

## Step 3 — Generate from a **prompt** (InVideo writes the script)

Default test — ChatGPT Plus review brief:

```bash
python3 -m shorts_bot.invideo.generate_cli --open-browser
```

Custom prompt:

```bash
python3 -m shorts_bot.invideo.generate_cli --open-browser --prompt "30s honest review of NotebookLM. Pay Skip Wait. 9:16 Short."
```

1. Desktop tab opens your InVideo project  
2. **InVideo writes the script** and generates the video  
3. When done → **Download** MP4  
4. Save as: `data/production/invideo_runs/chatgpt-plus/final_short.mp4` (or tell agent path)

**We do not paste finished scripts** unless you pass `--from-our-script`.

---

## Step 4 — Upload to YouTube

```bash
python3 -m shorts_bot.production.upload_canonical_cli --draft-id 1 \
  --video data/production/draft_1/final_short.mp4
```

---

## Manual fallback (no MCP)

Script pack is always written to the draft folder:

```bash
python3 -m shorts_bot.invideo.generate_cli --draft-id 1 --pack-only
```

Open `data/production/draft_1/invideo_script.txt` → paste into InVideo → export MP4.

---

## If stuck

```bash
python3 -m shorts_bot.invideo.auth_cli status
python3 -m shorts_bot.login_status
```

Common fixes:
- **"Login to continue"** on project URL → run `handoff_cli` again, sign in with Google  
- **No credits** → upgrade InVideo plan or wait for monthly reset  
- **Twin not ready** → finish face/voice clone in InVideo settings first

When first video looks good, tell the agent **"invideo pass"** — we wire full autopilot next.
