@echo off
REM Emergency hub recovery — visible window, always pauses at end.
title Proof Codex - HUB RECOVERY
color 0E
mode con: cols=72 lines=36

echo.
echo   ============================================================
echo        PROOF CODEX — HUB RECOVERY
echo   Fixes WSL SSH + starts services. Use when agent is offline.
echo   ============================================================
echo.

call "%~dp0hub_win_repo_path.bat" 2>nul
if not defined REPO_WSL (
  for /f "usebackq delims=" %%i in (`wsl.exe bash -lc "readlink -f \"$HOME/proof-codex-ai\" 2>/dev/null"`) do set "REPO_WSL=%%i"
)

if not defined REPO_WSL (
  color 0C
  echo   ERROR: ~/proof-codex-ai not found in WSL.
  echo   Open Ubuntu, clone repo, run again.
  goto done
)

echo   Step 1/3 — WSL SSH fix...
wsl.exe bash -lc "cd '%REPO_WSL%' && bash scripts/hub_wsl_fix_all.sh"
echo.

echo   Step 2/3 — Hub start (SSH + Tailscale + helper)...
wsl.exe bash -lc "cd '%REPO_WSL%' && bash scripts/hub_one_click_start.sh"
set EXITCODE=%ERRORLEVEL%
echo.

echo   Step 3/3 — Windows gateway check (port 2222)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Service sshd -ErrorAction SilentlyContinue | Select-Object Status,Name; if (Test-Path \"$env:ProgramFiles\Tailscale\tailscale.exe\") { & \"$env:ProgramFiles\Tailscale\tailscale.exe\" ip -4 } else { Write-Host 'Install Tailscale Windows app + gateway: INSTALL_HUB_GATEWAY.bat' }"
echo.

if %EXITCODE%==0 (
  color 0A
  echo   ============================================================
  echo        RECOVERY DONE — tell agent: try hub verify
  echo   If you installed gateway: HUB_SSH_PORT=2222 in Cursor secrets
  echo   ============================================================
) else (
  color 0C
  echo   ============================================================
  echo        PARTIAL — read messages above
  echo   One-time admin: INSTALL_HUB_GATEWAY.bat + INSTALL_HUB_WATCHDOG.bat
  echo   ============================================================
)

:done
echo.
pause
