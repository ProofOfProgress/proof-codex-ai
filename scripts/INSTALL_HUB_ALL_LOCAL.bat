@echo off
title Proof Codex - Install Hub (local C drive)
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0INSTALL_HUB_ALL_LOCAL.ps1"
pause
