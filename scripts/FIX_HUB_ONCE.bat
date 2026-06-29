@echo off
REM Opens Ubuntu with the one-time hub fix script — use when START HUB crashes.
title Proof Codex - Fix Hub Once

echo.
echo   Opening Ubuntu to fix hub connection...
echo   Enter your Ubuntu password if asked (once).
echo.

call "%~dp0hub_win_repo_path.bat" 2>nul
if not defined REPO_WSL (
  for /f "usebackq delims=" %%i in (`wsl.exe bash -lc "readlink -f \"$HOME/proof-codex-ai\" 2>/dev/null"`) do set "REPO_WSL=%%i"
)

if not defined REPO_WSL (
  echo Could not find ~/proof-codex-ai in WSL. Open Ubuntu manually and run:
  echo   cd ~/proof-codex-ai
  echo   bash scripts/hub_owner_fix_once.sh
  pause
  exit /b 1
)

start "Proof Codex Fix Hub" wsl.exe --cd "%REPO_WSL%" bash -i scripts/hub_owner_fix_once.sh
echo.
echo   Ubuntu window opened — follow prompts there.
echo.
pause
