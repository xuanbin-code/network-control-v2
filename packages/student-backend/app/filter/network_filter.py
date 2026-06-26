"""Windows 网络过滤控制

使用 PowerShell New-NetFirewallRule / Remove-NetFirewallRule、route 命令、
网卡 DNS 设置实现四种模式：
  - normal：恢复默认网关与 DNS，清除规则
  - whitelist：本地 DNS + 路由表动态放行白名单域名
  - blacklist：本地 DNS 拦截黑名单，其余正常
  - disconnect：删除默认路由，保留到教师端路由

迁移自原 Network_Control 项目的 firewall.py，适配当前 v2 路径与状态对象。
"""

import json
import logging
import os
import socket
import subprocess
import sys
import threading
import time
from typing import Optional

from shared.protocol import FilterMode

logger = logging.getLogger("network_filter")

RULE_PREFIX = "NC_"


def _run_ps(cmd: str, timeout: int = 15) -> tuple[bool, str]:
    result = subprocess.run(
        ["powershell", "-NonInteractive", "-Command", cmd],
        capture_output=True, text=True, timeout=timeout,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    ok = result.returncode == 0
    out = (result.stdout + result.stderr).strip()
    if not ok:
        logger.debug(f"PS命令失败: {cmd[:200]}\n{out}")
    return ok, out


def _ps_addr(addr: str) -> str:
    if "," in addr:
        parts = [p.strip() for p in addr.split(",") if p.strip()]
        return ",".join(f'"{p}"' for p in parts)
    return f'"{addr}"'


def _add_rule(name: str, direction: str, protocol: str,
              remote_addr: str = "Any", remote_port: str = "Any",
              local_port: str = "Any", action: str = "Allow") -> bool:
    full_name = RULE_PREFIX + name
    _run_ps(f'Remove-NetFirewallRule -DisplayName "{full_name}" -ErrorAction SilentlyContinue')
    cmd = (
        f'New-NetFirewallRule -DisplayName "{full_name}" '
        f'-Direction {direction} -Protocol {protocol} '
        f'-RemoteAddress {_ps_addr(remote_addr)} '
        f'-RemotePort "{remote_port}" '
        f'-LocalPort "{local_port}" '
        f'-Action {action} -Enabled True -Profile Any'
    )
    ok, out = _run_ps(cmd)
    if ok:
        logger.debug(f"规则已添加: {full_name}")
    else:
        logger.warning(f"规则添加失败: {full_name} -> {out}")
    return ok


def _set_default_outbound(action: str) -> bool:
    cmd = f'Set-NetFirewallProfile -All -DefaultOutboundAction {action}'
    ok, out = _run_ps(cmd)
    if ok:
        logger.info(f"防火墙默认出站策略已设为: {action}")
    else:
        logger.warning(f"设置默认出站策略失败: {out}")
    return ok


def remove_all_rules():
    """恢复默认放行，并清除所有 NC_ 规则"""
    _set_default_outbound("Allow")
    cmd = f'Get-NetFirewallRule | Where-Object {{$_.DisplayName -like "{RULE_PREFIX}*"}} | Remove-NetFirewallRule -ErrorAction SilentlyContinue'
    ok, out = _run_ps(cmd)
    logger.info("已清除所有 NC_ 防火墙规则，默认出站已恢复")
    return ok


def resolve_domain_ips(domain: str) -> list[str]:
    domain = domain.lstrip("*.").strip()
    try:
        infos = socket.getaddrinfo(domain, None)
        ips = list({info[4][0] for info in infos if ":" not in info[4][0]})
        return ips
    except Exception:
        return []


def _add_common_allow_rules(lan_subnets: list[str], controller_ip: str):
    _add_rule("Allow_Loopback", "Outbound", "Any", remote_addr="127.0.0.0/8")
    for subnet in lan_subnets:
        safe_name = subnet.replace("/", "_").replace(".", "_")
        _add_rule(f"Allow_LAN_{safe_name}", "Outbound", "Any", remote_addr=subnet)
    if controller_ip:
        _add_rule("Allow_Controller", "Outbound", "Any", remote_addr=controller_ip)


def apply_whitelist_rules(whitelist_domains: list[str],
                          lan_subnets: list[str],
                          controller_ip: str,
                          upstream_dns: str):
    """防火墙白名单方案（兜底/兼容）：默认封锁 + 放行白名单 IP。
    当前 v2 主要使用路由表白名单，本函数作为备用入口保留。
    """
    logger.info("开始应用白名单防火墙规则...")
    remove_all_rules()
    _add_common_allow_rules(lan_subnets, controller_ip)

    whitelist_ips: set[str] = set()
    for domain in whitelist_domains:
        bare = domain.lstrip("*").lstrip(".").strip()
        if not bare:
            continue
        ips = resolve_domain_ips(bare)
        whitelist_ips.update(ips)
        logger.debug(f"域名 {bare} 解析到 {ips}")

    if whitelist_ips:
        ip_list = ",".join(sorted(whitelist_ips))
        _add_rule("Allow_Whitelist_IPs", "Outbound", "Any", remote_addr=ip_list)
        logger.info(f"已放行 {len(whitelist_ips)} 个白名单 IP")

    if upstream_dns:
        _add_rule("Allow_UpstreamDNS", "Outbound", "UDP",
                  remote_addr=upstream_dns, remote_port="53")

    _set_default_outbound("Block")
    logger.info("白名单防火墙规则应用完成")


# ── 路由表方案（v2 主推）──────────────────────────────────────────

_GW_BACKUP_FILE: str = ""


def _gw_backup_path() -> str:
    global _GW_BACKUP_FILE
    if not _GW_BACKUP_FILE:
        if getattr(sys, "frozen", False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        _GW_BACKUP_FILE = os.path.join(base, "gw_backup.json")
    return _GW_BACKUP_FILE


def _get_default_gateways() -> list[dict]:
    cmd = (
        'Get-NetRoute -DestinationPrefix "0.0.0.0/0" '
        '| Select-Object NextHop, InterfaceIndex, RouteMetric '
        '| ConvertTo-Json -Compress'
    )
    ok, out = _run_ps(cmd)
    if not ok or not out.strip():
        return []
    try:
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]
        return data
    except Exception as e:
        logger.debug(f"解析默认路由失败: {e} raw={out[:200]}")
        return []


def _ps_metric_arg(metric) -> str:
    try:
        m = int(metric)
    except (TypeError, ValueError):
        return ""
    return f"-RouteMetric {m}" if m > 0 else ""


_whitelist_host_routes: set[str] = set()
_cached_gateway: tuple[str, int] = ("", 0)
_dynamic_routes_lock = threading.Lock()


def _clean_whitelist_routes():
    global _whitelist_host_routes, _cached_gateway
    with _dynamic_routes_lock:
        if not _whitelist_host_routes:
            _cached_gateway = ("", 0)
            return
        ips = list(_whitelist_host_routes)
        _whitelist_host_routes.clear()
        _cached_gateway = ("", 0)

    parts = [
        f'try {{ Remove-NetRoute -DestinationPrefix "{ip}/32" -Confirm:$false -ErrorAction SilentlyContinue }} catch {{}};'
        for ip in ips
    ]
    script = " ".join(parts)
    _run_ps(script, timeout=60)
    logger.debug(f"已清除 {len(ips)} 条白名单主机路由")


def add_host_routes_dynamic(ips: list[str]) -> set[str]:
    """运行时把上游 DNS 返回的 IP 加进白名单路由表。
    由 DNS 服务器在每次解析白名单域名后调用。
    """
    global _whitelist_host_routes, _cached_gateway
    with _dynamic_routes_lock:
        gw_ip, gw_idx = _cached_gateway
        if not gw_ip:
            return set()
        new_ips = [ip for ip in ips if ip and ip not in _whitelist_host_routes]
        if not new_ips:
            return set()
        _whitelist_host_routes.update(new_ips)

    added = _add_host_routes_bulk(new_ips, gw_ip, gw_idx)
    failed = set(new_ips) - added
    if failed:
        with _dynamic_routes_lock:
            _whitelist_host_routes.difference_update(failed)
    if added:
        logger.debug(f"动态添加主机路由 {len(added)} 条: {sorted(added)[:5]}{'...' if len(added) > 5 else ''}")
    return added


def _delete_default_route() -> bool:
    gateways = _get_default_gateways()
    if not gateways:
        return True
    try:
        with open(_gw_backup_path(), "w", encoding="utf-8") as f:
            json.dump(gateways, f)
        logger.debug(f"网关信息已保存: {gateways}")
    except Exception as e:
        logger.warning(f"保存网关信息失败: {e}")

    ok, out = _run_ps('route DELETE 0.0.0.0 MASK 0.0.0.0')
    if ok:
        logger.info(f"已删除默认路由（共 {len(gateways)} 条），互联网已断开，局域网保留")
    else:
        logger.warning(f"删除默认路由失败: {out}")
    return ok


def disconnect_internet(controller_ip: str = "") -> bool:
    """彻底断网。若给了 controller_ip，删默认路由前先保留到教师端的路由。"""
    global _whitelist_host_routes
    _clean_whitelist_routes()
    if controller_ip:
        gws = _get_default_gateways()
        if gws:
            gw = gws[0]
            gw_ip = gw.get("NextHop", "")
            gw_idx = gw.get("InterfaceIndex", 0)
            if gw_ip and gw_ip not in ("0.0.0.0", "::", ""):
                added = _add_host_routes_bulk([controller_ip], gw_ip, gw_idx)
                _whitelist_host_routes |= added
                logger.info(f"断网保留教师端路由: {controller_ip} 经 {gw_ip}")
    return _delete_default_route()


def has_internet_route() -> bool:
    return bool(_get_default_gateways())


def reconnect_internet() -> bool:
    """恢复默认网关路由，优先读取备份，否则 DHCP 续约。"""
    _clean_whitelist_routes()
    if _get_default_gateways():
        logger.info("默认路由已存在，无需恢复")
        return True

    backup = _gw_backup_path()
    gateways = []
    if os.path.exists(backup):
        try:
            with open(backup, "r", encoding="utf-8") as f:
                gateways = json.load(f)
        except Exception as e:
            logger.warning(f"读取网关备份失败: {e}，将尝试 DHCP 续约")

    if gateways:
        success = True
        for gw in gateways:
            nh = gw.get("NextHop", "")
            idx = gw.get("InterfaceIndex", 0)
            metric = gw.get("RouteMetric", 0)
            if not nh or nh in ("0.0.0.0", "::", ""):
                continue
            _run_ps(
                f'Remove-NetRoute -DestinationPrefix "0.0.0.0/0" '
                f'-InterfaceIndex {idx} -Confirm:$false -ErrorAction SilentlyContinue'
            )
            metric_arg = _ps_metric_arg(metric)
            ok, out = _run_ps(
                f'New-NetRoute -DestinationPrefix "0.0.0.0/0" '
                f'-NextHop "{nh}" -InterfaceIndex {idx} '
                f'{metric_arg} -ErrorAction Stop'
            )
            if ok:
                logger.info(f"已恢复默认路由: {nh} (IF {idx})")
            else:
                logger.warning(f"恢复路由失败: {out}")
                success = False
        verify = _get_default_gateways()
        if verify:
            logger.info(f"路由表已确认存在 {len(verify)} 条默认路由")
        else:
            logger.warning("恢复后路由表中仍无默认路由！")
            success = False
        if success:
            try:
                os.remove(backup)
            except Exception:
                pass
        else:
            logger.warning("部分路由恢复失败，保留备份文件以供下次重试")
        return success
    else:
        logger.info("无网关备份，尝试 DHCP 续约恢复路由...")
        ok, out = _run_ps(
            'Get-NetAdapter | Where-Object {$_.Status -eq "Up" -and $_.Name -notmatch "Loopback"} '
            '| ForEach-Object { ipconfig /renew $_.Name }'
        )
        return ok


def apply_whitelist_routing(whitelist_domains: list[str],
                            lan_subnets: list[str],
                            controller_ip: str,
                            upstream_dns: str) -> bool:
    """路由表白名单（动态加路由方案）：
      Phase 1: 确保默认路由存在
      Phase 2: 缓存网关 → 加基线路由（upstream_dns + controller_ip）
      Phase 3: 删除默认路由，后续 DNS 查询动态加路由
    """
    global _whitelist_host_routes, _cached_gateway
    logger.info("配置路由表白名单（动态模式）...")

    _clean_whitelist_routes()

    if not _get_default_gateways():
        logger.info("当前无默认路由，先恢复网络以便建基线路由")
        if not reconnect_internet():
            logger.error("默认路由恢复失败，白名单配置中止")
            return False
        time.sleep(0.5)

    gateways = _get_default_gateways()
    if not gateways:
        logger.error("默认路由恢复后仍不存在，白名单配置失败")
        return False

    gw = gateways[0]
    gw_ip = gw.get("NextHop", "")
    gw_idx = gw.get("InterfaceIndex", 0)
    if not gw_ip or gw_ip in ("0.0.0.0", "::", ""):
        logger.error(f"无效网关 IP '{gw_ip}'，白名单配置失败")
        return False

    set_adapter_dns("127.0.0.1")

    baseline: set[str] = set()
    if upstream_dns:
        baseline.add(upstream_dns)
    if controller_ip:
        baseline.add(controller_ip)

    added = _add_host_routes_bulk(sorted(baseline), gw_ip, gw_idx)
    logger.info(f"基线主机路由已添加 {len(added)}/{len(baseline)} 条（上游 DNS + 教师端）")

    with _dynamic_routes_lock:
        _whitelist_host_routes = set(added)
        _cached_gateway = (gw_ip, gw_idx)

    _delete_default_route()

    _run_ps('Clear-DnsClientCache -ErrorAction SilentlyContinue')
    logger.info(f"路由表白名单就绪：基线 {len(added)} IP，余下按 DNS 查询动态添加")
    return True


def _add_host_routes_bulk(ips: list[str], gw_ip: str, gw_idx: int) -> set[str]:
    if not ips:
        return set()
    parts = []
    for ip in ips:
        parts.append(
            f'try {{ Remove-NetRoute -DestinationPrefix "{ip}/32" -Confirm:$false -ErrorAction SilentlyContinue }} catch {{}};'
            f'try {{ New-NetRoute -DestinationPrefix "{ip}/32" -NextHop "{gw_ip}" '
            f'-InterfaceIndex {gw_idx} -RouteMetric 1 -ErrorAction Stop | Out-Null; '
            f'Write-Output "OK {ip}" }} catch {{ Write-Output "FAIL {ip} $($_.Exception.Message)" }};'
        )
    script = " ".join(parts)
    ok, out = _run_ps(script, timeout=120)
    added: set[str] = set()
    for line in (out or "").splitlines():
        line = line.strip()
        if line.startswith("OK "):
            added.add(line[3:].strip())
        elif line.startswith("FAIL "):
            logger.warning(f"主机路由失败: {line[5:][:120]}")
    return added


def set_adapter_dns(dns_ip: str = "127.0.0.1"):
    cmd = (
        'Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | ForEach-Object {'
        f'Set-DnsClientServerAddress -InterfaceAlias $_.Name -ServerAddresses "{dns_ip}"'
        '}'
    )
    ok, out = _run_ps(cmd)
    if ok:
        logger.info(f"网卡 DNS 已设置为 {dns_ip}")
    else:
        logger.warning(f"设置网卡 DNS 失败: {out}")
    return ok


def restore_adapter_dns():
    cmd = (
        'Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | ForEach-Object {'
        'Set-DnsClientServerAddress -InterfaceAlias $_.Name -ResetServerAddresses'
        '}'
    )
    ok, out = _run_ps(cmd)
    if ok:
        logger.info("网卡 DNS 已恢复为自动获取")
    else:
        logger.warning(f"恢复网卡 DNS 失败: {out}")
    return ok


# ── 模式统一入口 ────────────────────────────────────────────────

def apply_filter_mode(mode: str,
                      whitelist_domains: Optional[list[str]] = None,
                      blacklist_domains: Optional[list[str]] = None,
                      lan_subnets: Optional[list[str]] = None,
                      controller_ip: str = "",
                      upstream_dns: str = "114.114.114.114"):
    """应用网络过滤模式。实际会操作 Windows 路由/防火墙/DNS。"""
    logger.info(f"切换到模式: {mode}")
    if mode == FilterMode.NORMAL:
        _enable_network()
    elif mode == FilterMode.WHITELIST:
        _enable_whitelist(whitelist_domains or [], lan_subnets or [], controller_ip, upstream_dns)
    elif mode == FilterMode.BLACKLIST:
        _enable_blacklist(blacklist_domains or [], upstream_dns)
    elif mode == FilterMode.DISCONNECT:
        _disable_network(controller_ip, upstream_dns)


def _enable_network():
    logger.info("恢复正常路由/DNS")
    remove_all_rules()
    restore_adapter_dns()
    reconnect_internet()


def _enable_whitelist(whitelist_domains: list[str],
                      lan_subnets: list[str],
                      controller_ip: str,
                      upstream_dns: str):
    logger.info("启用白名单过滤（路由表动态放行）")
    # 先恢复正常，确保能拿到网关
    _enable_network()
    apply_whitelist_routing(whitelist_domains, lan_subnets, controller_ip, upstream_dns)


def _enable_blacklist(blacklist_domains: list[str], upstream_dns: str):
    logger.info("启用黑名单过滤（仅 DNS 拦截）")
    _enable_network()
    # 黑名单模式由 dns_server 负责拦截，这里只需确保网络正常、DNS 指向本地
    set_adapter_dns("127.0.0.1")


def _disable_network(controller_ip: str = "", upstream_dns: str = "114.114.114.114"):
    logger.info("断开默认网络，保留到教师端路由")
    remove_all_rules()
    set_adapter_dns(upstream_dns)
    disconnect_internet(controller_ip)
