# Network Control v2 Dev Startup Script
# Start teacher backend, teacher frontend, student backend, student frontend simultaneously

$ErrorActionPreference = "Continue"

# ── UTF-8 Global Encoding Setup ──
$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8
chcp 65001 > $null
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$root = Split-Path -Parent $PSScriptRoot
$teacherBackend = Join-Path $root "packages/teacher-backend"
$studentBackend = Join-Path $root "packages/student-backend"
$teacherApp = Join-Path $root "packages/teacher-app"
$studentApp = Join-Path $root "packages/student-app"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Network Control v2 Dev Environment " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Teacher Backend: http://127.0.0.1:8771" -ForegroundColor Green
Write-Host "Student Backend: http://127.0.0.1:8772" -ForegroundColor Green
Write-Host "Teacher Frontend: http://127.0.0.1:5173" -ForegroundColor Green
Write-Host "Student Frontend: http://127.0.0.1:5174" -ForegroundColor Green
Write-Host ""

# ── Clean up stale processes ──
$ports = @(8765, 8770, 8771, 8772, 5173, 5174)
$staleFound = $false
foreach ($port in $ports) {
    $line = netstat -ano 2>$null | Select-String ":$port "
    if ($line) {
        $pidStr = ($line -split '\s+')[-1]
        if ($pidStr -match '^\d+$') {
            Write-Host "[Cleanup] Port $port occupied by PID $pidStr, terminating..." -ForegroundColor Yellow
            taskkill /F /PID $pidStr 2>$null | Out-Null
            $staleFound = $true
            Start-Sleep -Milliseconds 300
        }
    }
}
if ($staleFound) {
    Write-Host "[Cleanup] Stale processes cleaned, waiting for ports to release..." -ForegroundColor Yellow
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

$jobs = @()

# Teacher Backend
$jobs += Start-Job -Name "teacher-backend" -ScriptBlock {
    param($dir)
    $OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8
    chcp 65001 > $null
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    Set-Location $dir
    & python -m app.main
} -ArgumentList $teacherBackend

# Student Backend
$jobs += Start-Job -Name "student-backend" -ScriptBlock {
    param($dir)
    $OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8
    chcp 65001 > $null
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    Set-Location $dir
    & python -m app.main
} -ArgumentList $studentBackend

# Teacher Frontend
$jobs += Start-Job -Name "teacher-app" -ScriptBlock {
    param($dir)
    $OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8
    chcp 65001 > $null
    Set-Location $dir
    & npm run dev
} -ArgumentList $teacherApp

# Student Frontend
$jobs += Start-Job -Name "student-app" -ScriptBlock {
    param($dir)
    $OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8
    chcp 65001 > $null
    Set-Location $dir
    & npm run dev
} -ArgumentList $studentApp

# Stream job output
try {
    while ($true) {
        foreach ($job in $jobs) {
            if ($job.HasMoreData) {
                $output = Receive-Job -Job $job
                if ($output) {
                    $prefix = "[$($job.Name)]"
                    Write-Host "$prefix $output"
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
