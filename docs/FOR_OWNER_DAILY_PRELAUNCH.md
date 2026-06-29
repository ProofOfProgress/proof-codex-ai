# Daily pre-launch — wake the CEO agent every morning

**Before Launch Date:** one automated run per day that **researches products**, **writes the day's plan**, **pastes the CEO prompt into Cursor**, and **clicks Run** — so the cloud agent schedules and generates that day's affiliate clips (QC-pass, queued locally, **no Zernio**).

---

## What happens each day (automatic)

1. **Prepare** (WSL) — FastMoss scout if wired, pick products, write `today_plan.json` + `today_prompt.txt`, create mission id  
2. **Focus** Cursor chat (mouse click at your coords)  
3. **Paste** the daily CEO prompt (keyboard — not clicking keys)  
4. **Click Run** (mouse at your submit button coords)  
5. **Cloud agent** executes — research → Kling → edit → zero-strike QC → queue  

Requires: **desktop helper running** on Windows (`START_DESKTOP_HELPER.bat`) + **Cursor open** on hub laptop.

---

## One-time setup

### 1. Helper + token
See `FOR_OWNER_DESKTOP_HELPER.md` — `helper.env` + double-click `scripts/START_DESKTOP_HELPER.bat`.

### 2. Clips per day (default 8)

```bash
python3 -m shorts_bot.daily_prelaunch.cli config --clips 8 --timezone America/Los_Angeles
```

During warmup you can use `--clips 4` to save Kling credits.

### 3. Calibrate Cursor click spots

Ask the agent for a screenshot, then set **focus** (chat box) and **submit** (Run agent button):

```bash
python3 -m shorts_bot.desktop_hub.cli schedule set-prelaunch \
  --hour 7 --minute 0 \
  --focus-x 400 --focus-y 850 \
  --submit-x 1180 --submit-y 920 \
  --clips 8 \
  --enable \
  --label "Cursor daily CEO mission"
```

### 4. Test without waiting 24h

```bash
python3 -m shorts_bot.daily_prelaunch.cli prepare
python3 -m shorts_bot.daily_prelaunch.cli prompt   # read what will be sent
```

Manual send: copy `data/daily_prelaunch/today_prompt.txt` into a new Cloud Agent chat.

---

## Files

| File | Purpose |
|------|---------|
| `data/daily_prelaunch/today_plan.json` | Products + mission id for today |
| `data/daily_prelaunch/today_prompt.txt` | Text pasted into Cursor |
| `data/daily_prelaunch/config.json` | clips_target, timezone |
| `data/desktop_hub/schedule.json` | prelaunch time + click coordinates |

---

## Commands

```bash
python3 -m shorts_bot.daily_prelaunch.cli prepare
python3 -m shorts_bot.daily_prelaunch.cli show
python3 -m shorts_bot.desktop_hub.cli schedule show
python3 -m shorts_bot.desktop_hub.cli ensure --via-hub
```

---

## Hard rules (in every prompt)

- Agent owns product research — owner does not pick products  
- Zero strikes — QC before ready  
- No Zernio on purchased account until owner says launch is close  

---

## Related

- Desktop helper: `FOR_OWNER_DESKTOP_HELPER.md`  
- Launch order: `LAUNCH_TODO.md`  
- Pipeline: `PIPELINE_SYSTEM_DESIGN.md`
