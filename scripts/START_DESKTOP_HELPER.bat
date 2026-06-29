@echo off
REM Start desktop helper — double-click (Windows). Run INSTALL first if you never installed.
title Proof Codex — Start Desktop Helper
cd /d "%~dp0"
cd /d "%~dp0.."
echo.
echo === Start desktop helper ===
echo Repo: %CD%
echo.
if not exist "data\desktop_hub\helper.env" (
  echo.
  echo STOP: data\desktop_hub\helper.env is missing.
  echo.
  echo 1. Open folder: data\desktop_hub
  echo 2. Copy helper.env.example to helper.env
  echo 3. Edit helper.env — paste DESKTOP_HELPER_TOKEN with NO spaces
  echo    Same token as Cursor Cloud Agent Secrets.
  echo.
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0desktop_helper_start_background.ps1"
if errorlevel 1 (
  echo.
  echo Start failed. Try running INSTALL_DESKTOP_HELPER.bat first.
  pause
  exit /b 1
)
echo.
echo Helper should be running in the background.
echo Log: data\desktop_hub\daemon.log
echo.
pause
