# Video production — TurboScribe + still images (replaces Claude Code workflow)

This is the **Soft Continuity** version of the faceless Shorts pipeline from the tutorial you shared — same steps, but the **Shorts Bot** does the script + timestamp + image-prompt work.

## Pipeline (≈20 min per Short)

| Step | Who | Tool |
|------|-----|------|
| 1. Script | Bot | `draft <topic>` → approve |
| 2. Voiceover | Bot (default) | Auto `voiceover.mp3` on `make video` — no mic needed (see `docs/VOICEOVER_POLICY.md`) |
| 3. Timestamps | TurboScribe | Upload audio → **Whale** mode → copy text **with timestamps** |
| 4. Image pack | Bot | `produce <draft_id> \| <paste>` or web **Learning → Build production pack** |
| 5. Still images | You / Cursor | One PNG per `prompts/00.07.txt` etc. (Higgsfield optional) |
| 6. Edit | CapCut | Drop images on timeline by filename seconds → see `CAPCUT_TIMELINE.md` |
| 7. Upload | You | YouTube Studio Short |
| 8. Learn | Bot | `sync` → Yes/No improvements |

## Fully automated (no TurboScribe paste)

Bot estimates timestamps from the approved script and **renders still PNGs** locally.

**Discord:** `!makevideo 6`  
**Web:** Learning → draft ID → **Auto-make video**  
**Chat:** `make video 6`

Output: `data/production/draft_6/images/*.png` + `VOICEOVER_SCRIPT.txt` + `CAPCUT_TIMELINE.md`

**You only:** CapCut (import `voiceover.mp3` + `images/`) → upload to YouTube. Mic optional.

---

## Bot commands (TurboScribe path — tighter sync)

**Discord**
```
!produce 5 | 0:00 Imagine waking up at 2 a.m.
0:07 and not reaching for your phone.
0:15 Just absolute darkness.
```

**Web** — Learning tab → draft ID + paste transcript → **Build production pack**

**CLI**
```bash
python3 -m shorts_bot.production.cli --draft-id 5 --transcript turboscribe.txt
```

## Output folder

```
data/production/draft_5/
  manifest.json          # full metadata
  prompts/00.00.txt      # one image prompt per timestamp
  prompts/00.07.txt
  images/                # put generated PNGs here (00.07.png)
  CAPCUT_TIMELINE.md     # where to cut each still
  MASTER_IMAGE_PROMPT.md # batch prompt for image tools
  README.txt
```

## Image style — ChainsFR stick figures (default)

Stick figures **act out** each line. Speech bubbles when the character **says** something (quoted dialogue).

See `channel/brand/stick_figure_style.md`. Set `VISUAL_STYLE=calm_stills` in `.env` to revert to old style.

## Script rule — AI detector passes (required)

Before `finish video`, the bot runs the script through an **AI likelihood detector up to 5 times** and humanizes until score ≤ 35.

Log: `data/production/draft_<id>/ai_detect_log.txt`

## Optional: Higgsfield

Tutorial used Higgsfield + Claude Code for batch image gen. You can paste `MASTER_IMAGE_PROMPT.md` + prompts into Higgsfield or ask Cursor to generate images from each `prompts/*.txt` file.

## Filename rule (important)

`00.07.png` = starts at **7 seconds** on the CapCut timeline. Drag until the next file’s second mark — same as the tutorial.
