@echo off
REM First-time install — double-click this file (Windows). Do NOT type WSL paths in PowerShell.
title Proof Codex — Install Desktop Helper
cd /d "%~dp0"
cd /d "%~dp0.."
echo.
echo === Desktop helper install ===
echo Repo: %CD%
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0desktop_helper_install.ps1"
echo.
pause
