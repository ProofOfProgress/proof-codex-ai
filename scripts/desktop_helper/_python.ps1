# Shared helpers for Windows desktop helper scripts.
$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    # scripts/desktop_helper/_python.ps1 -> repo root is two levels up from scripts/
    if ($PSScriptRoot -match "desktop_helper$") {
        return (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
    }
    return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Find-PythonExe {
    # Prefer Windows py launcher, then python on PATH.
    foreach ($candidate in @(
        @{ Args = @("-3"); Cmd = "py" },
        @{ Args = @(); Cmd = "python" },
        @{ Args = @(); Cmd = "python3" }
    )) {
        $cmd = Get-Command $candidate.Cmd -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        $argList = @($candidate.Args + @("-c", "import sys; print(sys.executable)"))
        try {
            $exe = & $candidate.Cmd @argList 2>$null | Select-Object -First 1
            if ($exe -and (Test-Path $exe)) {
                return @{ Launcher = $candidate.Cmd; LauncherArgs = $candidate.Args; Exe = $exe.Trim() }
            }
        } catch {}
    }
    return $null
}

function Import-HelperEnv {
    param([string]$Root)
    $EnvFile = Join-Path $Root "data\desktop_hub\helper.env"
    if (-not (Test-Path $EnvFile)) {
        return $false
    }
    Get-Content $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or $line -notmatch "=") { return }
        $name, $value = $line -split "=", 2
        $name = $name.Trim()
        $value = $value.Trim().Trim('"').Trim("'")
        if ($name -eq "DESKTOP_HELPER_TOKEN") {
            $value = ($value -replace "\s", "")
        }
        if ($name) {
            Set-Item -Path "Env:$name" -Value $value
        }
    }
    return $true
}

function Test-HelperEnv {
    param([string]$Root)
    $example = Join-Path $Root "data\desktop_hub\helper.env.example"
    $envFile = Join-Path $Root "data\desktop_hub\helper.env"
    if (-not (Test-Path $envFile)) {
        Write-Host ""
        Write-Host "MISSING: data\desktop_hub\helper.env"
        Write-Host "1. Copy helper.env.example to helper.env in the same folder"
        Write-Host "2. Paste DESKTOP_HELPER_TOKEN (same as Cursor Secrets) - no spaces"
        if (Test-Path $example) {
            Write-Host "   Example file: $example"
        }
        return $false
    }
    return $true
}
