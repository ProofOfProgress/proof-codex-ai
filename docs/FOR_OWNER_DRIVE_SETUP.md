# Google Drive inbox — plain English setup

**What this does:** You finish a video in InVideo on your laptop, save the MP4 to a Google Drive folder, and the agent picks it up automatically — no pasting links in chat.

**Time:** ~5 minutes one-time setup.

---

## Your loop (after setup)

1. InVideo on laptop → **Download** MP4  
2. Upload to your **Rapid Tool Review Inbox** folder on Drive  
3. Name the file **`draft_6.mp4`** (use the draft number you're shipping)  
4. Tell the agent **"pull draft 6 from Drive"** — or the daily workflow will grab it on its own  

Optional one-shot command (agent runs this):

```bash
python3 -m shorts_bot.drive.inbox_cli pull --draft-id 6 --upload
```

---

## Step 1 — Create the inbox folder

1. Open [Google Drive](https://drive.google.com) on your laptop  
2. **New → Folder** → name it **`Rapid Tool Review Inbox`**  
3. Open the folder  
4. Copy the **folder ID** from the address bar:  
   `https://drive.google.com/drive/folders/THIS_PART_IS_THE_ID`

---

## Step 2 — Tell the agent your folder ID

In **Cursor → Cloud Agent → Secrets**, add:

| Secret name | Value |
|-------------|--------|
| `GOOGLE_DRIVE_FOLDER_ID` | The folder ID from Step 1 |

Then on the VM:

```bash
bash scripts/install.sh
```

Check status:

```bash
python3 -m shorts_bot.drive.inbox_cli status
```

You want **Drive API ready: True** and your folder listed.

---

## Step 3 — Enable Google Drive API (one time)

Same Google Cloud project as YouTube:

1. [Google Cloud Console](https://console.cloud.google.com) → your project  
2. **APIs & Services → Library** → search **Google Drive API** → **Enable**

---

## Step 4 — Re-connect Google (add Drive permission)

Your existing YouTube login may not include Drive yet. Run on the VM (Desktop browser tab):

```bash
python3 -m shorts_bot.youtube.auth_cli connect
```

Sign in → **Allow** (YouTube + Drive read access).

Verify:

```bash
python3 -m shorts_bot.login_status
```

Look for **Google Drive inbox → Ready**.

---

## File naming (important)

| Filename | Agent assigns to |
|----------|------------------|
| `draft_6.mp4` | Draft #6 |
| `6_chatgpt_plus.mp4` | Draft #6 |
| `draft-7-final.mp4` | Draft #7 |

If the name has no number, run with `--draft-id N` explicitly.

---

## Still works: paste a link

If you don't set up the folder yet, the old path still works:

```bash
python3 -m shorts_bot.invideo.fetch_url_cli --draft-id 6 'PASTE_DRIVE_LINK'
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "No new MP4s in inbox" | Check file is in the right folder; name ends in `.mp4` |
| "Token needs Drive scope" | Re-run `auth_cli connect` (Step 4) |
| "Download too small" | File still uploading — wait 30s and retry |
| Wrong draft | Rename file to `draft_N.mp4` or use `--draft-id N` |

```bash
python3 -m shorts_bot.drive.inbox_cli status   # config + pending files
python3 -m shorts_bot.drive.inbox_cli list      # everything in folder
python3 -m shorts_bot.drive.inbox_cli pull --draft-id 6
```

When first video ships this way, tell the agent **"drive pass"** — we'll wire it into full daily autopilot next.
