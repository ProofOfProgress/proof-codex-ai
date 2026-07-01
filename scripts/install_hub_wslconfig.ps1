# Copy .wslconfig so WSL never idles out (hub stays alive when Windows is locked).
param(
    [string]$WslUser = $env:USERNAME
)

$ErrorActionPreference = 'Stop'
$Dest = Join-Path $env:USERPROFILE '.wslconfig'

$content = @"
[wsl2]
# Keep WSL running when Windows is locked (hub agent needs this).
vmIdleTimeout=-1
networkingMode=mirrored
dnsTunneling=true
firewall=true
autoMemoryReclaim=disabled
"@

Set-Content -Path $Dest -Value $content -Encoding UTF8
Write-Host "[OK] Wrote $Dest"
Write-Host "Run in PowerShell (once): wsl.exe --shutdown"
Write-Host "Then open Ubuntu again — WSL picks up new settings."
