@echo off
REM Opens Ubuntu with the one-time hub fix script — use when START HUB crashes.
title Proof Codex - Fix Hub Once
cd /d "%~dp0.."

echo.
echo   Opening Ubuntu to fix hub connection...
echo   Enter your Ubuntu password if asked (once).
echo.

set "REPO_WSL="
for /f "delims=" %%i in ('wsl.exe wslpath -u "%CD%" 2^>nul') do set "REPO_WSL=%%i"

if not defined REPO_WSL (
  echo Could not find repo in WSL. Open Ubuntu manually and run:
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
