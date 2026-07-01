@echo off
title Proof Codex - Install Hub Watchdog
cd /d "%~dp0.."
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_hub_watchdog.ps1"
if errorlevel 1 pause
echo.
pause
