@echo off
REM Keep hub awake + restart services on unlock — RUN AS ADMINISTRATOR
title Proof Codex - Install Hub Never Sleep
cd /d "%~dp0.."

net session >nul 2>&1
if errorlevel 1 (
  echo.
  echo   Right-click this file and choose "Run as administrator"
  echo.
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_hub_never_sleep.ps1"
if errorlevel 1 (
  echo Install failed.
  pause
  exit /b 1
)
echo.
pause
