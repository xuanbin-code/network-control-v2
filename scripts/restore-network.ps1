# 一键恢复网络脚本
#
# 用途：当 student-backend 异常退出导致网络未恢复时，运行此脚本一键还原：
#   1. DNS 自动获取
#   2. 防火墙默认出站策略恢复为 Allow
#   3. 删除所有 NC_ 前缀的防火墙规则
#   4. 恢复默认路由（优先读取 gw_backup.json，否则 DHCP 续约）
#
# 运行方式（需要管理员权限）：
#   右键 PowerShell → 以管理员身份运行
#   cd d:\A_MY_CODE_WORK\network-control-v2
#   .\scripts\restore-network.ps1

param(
    [string]$BackendDir = "$PSScriptRoot\..\packages\student-backend"
)

function Write-Info($msg) {
    Write-Host "[恢复网络] $msg" -ForegroundColor Cyan
}

function Write-Ok($msg) {
    Write-Host "[OK] $msg" -ForegroundColor Green
}

function Write-Warn($msg) {
    Write-Host "[WARN] $msg" -ForegroundColor Yellow
}

# 检查管理员权限
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warn "当前不是管理员权限，部分网络恢复操作会失败。"
    Write-Warn "请右键 PowerShell 选择「以管理员身份运行」后重新执行。"
}

Write-Info "开始恢复网络..."

# 1. 恢复 DNS 自动获取
Write-Info "恢复网卡 DNS 为自动获取..."
try {
    Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | ForEach-Object {
        Set-DnsClientServerAddress -InterfaceAlias $_.Name -ResetServerAddresses -ErrorAction SilentlyContinue
    }
    Write-Ok "DNS 已恢复为自动获取"
} catch {
    Write-Warn "恢复 DNS 失败: $_"
}

# 2. 恢复防火墙默认出站策略
Write-Info "恢复防火墙默认出站策略为 Allow..."
try {
    Set-NetFirewallProfile -All -DefaultOutboundAction Allow -ErrorAction Stop
    Write-Ok "防火墙默认出站策略已恢复为 Allow"
} catch {
    Write-Warn "恢复防火墙默认出站策略失败: $_"
}

# 3. 删除 NC_ 前缀防火墙规则
Write-Info "删除 NC_ 前缀防火墙规则..."
try {
    Get-NetFirewallRule | Where-Object { $_.DisplayName -like "NC_*" } | Remove-NetFirewallRule -ErrorAction SilentlyContinue
    Write-Ok "已删除 NC_ 防火墙规则"
} catch {
    Write-Warn "删除 NC_ 防火墙规则失败: $_"
}

# 4. 恢复默认路由
Write-Info "恢复默认路由..."
$backupFile = Join-Path $BackendDir "gw_backup.json"
$pythonAvailable = $false

# 优先尝试用 Python 恢复（会读取 gw_backup.json）
try {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        $pythonCmd = Get-Command py -ErrorAction SilentlyContinue
    }

    if ($pythonCmd) {
        Push-Location $BackendDir
        $script = @"
import sys
sys.path.insert(0, '../..')
try:
    from app.services.network_filter import reconnect_internet
    reconnect_internet()
    print('ROUTE_RESTORED')
except Exception as e:
    print(f'ROUTE_FAILED: {e}')
"@
        $result = & $pythonCmd.Name -c $script 2>&1
        Pop-Location

        if ($result -like "*ROUTE_RESTORED*") {
            Write-Ok "默认路由已通过 Python 恢复"
            $pythonAvailable = $true
        } else {
            Write-Warn "Python 恢复路由失败: $result"
        }
    }
} catch {
    Write-Warn "调用 Python 恢复路由失败: $_"
}

# 兜底：删除残留默认路由 + DHCP 续约
if (-not $pythonAvailable) {
    Write-Info "尝试通过 DHCP 续约恢复路由..."
    try {
        # 先删除所有 0.0.0.0/0 路由（避免冲突）
        Get-NetRoute -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue |
            Remove-NetRoute -Confirm:$false -ErrorAction SilentlyContinue

        # 对每张在线网卡执行 DHCP 续约
        Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and $_.Name -notmatch "Loopback" } | ForEach-Object {
            ipconfig /renew $_.Name | Out-Null
        }
        Write-Ok "DHCP 续约完成"
    } catch {
        Write-Warn "DHCP 续约失败: $_"
    }
}

# 5. 清理 DNS 缓存
Write-Info "清理 DNS 缓存..."
try {
    Clear-DnsClientCache -ErrorAction SilentlyContinue
    Write-Ok "DNS 缓存已清理"
} catch {
    Write-Warn "清理 DNS 缓存失败: $_"
}

# 6. 可选：删除网关备份文件
if (Test-Path $backupFile) {
    Write-Info "删除旧的网关备份文件..."
    try {
        Remove-Item $backupFile -Force -ErrorAction SilentlyContinue
        Write-Ok "已删除 gw_backup.json"
    } catch {
        Write-Warn "删除 gw_backup.json 失败: $_"
    }
}

Write-Info "网络恢复脚本执行完毕。"
Write-Info "如果仍无法上网，请尝试重启电脑。"

# 显示当前默认路由和 DNS 供检查
Write-Host ""
Write-Host "===== 当前默认路由 =====" -ForegroundColor Gray
Get-NetRoute -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue |
    Select-Object -Property InterfaceAlias, NextHop, RouteMetric |
    Format-Table -AutoSize

Write-Host "===== 当前 DNS 设置 =====" -ForegroundColor Gray
Get-DnsClientServerAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.ServerAddresses } |
    Select-Object -Property InterfaceAlias, ServerAddresses |
    Format-Table -AutoSize
