@echo off
REM Double-click to start desktop helper (Windows). Keeps running in background.
cd /d "%~dp0.."
if not exist "data\desktop_hub" mkdir "data\desktop_hub"
if not exist "data\desktop_hub\helper.env" (
  echo.
  echo First time: copy data\desktop_hub\helper.env.example to data\desktop_hub\helper.env
  echo Paste your DESKTOP_HELPER_TOKEN ^(same as Cursor Secrets^).
  echo.
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0desktop_helper_start_background.ps1"
echo.
echo Helper is running in the background.
echo To stop: close Python in Task Manager or reboot.
echo.
pause
