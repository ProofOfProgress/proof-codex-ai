@echo off
title Proof Codex - Install Hub Gateway
cd /d "%~dp0.."
echo.
echo === Install Windows SSH gateway (port 2222) ===
echo Right-click needed if not admin — this window must say Administrator.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_hub_windows_gateway.ps1"
if errorlevel 1 (
  echo.
  echo FAILED — right-click this file - Run as administrator
  pause
  exit /b 1
)
echo.
pause
