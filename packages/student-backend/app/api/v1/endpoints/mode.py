"""模式切换（供前端测试）"""

import asyncio

from fastapi import APIRouter

from shared.protocol import FilterMode

from app.core.state import state
from app.services.network_filter import apply_filter_mode, clear_dns_cache
from app.services.tray_icon import current_tray

router = APIRouter()


@router.post("/apply_mode")
async def apply_mode(data: dict):
    """供前端测试：直接切换到指定模式"""
    mode = data.get("mode", FilterMode.NORMAL)
    state.set_mode(mode)
    # 网络过滤涉及 PowerShell/路由表/DNS 等系统命令，必须进线程池避免阻塞事件循环
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None,
        apply_filter_mode,
        mode,
        state.whitelist_domains,
        state.blacklist_domains,
        state.lan_subnets,
        state.controller_ip,
        state.upstream_dns,
    )
    # 同步本地 DNS 服务器模式，使白名单/黑名单过滤生效
    dns = getattr(state, "dns_server", None)
    if dns and dns.running:
        try:
            if mode == FilterMode.WHITELIST:
                dns.set_mode(FilterMode.WHITELIST)
                dns.update_domains(state.whitelist_domains)
            elif mode == FilterMode.BLACKLIST:
                dns.set_mode(FilterMode.BLACKLIST)
                dns.update_domains(state.blacklist_domains)
            else:
                dns.set_mode(FilterMode.NORMAL)
        except Exception:
            pass
    # 清除 DNS 缓存，避免浏览器使用旧解析结果
    try:
        await loop.run_in_executor(None, clear_dns_cache)
    except Exception:
        pass
    # 同步托盘图标状态
    if current_tray:
        try:
            current_tray.set_net_state(mode)
        except Exception:
            pass
    return {"ok": True, "mode": mode}
