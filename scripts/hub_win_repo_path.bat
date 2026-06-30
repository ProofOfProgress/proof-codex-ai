@echo off
REM Sets REPO_WSL to the WSL absolute path of proof-codex-ai.
REM Safe from Desktop shortcuts — does NOT use %~dp0.. (that breaks on Desktop).
set "REPO_WSL="
for /f "usebackq delims=" %%i in (`wsl.exe bash -lc "if [[ -f \"$HOME/proof-codex-ai/scripts/hub_one_click_start.sh\" ]]; then readlink -f \"$HOME/proof-codex-ai\"; fi"`) do set "REPO_WSL=%%i"
