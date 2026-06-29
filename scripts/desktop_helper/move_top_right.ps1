# Move mouse to top-right corner via local desktop helper daemon.
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "_python.ps1")

$Root = Get-RepoRoot
Import-HelperEnv -Root $Root | Out-Null
if (-not $env:DESKTOP_HELPER_TOKEN) {
    Write-Error "DESKTOP_HELPER_TOKEN missing in data\desktop_hub\helper.env"
}

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class ScreenSize {
    [DllImport("user32.dll")] public static extern int GetSystemMetrics(int nIndex);
}
"@

$w = [ScreenSize]::GetSystemMetrics(0)
$h = [ScreenSize]::GetSystemMetrics(1)
$x = $w - 5
$y = 5

$body = @{ action = "move"; x = $x; y = $y } | ConvertTo-Json -Compress
$headers = @{ Authorization = "Bearer $($env:DESKTOP_HELPER_TOKEN)" }
$uri = "http://127.0.0.1:$($env:DESKTOP_HELPER_PORT)/v1/command"
if (-not $env:DESKTOP_HELPER_PORT) { $uri = "http://127.0.0.1:9876/v1/command" }

$r = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/json" -Headers $headers -TimeoutSec 10
Write-Host "Screen ${w}x${h} -> moved to ($x, $y)"
$r | ConvertTo-Json
