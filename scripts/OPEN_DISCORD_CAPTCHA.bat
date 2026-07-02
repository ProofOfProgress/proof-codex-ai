@echo off
REM Double-click on HP — opens Chromium for Discord CAPTCHA (saves Playwright session).
wsl.exe -d Ubuntu --cd /home/isaac/proof-codex-ai -e bash -lc "export DISPLAY=:0 WAYLAND_DISPLAY=wayland-0 BROWSER_ENABLED=true BROWSER_ALLOW_VISIBLE=true; python3 -m shorts_bot.browser.cli open discord --minutes 25 --block"
pause
