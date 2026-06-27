﻿# Network Control v2 - Teacher Dev Start
# Launches teacher-backend + teacher-app only

$ErrorActionPreference = "Continue"
chcp 65001 > $null

# --- Port cleanup -------------------------------------------------
$ports = @(8765, 8770, 8771, 5173)
Write-Host "Checking ports..." -ForegroundColor DarkGray

$killedIds = @{}
foreach ($port in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    foreach ($c in $conns) {
        $procId = $c.OwningProcess
        if ($procId -eq 0) { continue }
        if ($killedIds.ContainsKey($procId)) { continue }
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if (-not $proc) { continue }
        Write-Host "  Port ${port} occupied by ${procId} ($($proc.ProcessName)) - killing..." -ForegroundColor Yellow
        taskkill /PID $procId /F 2>$null | Out-Null
        $killedIds[$procId] = $true
    }
}
if ($killedIds.Count -gt 0) {
    Write-Host "  Waiting for ports to release..." -ForegroundColor DarkGray
    Start-Sleep -Seconds 2
}
Write-Host "Ports ready." -ForegroundColor DarkGray
Write-Host ""

# --- Paths --------------------------------------------------------
$root = Split-Path -Parent $PSScriptRoot
$teacherBackend = Join-Path $root "packages/teacher-backend"
$teacherApp     = Join-Path $root "packages/teacher-app"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Network Control v2 - Teacher Dev Mode " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " Teacher Backend : http://127.0.0.1:8771" -ForegroundColor Green
Write-Host " Teacher Frontend: http://127.0.0.1:5173" -ForegroundColor Green
Write-Host " WebSocket       : ws://0.0.0.0:8765"    -ForegroundColor Green
Write-Host ""
Write-Host " Press Ctrl+C to stop backend" -ForegroundColor Yellow
Write-Host ""

# --- Backend: background job --------------------------------------
$backendJob = Start-Job -Name "[backend]" -ScriptBlock {
    param($dir)
    Set-Location $dir
    & python -m app.main
} -ArgumentList $teacherBackend

# --- Frontend: new window for Electron ----------------------------
$frontendProc = Start-Process -FilePath "powershell" -ArgumentList (
    "-NoExit", "-Command",
    "chcp 65001 > `$null; Set-Location '$teacherApp'; npm run dev"
) -PassThru

# --- Monitor backend logs -----------------------------------------
try {
    while ($backendJob.State -ne 'Completed' -and $backendJob.State -ne 'Failed') {
        if ($backendJob.HasMoreData) {
            $output = Receive-Job -Job $backendJob
            if ($output) { Write-Host "[backend] $output" }
        }
        Start-Sleep -Milliseconds 200
    }
    Receive-Job -Job $backendJob | ForEach-Object { Write-Host "[backend] $_" }
}
finally {
    Write-Host ""
    Write-Host "Stopping..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job -Job $backendJob -Force -ErrorAction SilentlyContinue
    if ($frontendProc -and !$frontendProc.HasExited) {
        $frontendProc.Kill()
    }
    Write-Host "All stopped." -ForegroundColor Cyan
}
