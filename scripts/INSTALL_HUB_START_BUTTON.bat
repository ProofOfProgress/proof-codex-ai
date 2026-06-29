@echo off
REM One-time: put START HUB on your Windows desktop (big green button).
title Proof Codex - Install Hub Start Button
cd /d "%~dp0.."

set "DESKTOP=%USERPROFILE%\Desktop"
set "NAME=START HUB (Proof Codex).bat"

echo.
echo === Install hub start button on Desktop ===
echo.

copy /Y "%~dp0HUB_GREEN_START.bat" "%DESKTOP%\%NAME%" >nul
if errorlevel 1 (
  echo Copy failed. Try running as normal user from File Explorer.
  pause
  exit /b 1
)

echo Copied: %DESKTOP%\%NAME%
echo.
echo Optional GUI button (needs Python on Windows):
if exist "%~dp0desktop_helper\hub_green_launcher.pyw" (
  copy /Y "%~dp0desktop_helper\hub_green_launcher.pyw" "%DESKTOP%\START HUB Button.pyw" >nul
  echo Copied: %DESKTOP%\START HUB Button.pyw
)
echo.
echo Double-click either shortcut after every reboot (once Windows is logged in).
echo.
pause
