@echo off
REM Big green one-click hub start — double-click after Windows reboot + login.
title Proof Codex - START HUB
color 0A
mode con: cols=70 lines=32

echo.
echo   ============================================================
echo        PROOF CODEX — START HUB
echo   SSH + Tailscale + Desktop Helper
echo   ============================================================
echo.
echo   If Ubuntu asks for a password, type it ONCE and press Enter.
echo   Do NOT close this window until you see HUB READY or NOT READY.
echo.

call "%~dp0hub_win_repo_path.bat" 2>nul
if not defined REPO_WSL (
  for /f "usebackq delims=" %%i in (`wsl.exe bash -lc "readlink -f \"$HOME/proof-codex-ai\" 2>/dev/null"`) do set "REPO_WSL=%%i"
)

if not defined REPO_WSL (
  color 0C
  echo   ERROR: Could not find ~/proof-codex-ai in WSL.
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
