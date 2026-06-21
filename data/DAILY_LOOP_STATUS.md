# Daily loop — ARMED on cloud VM

**Started:** 2026-06-21 UTC  
**Mechanism:** `scripts/daily_loop.sh` in tmux session `daily-invideo-loop`  
**Interval:** every 24 hours (86400 seconds)  
**Command each tick:** `python3 -m shorts_bot.production.invideo_daily_cli`  
**Log:** `data/daily_loop.log`

This is the server-side equivalent of Cursor `/loop` — runs on the cloud workspace, not your laptop.

**Note:** Cursor `/loop` on your laptop is separate — paste `data/LOOP_DAILY_PROMPT.txt` there if you also want local InVideo login.

**Next tick after first run completes:** +24h from end of first run.

Check status: `tail -30 data/daily_loop.log`
