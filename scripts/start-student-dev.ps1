# Network Control v2 -- Student Dev Startup
# Features:
#   1. Find available Python
#   2. Check if ports 8772/5174 are occupied, force-kill if so
#   3. Start student backend + student frontend
#
# Usage:
#   .\scripts\start-student-dev.ps1
#   .\scripts\start-student-dev.ps1 -PythonPath "C:\Python312\python.exe"

param(
    [int]$BackendPort = 8772,
    [int]$FrontendPort = 5174,
    [string]$PythonPath = ""
)

$ErrorActionPreference = "Continue"

# Ensure non-ASCII output is not garbled
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 1. Locate Python
function Find-Python {
    if ($PythonPath) {
        if (Test-Path $PythonPath) {
            return (Resolve-Path $PythonPath).Path
        }
        Write-Host "Specified Python not found: $PythonPath" -ForegroundColor Red
        exit 1
    }

    # Prefer python from PATH
    $py = Get-Command python -ErrorAction SilentlyContinue
    if ($py) {
        # Exclude Windows Store placeholder (python under Microsoft.WindowsApps opens the Store)
        $path = $py.Source
        if ($path -notlike "*WindowsApps*") {
            return $path
        }
    }

    # Search common install locations
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe"
        "C:\Python*\python.exe"
        "C:\Program Files\Python*\python.exe"
        "C:\Program Files (x86)\Python*\python.exe"
    )
    foreach ($pattern in $candidates) {
        $found = Get-Item $pattern -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1
        if ($found) {
            return $found.FullName
        }
    }

    Write-Host "No usable python.exe found. Install Python 3.10+ or pass -PythonPath explicitly." -ForegroundColor Red
    exit 1
}

# 2. Kill process by port (including child processes)
function Stop-ProcessOnPort {
    param([int]$Port)

    $conns = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if (-not $conns) {
        Write-Host "Port $Port is free" -ForegroundColor Green
        return
    }

    $pids = $conns | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique
    foreach ($pid in $pids) {
        $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
        $name = "Unknown"
        if ($proc) {
            $name = $proc.ProcessName
        }
        Write-Host "Port $Port occupied by PID $pid ($name), force killing..." -ForegroundColor Yellow
        & taskkill /PID $pid /T /F 2>&1 | Out-Null
    }

    # Wait for port release
    Start-Sleep -Milliseconds 500
}

# 3. Main flow
$pythonExe = Find-Python
Write-Host "Using Python: $pythonExe" -ForegroundColor Cyan

$root = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $root "packages\student-backend"
$frontendDir = Join-Path $root "packages\student-app"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Network Control v2 Student Dev Startup " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Stop-ProcessOnPort -Port $BackendPort
Stop-ProcessOnPort -Port $FrontendPort

Write-Host ""
Write-Host "Student Backend: http://127.0.0.1:$BackendPort" -ForegroundColor Green
Write-Host "Student Frontend: http://127.0.0.1:$FrontendPort" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

$jobs = @()

# Student Backend
$jobs += Start-Job -Name "student-backend" -ScriptBlock {
    param($dir, $py)
    Set-Location $dir
    & $py -m app.main 2>&1
} -ArgumentList $backendDir, $pythonExe

# Student Frontend
$jobs += Start-Job -Name "student-app" -ScriptBlock {
    param($dir)
    Set-Location $dir
    & npm run dev 2>&1
} -ArgumentList $frontendDir

# Stream job output
try {
    while ($true) {
        foreach ($job in $jobs) {
            if ($job.HasMoreData) {
                $output = Receive-Job -Job $job
                if ($output) {
                    $prefix = "[$($job.Name)]"
                    foreach ($line in $output) {
                        Write-Host "$prefix $line"
                    }
                }
            }
        }
        Start-Sleep -Milliseconds 200
    }
}
finally {
    Write-Host ""
    Write-Host "Stopping all services..." -ForegroundColor Yellow
    foreach ($job in $jobs) {
        Stop-Job -Job $job -ErrorAction SilentlyContinue
        Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
    }
}
