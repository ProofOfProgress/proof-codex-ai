@echo off
REM One-time: hub auto-starts 45 seconds after Windows login (no START HUB click).
title Proof Codex - Install Hub Auto-Start

echo.
echo === Install auto-start at Windows login ===
echo.

set "PS1_WSL="
for /f "usebackq delims=" %%i in (`wsl.exe bash -lc "readlink -f \"$HOME/proof-codex-ai/scripts/windows_hub_autostart.ps1\" 2>/dev/null"`) do set "PS1_WSL=%%i"

if not defined PS1_WSL (
  echo Could not find windows_hub_autostart.ps1 in ~/proof-codex-ai
  echo Open Ubuntu, run: cd ~/proof-codex-ai ^&^& git pull
  pause
  exit /b 1
)

for /f "usebackq delims=" %%w in (`wsl.exe wslpath -w "%PS1_WSL%"`) do set "PS1_WIN=%%w"

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1_WIN%"
if errorlevel 1 (
  echo Install failed.
  pause
  exit /b 1
)

set "DESKTOP=%USERPROFILE%\Desktop"
set "SRC=%~dp0"
copy /Y "%SRC%FIX_HUB_ONCE.bat" "%DESKTOP%\FIX HUB ONCE (Proof Codex).bat" >nul 2>&1
copy /Y "%SRC%hub_win_repo_path.bat" "%DESKTOP%\hub_win_repo_path.bat" >nul 2>&1
copy /Y "%SRC%HUB_DESKTOP_NOTE.txt" "%DESKTOP%\HUB NOTES (Proof Codex).txt" >nul 2>&1
echo.
echo Copied FIX HUB ONCE + notes to Desktop.
echo.
pause
