@echo off
REM One-time: put START HUB on your Windows desktop (big green button).
title Proof Codex - Install Hub Start Button

set "DESKTOP=%USERPROFILE%\Desktop"
set "SRC=%~dp0"

echo.
echo === Install hub start button on Desktop ===
echo.

copy /Y "%SRC%HUB_GREEN_START.bat" "%DESKTOP%\START HUB (Proof Codex).bat" >nul
if errorlevel 1 (
  echo Copy failed. Try running as normal user from File Explorer.
  pause
  exit /b 1
)
copy /Y "%SRC%hub_win_repo_path.bat" "%DESKTOP%\hub_win_repo_path.bat" >nul
copy /Y "%SRC%FIX_HUB_ONCE.bat" "%DESKTOP%\FIX HUB ONCE (Proof Codex).bat" >nul
copy /Y "%SRC%HUB_DESKTOP_NOTE.txt" "%DESKTOP%\HUB NOTES (Proof Codex).txt" >nul 2>nul

echo Copied: %DESKTOP%\START HUB (Proof Codex).bat
echo Copied: %DESKTOP%\FIX HUB ONCE (Proof Codex).bat
echo Copied: %DESKTOP%\HUB NOTES (Proof Codex).txt
echo.
echo Optional GUI button (needs Python on Windows):
if exist "%SRC%desktop_helper\hub_green_launcher.pyw" (
  copy /Y "%SRC%desktop_helper\hub_green_launcher.pyw" "%DESKTOP%\START HUB Button.pyw" >nul
  echo Copied: %DESKTOP%\START HUB Button.pyw
)
echo.
echo Double-click START HUB after every reboot (once Windows is logged in).
echo One-time: FIX HUB ONCE stops Ubuntu password prompts.
echo.
pause
