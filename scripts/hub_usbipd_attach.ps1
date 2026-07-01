# Attach Android phones from Windows USB to WSL for ADB
# Run in **Admin PowerShell** on the hub laptop when WSL `adb devices` is empty.
#
# Prereqs (one-time, Admin PowerShell):
#   winget install dorssel.usbipd-win
#   wsl --update
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File C:\ProofCodexInstall\hub_usbipd_attach.ps1
# Or from repo after copy:
#   powershell -ExecutionPolicy Bypass -File scripts\hub_usbipd_attach.ps1

$ErrorActionPreference = "Stop"

function Write-Step($msg) {
    Write-Host "==> $msg"
}

Write-Step "Listing USB devices (usbipd)"
$raw = usbipd list 2>&1
Write-Host $raw

# Match Android / ADB-class devices (Google, Samsung, Motorola, etc.)
$lines = $raw -split "`n" | Where-Object { $_ -match "\s+\d+-\d+\s+" }
if (-not $lines) {
    Write-Host "No USB devices found. Plug in a phone with USB debugging enabled."
    exit 1
}

$attached = 0
foreach ($line in $lines) {
    if ($line -notmatch "^\s*(\S+)\s+(\d+-\d+)\s+") { continue }
    $busId = $Matches[2]
    $desc = $line.Trim()
    if ($desc -notmatch "(?i)android|adb|google|samsung|motorola|oneplus|pixel|xiaomi|oppo|vivo|huawei|nokia|lg") {
        Write-Host "SKIP (not Android-looking): $desc"
        continue
    }
    Write-Step "Binding $busId"
    usbipd bind --busid $busId 2>$null
    Write-Step "Attaching $busId to WSL"
    usbipd attach --wsl --busid $busId
    $attached++
}

if ($attached -eq 0) {
    Write-Host "No Android devices attached. Enable USB debugging and accept the RSA prompt on the phone."
    exit 1
}

Write-Step "Checking ADB inside WSL"
wsl.exe bash -lc "adb kill-server 2>/dev/null; adb start-server; adb devices"

Write-Host ""
Write-Host "Done. If device shows 'unauthorized', unlock phone and tap Allow USB debugging."
