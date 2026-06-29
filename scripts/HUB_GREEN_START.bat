@echo off
REM Big green one-click hub start — double-click after Windows reboot + login.
title Proof Codex - START HUB
color 0A
mode con: cols=70 lines=32
cd /d "%~dp0.."

echo.
echo   ============================================================
echo        PROOF CODEX — START HUB
echo   SSH + Tailscale + Desktop Helper
echo   ============================================================
echo.
echo   If Ubuntu asks for a password, type it ONCE and press Enter.
echo   Do NOT close this window until you see HUB READY or NOT READY.
echo.

set "REPO_WSL="
for /f "delims=" %%i in ('wsl.exe wslpath -u "%CD%" 2^>nul') do set "REPO_WSL=%%i"

if not defined REPO_WSL (
  color 0C
  echo   ERROR: Could not find repo path in WSL.
  echo   Open Ubuntu and run: cd ~/proof-codex-ai ^&^& bash scripts/hub_one_click_start.sh
  goto done
)

wsl.exe bash -lc "cd '%REPO_WSL%' && bash scripts/hub_one_click_start.sh"
set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE%==0 (
  color 0A
  echo   ============================================================
  echo        HUB READY — tell the agent: hub is back
  echo   ============================================================
) else (
  color 0C
  echo   ============================================================
  echo        NOT READY — read the messages above
  echo   Log file: data\desktop_hub\hub_start.log
  echo.
  echo   Fix in Ubuntu:
  echo     cd ~/proof-codex-ai
  echo     bash scripts/hub_one_click_start.sh
  echo   ============================================================
)

:done
echo.
pause
