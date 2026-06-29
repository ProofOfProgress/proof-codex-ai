@echo off
REM Big green one-click hub start — double-click after Windows reboot + login.
title Proof Codex - START HUB
color 0A
mode con: cols=64 lines=26
cd /d "%~dp0.."

echo.
echo   ============================================================
echo.
echo        #####  PROOF CODEX  #####
echo.
echo              START HUB
echo.
echo   SSH + Tailscale + Desktop Helper
echo.
echo   ============================================================
echo.
echo   If Ubuntu asks for a password, type it once and press Enter.
echo.

wsl.exe bash -lc "cd ~/proof-codex-ai && bash scripts/hub_one_click_start.sh" 2>nul
if errorlevel 1 (
  for /f "delims=" %%i in ('wsl.exe wslpath -u "%CD%"') do wsl.exe bash -lc "cd '%%i' && bash scripts/hub_one_click_start.sh"
)

echo.
echo   Done. You can close this window.
echo.
pause
