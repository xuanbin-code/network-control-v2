# One-click Network Restore Script
#
# Purpose: When student-backend exits abnormally without restoring network,
# run this script to restore with one click:
#   1. DNS to auto-obtain
#   2. Firewall default outbound policy restored to Allow
#   3. Delete all NC_ prefixed firewall rules
#   4. Restore default route (prefer gw_backup.json, fallback DHCP renew)
#   5. Flush DNS cache
#   6. Optionally delete old gateway backup file
#
# Usage (admin required):
#   Right-click PowerShell -> Run as administrator
#   cd d:\A_MY_CODE_WORK\network-control-v2
#   .\scripts\restore-network.ps1

param(
    [string]$BackendDir = "$PSScriptRoot\..\packages\student-backend"
)

function Write-Info($msg) {
    Write-Host "[Restore Network] $msg" -ForegroundColor Cyan
}

function Write-Ok($msg) {
    Write-Host "[OK] $msg" -ForegroundColor Green
}

function Write-Warn($msg) {
    Write-Host "[WARN] $msg" -ForegroundColor Yellow
}

# Check admin privileges
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warn "Not running as admin, some network restore operations will fail."
    Write-Warn "Right-click PowerShell, select `"Run as administrator`", then re-run."
}

Write-Info "Starting network restore..."

# 1. Restore DNS to auto-obtain
Write-Info "Restoring adapter DNS to auto-obtain..."
try {
    Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | ForEach-Object {
        Set-DnsClientServerAddress -InterfaceAlias $_.Name -ResetServerAddresses -ErrorAction SilentlyContinue
    }
    Write-Ok "DNS restored to auto-obtain"
} catch {
    Write-Warn "Failed to restore DNS: $_"
}

# 2. Restore firewall default outbound policy
Write-Info "Restoring firewall default outbound policy to Allow..."
try {
    Set-NetFirewallProfile -All -DefaultOutboundAction Allow -ErrorAction Stop
    Write-Ok "Firewall default outbound policy restored to Allow"
} catch {
    Write-Warn "Failed to restore firewall default outbound policy: $_"
}

# 3. Delete NC_ prefixed firewall rules
Write-Info "Deleting NC_ prefixed firewall rules..."
try {
    Get-NetFirewallRule | Where-Object { $_.DisplayName -like "NC_*" } | Remove-NetFirewallRule -ErrorAction SilentlyContinue
    Write-Ok "NC_ firewall rules deleted"
} catch {
    Write-Warn "Failed to delete NC_ firewall rules: $_"
}

# 4. Restore default route
Write-Info "Restoring default route..."
$backupFile = Join-Path $BackendDir "gw_backup.json"
$pythonAvailable = $false

# Prefer Python restore (reads gw_backup.json)
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
            Write-Ok "Default route restored via Python"
            $pythonAvailable = $true
        } else {
            Write-Warn "Python route restore failed: $result"
        }
    }
} catch {
    Write-Warn "Failed to invoke Python for route restore: $_"
}

# Fallback: delete leftover default routes + DHCP renew
if (-not $pythonAvailable) {
    Write-Info "Attempting route restore via DHCP renew..."
    try {
        # Delete all 0.0.0.0/0 routes first (avoid conflicts)
        Get-NetRoute -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue |
            Remove-NetRoute -Confirm:$false -ErrorAction SilentlyContinue

        # DHCP renew on every online (non-loopback) adapter
        Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and $_.Name -notmatch "Loopback" } | ForEach-Object {
            ipconfig /renew $_.Name | Out-Null
        }
        Write-Ok "DHCP renew complete"
    } catch {
        Write-Warn "DHCP renew failed: $_"
    }
}

# 5. Flush DNS cache
Write-Info "Flushing DNS cache..."
try {
    Clear-DnsClientCache -ErrorAction SilentlyContinue
    Write-Ok "DNS cache flushed"
} catch {
    Write-Warn "Failed to flush DNS cache: $_"
}

# 6. Optionally delete old gateway backup file
if (Test-Path $backupFile) {
    Write-Info "Deleting old gateway backup file..."
    try {
        Remove-Item $backupFile -Force -ErrorAction SilentlyContinue
        Write-Ok "Deleted gw_backup.json"
    } catch {
        Write-Warn "Failed to delete gw_backup.json: $_"
    }
}

Write-Info "Network restore script completed."
Write-Info "If you still cannot access the internet, try restarting your computer."

# Display current default route and DNS for inspection
Write-Host ""
Write-Host "===== Current Default Route =====" -ForegroundColor Gray
Get-NetRoute -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue |
    Select-Object -Property InterfaceAlias, NextHop, RouteMetric |
    Format-Table -AutoSize

Write-Host "===== Current DNS Settings =====" -ForegroundColor Gray
Get-DnsClientServerAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.ServerAddresses } |
    Select-Object -Property InterfaceAlias, ServerAddresses |
    Format-Table -AutoSize
