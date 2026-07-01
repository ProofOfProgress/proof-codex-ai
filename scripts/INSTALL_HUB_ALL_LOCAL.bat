@echo off
REM Hub install — always copy PS1 to C: first (UNC path breaks PowerShell parser).
title Proof Codex - Hub Install
color 0E
echo.
echo   PROOF CODEX - HUB INSTALL (gateway + watchdog + never sleep)
echo   Must run as Administrator (right-click - Run as administrator)
echo.

net session >nul 2>&1
if errorlevel 1 (
  color 0C
  echo   ERROR: Not running as Administrator.
  echo   Right-click this file - Run as administrator
  goto done
)

echo   Step 1 - git pull + copy scripts to C:\ProofCodexInstall ...
wsl.exe bash -lc "cd ~/proof-codex-ai && git pull -q && mkdir -p /mnt/c/ProofCodexInstall && cp scripts/INSTALL_HUB_ALL_LOCAL.ps1 scripts/install_hub_windows_gateway.ps1 scripts/install_hub_watchdog.ps1 scripts/install_hub_never_sleep.ps1 scripts/install_hub_wslconfig.ps1 scripts/hub_watchdog.ps1 scripts/hub_print_secrets_for_cursor.ps1 /mnt/c/ProofCodexInstall/"
if errorlevel 1 (
  color 0C
  echo   FAIL - open Ubuntu, ensure ~/proof-codex-ai exists
  goto done
)

echo   Step 2 - run install from C:\ProofCodexInstall ...
powershell -NoProfile -ExecutionPolicy Bypass -File C:\ProofCodexInstall\INSTALL_HUB_ALL_LOCAL.ps1
set EXITCODE=%ERRORLEVEL%

if %EXITCODE%==0 (
  color 0A
  echo.
  echo   DONE - copy Cursor secrets printed above, then NEW agent run
) else (
  color 0C
  echo.
  echo   INSTALL FAILED - scroll up for errors
)

:done
echo.
pause
