@echo off
REM One-time: hub auto-starts 45 seconds after Windows login (no START HUB click).
title Proof Codex - Install Hub Auto-Start
cd /d "%~dp0.."
echo.
echo === Install auto-start at Windows login ===
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows_hub_autostart.ps1"
if errorlevel 1 (
  echo Install failed.
  pause
  exit /b 1
)
echo.
echo Optional: copy FIX_HUB_ONCE.bat to Desktop for emergencies.
copy /Y "%~dp0FIX_HUB_ONCE.bat" "%USERPROFILE%\Desktop\FIX HUB ONCE (Proof Codex).bat" >nul 2>&1
echo Copied FIX HUB ONCE shortcut to Desktop.
echo.
pause
