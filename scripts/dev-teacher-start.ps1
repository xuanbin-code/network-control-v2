# Network Control v2 - 教师端开发启动脚本
# 仅启动教师端后端 + 教师端前端

$ErrorActionPreference = "Continue"
chcp 65001 > $null

$root = Split-Path -Parent $PSScriptRoot
$teacherBackend = Join-Path $root "packages/teacher-backend"
$teacherApp     = Join-Path $root "packages/teacher-app"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Network Control v2 - 教师端开发环境 " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " 教师端后端 : http://127.0.0.1:8771" -ForegroundColor Green
Write-Host " 教师端前端 : http://127.0.0.1:5173" -ForegroundColor Green
Write-Host " WebSocket  : ws://0.0.0.0:8765"    -ForegroundColor Green
Write-Host ""
Write-Host " 按 Ctrl+C 停止全部服务" -ForegroundColor Yellow
Write-Host ""

$jobs = @()

# 教师端后端
$jobs += Start-Job -Name "[teacher-backend]" -ScriptBlock {
    param($dir)
    Set-Location $dir
    & python -m app.main
} -ArgumentList $teacherBackend

# 教师端前端
$jobs += Start-Job -Name "[teacher-app]" -ScriptBlock {
    param($dir)
    Set-Location $dir
    & npm run dev
} -ArgumentList $teacherApp

# 持续输出日志
try {
    while ($true) {
        foreach ($job in $jobs) {
            if ($job.HasMoreData) {
                $output = Receive-Job -Job $job
                if ($output) {
                    Write-Host "$($job.Name) $output"
                }
            }
        }
        Start-Sleep -Milliseconds 200
    }
}
finally {
    Write-Host ""
    Write-Host "正在停止教师端服务..." -ForegroundColor Yellow
    foreach ($job in $jobs) {
        Stop-Job -Job $job -ErrorAction SilentlyContinue
        Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
    }
    Write-Host "已停止。" -ForegroundColor Cyan
}
