# Automation alerts
- **2026-06-22 16:07 UTC** `invideo_daily`: Not logged in — run handoff_cli or paste Drive link
  - draft=1 project=https://ai.invideo.io/ai-mcp-video?video=claude-code-qubijb workflow=v1 — Recovery draft #1: https://ai.invideo.io/ai-mcp-video?video=claude-code-qubijb | Login/check InVideo: python3 -m shorts_bot.invideo.handoff_cli | Retry download: python3 -m shorts_bot.invideo.ship_cli --draft-id 1 | If exported elsewhere, import it: python3 -m shorts_bot.invideo.fetch_url_cli --draft-id 1 'DRIVE_OR_MP4_URL'
- **2026-06-22 07:45 UTC** `claude_code_ship`: **Draft #8 MP4 ready** (44MB, 2 InVideo credits). Upload **queued** for ~2026-06-23 04:45 UTC (21h gap after ChatGPT Plus). Run when due: `python3 -m shorts_bot.youtube.pending_upload_cli process`
- **2026-06-22 07:22 UTC** `claude_code_ship`: first ship attempt failed — Generate UI loads in ~15s; fixed wait in ship_cli
- **2026-06-21 06:47 UTC** `auto_daily`: render failed
  - timeout
- **2026-06-21 06:13 UTC** `invideo_daily`: No Generate/Download on page: Home
Library
Explore
You
Create New
Upgrade
Getting Started
0%
  - draft=7 project=https://ai.invideo.io/ai-mcp-video?video=chatgpt-vs-claude-for-writing-honest-pick-ceecwc — If credits exhausted: Generate on laptop → Drive link → fetch_url_cli
- **2026-06-21 04:55 UTC** `auto_daily`: render failed
  - timeout
- **2026-06-19 05:55 UTC** `auto_daily`: render failed
  - timeout
- **2026-06-19 02:47 UTC** `auto_daily`: render failed
  - timeout
- **2026-06-19 00:41 UTC** `auto_daily`: render failed
  - timeout
- **2026-06-19 00:40 UTC** `auto_daily`: render failed
  - timeout
- **2026-06-19 00:39 UTC** `auto_daily`: render failed
  - timeout
- **2026-06-12 05:47 UTC** `auto_daily`: render failed
  - timeout
- **2026-06-12 05:46 UTC** `auto_daily`: render failed
  - timeout
- **2026-06-12 05:36 UTC** `auto_daily`: render failed
  - timeout
- **2026-06-12 05:35 UTC** `auto_daily`: render failed
  - timeout
- **2026-06-12 05:32 UTC** `auto_daily`: render failed
  - timeout
- **2026-06-12 05:03 UTC** `auto_daily`: render failed
  - timeout
- **2026-06-12 05:03 UTC** `auto_daily`: render failed
  - timeout
