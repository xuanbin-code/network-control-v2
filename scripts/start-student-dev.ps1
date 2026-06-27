# Network Control v2 — 学生端开发启动脚本
# 功能：
#   1. 查找可用 Python
#   2. 检查 8772 / 5174 端口是否被占用，若占用则强制结束对应进程
#   3. 启动学生端后端 + 学生端前端
#
# 用法：
#   .\scripts\start-student-dev.ps1
#   .\scripts\start-student-dev.ps1 -PythonPath "C:\Python312\python.exe"

param(
    [int]$BackendPort = 8772,
    [int]$FrontendPort = 5174,
    [string]$PythonPath = ""
)

$ErrorActionPreference = "Continue"

# 保证中文输出不乱码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 1. 定位 Python
function Find-Python {
    if ($PythonPath) {
        if (Test-Path $PythonPath) {
            return (Resolve-Path $PythonPath).Path
        }
        Write-Host "指定的 Python 不存在: $PythonPath" -ForegroundColor Red
        exit 1
    }

    # 优先使用 PATH 中的 python
    $py = Get-Command python -ErrorAction SilentlyContinue
    if ($py) {
        # 排除 Windows Store 的占位符（ Microsoft.WindowsApps 路径下的 python 会弹商店）
        $path = $py.Source
        if ($path -notlike "*WindowsApps*") {
            return $path
        }
    }

    # 搜索常见安装位置
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

    Write-Host "未找到可用的 python.exe，请安装 Python 3.10+ 或显式传入 -PythonPath" -ForegroundColor Red
    exit 1
}

# 2. 根据端口结束进程（包含子进程）
function Stop-ProcessOnPort {
    param([int]$Port)

    $conns = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if (-not $conns) {
        Write-Host "端口 $Port 未被占用" -ForegroundColor Green
        return
    }

    $pids = $conns | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique
    foreach ($pid in $pids) {
        $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
        $name = "未知"
        if ($proc) {
            $name = $proc.ProcessName
        }
        Write-Host "端口 $Port 被 PID $pid ($name) 占用，正在强制结束..." -ForegroundColor Yellow
        & taskkill /PID $pid /T /F 2>&1 | Out-Null
    }

    # 稍等端口释放
    Start-Sleep -Milliseconds 500
}

# 3. 主流程
$pythonExe = Find-Python
Write-Host "使用 Python: $pythonExe" -ForegroundColor Cyan

$root = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $root "packages\student-backend"
$frontendDir = Join-Path $root "packages\student-app"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Network Control v2 学生端开发启动 " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Stop-ProcessOnPort -Port $BackendPort
Stop-ProcessOnPort -Port $FrontendPort

Write-Host ""
Write-Host "学生端后端: http://127.0.0.1:$BackendPort" -ForegroundColor Green
Write-Host "学生端前端: http://127.0.0.1:$FrontendPort" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止全部服务" -ForegroundColor Yellow
Write-Host ""

$jobs = @()

# 学生端后端
$jobs += Start-Job -Name "student-backend" -ScriptBlock {
    param($dir, $py)
    Set-Location $dir
    & $py -m app.main 2>&1
} -ArgumentList $backendDir, $pythonExe

# 学生端前端
$jobs += Start-Job -Name "student-app" -ScriptBlock {
    param($dir)
    Set-Location $dir
    & npm run dev 2>&1
} -ArgumentList $frontendDir

# 持续输出各任务日志
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
    Write-Host "正在停止所有服务..." -ForegroundColor Yellow
    foreach ($job in $jobs) {
        Stop-Job -Job $job -ErrorAction SilentlyContinue
        Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
    }
}
