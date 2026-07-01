#!/usr/bin/env python3
"""Translate Chinese log messages in Python files to English.

Usage:
    python scripts/translate_logs.py packages/student-backend/app/services/network_filter.py
"""
import re
import sys

# Mapping of Chinese log messages to English.
# Keys are the Chinese text inside the quotes; values are English replacements.
TRANSLATIONS = {
    "PS命令执行超时": "PowerShell command timed out",
    "PS命令失败": "PowerShell command failed",
    "规则已添加": "Rule added",
    "规则添加失败": "Rule add failed",
    "防火墙默认出站策略已设为": "Firewall default outbound action set to",
    "设置默认出站策略失败": "Failed to set default outbound action",
    "已清除所有 NC_ 防火墙规则，默认出站已恢复": "All NC_ firewall rules removed, default outbound restored",
    "开始应用白名单防火墙规则": "Applying whitelist firewall rules",
    "域名": "Domain",
    "解析到": "resolved to",
    "已放行": "Allowed",
    "个白名单 IP": "whitelist IP(s)",
    "白名单防火墙规则应用完成": "Whitelist firewall rules applied",
    "网关信息已保存": "Gateway info saved",
    "保存网关信息失败": "Failed to save gateway info",
    "解析默认路由失败": "Failed to parse default route",
    "已清除": "Cleared",
    "条白名单主机路由": "whitelist host route(s)",
    "动态添加主机路由": "Dynamically added host routes",
    "条": "",
    "Remove-NetRoute 删除 IF": "Remove-NetRoute failed for IF",
    "默认路由失败": "default route failed",
    "已删除默认路由": "Default route(s) deleted",
    "互联网已断开，局域网保留": "Internet disconnected, LAN preserved",
    "删除默认路由失败，请检查管理员权限": "Failed to delete default route; administrator rights required",
    "断网保留教师端路由": "Preserved controller route for disconnect",
    "经": "via",
    "当前无默认路由，先恢复网络以便建基线路由": "No default route; restoring network to build baseline routes",
    "默认路由恢复失败，白名单配置中止": "Failed to restore default route; whitelist configuration aborted",
    "默认路由恢复后仍不存在，白名单配置失败": "Default route still missing after restore; whitelist configuration failed",
    "无效网关 IP": "Invalid gateway IP",
    "白名单配置失败": "Whitelist configuration failed",
    "基线主机路由已添加": "Baseline host routes added",
    "条（上游 DNS + 教师端）": "(upstream DNS + controller)",
    "路由表白名单就绪": "Routing whitelist ready",
    "基线": "baseline",
    "IP，余下按 DNS 查询动态添加": "IP(s), remaining will be added dynamically on DNS query",
    "网卡 DNS 已设置为": "Adapter DNS set to",
    "设置网卡 DNS 失败": "Failed to set adapter DNS",
    "网卡 DNS 已恢复为自动获取": "Adapter DNS restored to DHCP",
    "恢复网卡 DNS 失败": "Failed to restore adapter DNS",
    "切换到模式": "Switched to mode",
    "恢复正常路由/DNS": "Restored normal routing/DNS",
    "启用白名单过滤（路由表动态放行）": "Enabled whitelist filtering (dynamic routing)",
    "启用黑名单过滤（仅 DNS 拦截）": "Enabled blacklist filtering (DNS only)",
    "断开默认网络，保留到教师端路由": "Disconnected default network, preserved controller route",
    "默认路由已存在，无需恢复": "Default route already exists, no restore needed",
    "读取网关备份失败": "Failed to read gateway backup",
    "将尝试 DHCP 续约": "will try DHCP renew",
    "已恢复默认路由": "Default route restored",
    "恢复路由失败": "Failed to restore route",
    "路由表已确认存在": "Route table confirmed with",
    "条默认路由": "default route(s)",
    "恢复后路由表中仍无默认路由": "Still no default route after restore",
    "部分路由恢复失败，保留备份文件以供下次重试": "Some routes failed to restore; keeping backup for retry",
    "无网关备份，尝试 DHCP 续约恢复路由": "No gateway backup; trying DHCP renew to restore routes",
    "配置路由表白名单（动态模式）": "Configuring routing whitelist (dynamic mode)",
    "主机路由失败": "Host route failed",
    "，": ", ",
    "。": ".",
    "！": "!",
    "（": "(",
    "）": ")",
}


def translate_file(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    replaced = 0
    # Replace messages inside logger calls and plain strings.
    for cn, en in TRANSLATIONS.items():
        new_content, count = re.subn(re.escape(cn), en, content)
        if count:
            content = new_content
            replaced += count

    # Clean up any empty parentheses artifacts from removing "条".
    content = re.sub(r"\s+\)", ")", content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return replaced


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python translate_logs.py <file>")
        sys.exit(1)
    total = 0
    for file_path in sys.argv[1:]:
        n = translate_file(file_path)
        print(f"{file_path}: {n} replacements")
        total += n
    print(f"Total replacements: {total}")
