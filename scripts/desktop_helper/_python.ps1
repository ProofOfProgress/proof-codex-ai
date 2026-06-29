# Shared helpers for Windows desktop helper scripts.
$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    if ($env:DESKTOP_HUB_REPO_WIN -and (Test-Path -LiteralPath $env:DESKTOP_HUB_REPO_WIN)) {
        return $env:DESKTOP_HUB_REPO_WIN
    }
    $here = $PSScriptRoot
    if ($here -match "desktop_helper$") {
        return (Resolve-Path (Join-Path $here "..\..")).Path
    }
    return (Resolve-Path (Join-Path $here "..")).Path
}

function Find-PythonExe {
    $candidates = @()

    foreach ($candidate in @(
        @{ Args = @("-3"); Cmd = "py" },
        @{ Args = @(); Cmd = "python" },
        @{ Args = @(); Cmd = "python3" }
    )) {
        $cmd = Get-Command $candidate.Cmd -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        $argList = @($candidate.Args + @("-c", "import sys; print(sys.version_info.major)"))
        try {
            $major = & $candidate.Cmd @argList 2>$null | Select-Object -First 1
            if ($major -eq "3") {
                $exeArg = @($candidate.Args + @("-c", "import sys; print(sys.executable)"))
                $exe = & $candidate.Cmd @exeArg 2>$null | Select-Object -First 1
                if ($exe -and (Test-Path $exe)) {
                    return @{ Launcher = $candidate.Cmd; LauncherArgs = $candidate.Args; Exe = $exe.Trim() }
                }
            }
        } catch {}
    }

    # winget / python.org default user install paths (PATH may not refresh in same session)
    $localApp = $env:LOCALAPPDATA
    if ($localApp) {
        foreach ($pattern in @(
            "$localApp\Programs\Python\Python312\python.exe",
            "$localApp\Programs\Python\Python313\python.exe",
            "$localApp\Programs\Python\Python311\python.exe"
        )) {
            if (Test-Path $pattern) {
                return @{ Launcher = $pattern; LauncherArgs = @(); Exe = $pattern }
            }
        }
        $found = Get-ChildItem -Path "$localApp\Programs\Python" -Filter python.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            return @{ Launcher = $found.FullName; LauncherArgs = @(); Exe = $found.FullName }
        }
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
