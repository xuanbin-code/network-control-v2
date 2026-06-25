# Network Control v2 开发启动脚本
# 同时启动教师端后端、教师端前端、学生端后端、学生端前端

$ErrorActionPreference = "Continue"

$root = Split-Path -Parent $PSScriptRoot
$teacherBackend = Join-Path $root "packages/teacher-backend"
$studentBackend = Join-Path $root "packages/student-backend"
$teacherApp = Join-Path $root "packages/teacher-app"
$studentApp = Join-Path $root "packages/student-app"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Network Control v2 开发环境启动 " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "教师端后端: http://127.0.0.1:8771" -ForegroundColor Green
Write-Host "学生端后端: http://127.0.0.1:8772" -ForegroundColor Green
Write-Host "教师端前端: http://127.0.0.1:5173" -ForegroundColor Green
Write-Host "学生端前端: http://127.0.0.1:5174" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止全部服务" -ForegroundColor Yellow
Write-Host ""

$jobs = @()

# 教师端后端
$jobs += Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    & python -m app.main
} -ArgumentList $teacherBackend

# 学生端后端
$jobs += Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    & python -m app.main
} -ArgumentList $studentBackend

# 教师端前端
$jobs += Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    & npm run dev
} -ArgumentList $teacherApp

# 学生端前端
$jobs += Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    & npm run dev
} -ArgumentList $studentApp

# 持续输出各任务日志
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
    Write-Host "正在停止所有服务..." -ForegroundColor Yellow
    foreach ($job in $jobs) {
        Stop-Job -Job $job -ErrorAction SilentlyContinue
        Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
    }
}
