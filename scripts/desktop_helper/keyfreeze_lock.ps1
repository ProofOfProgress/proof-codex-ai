# Launch KeyFreeze on Windows (path passed from WSL agent).
param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $ExePath)) {
    Write-Error "KeyFreeze exe not found: $ExePath"
    exit 1
}

$existing = Get-Process *KeyFreeze* -ErrorAction SilentlyContinue
if ($existing) {
    Write-Output 'already_running'
    exit 0
}

Start-Process -FilePath $ExePath | Out-Null
Write-Output 'started'
exit 0
