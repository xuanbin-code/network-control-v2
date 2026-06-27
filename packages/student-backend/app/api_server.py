"""学生端本地 HTTP API：供 Electron 前端调用"""

from fastapi import APIRouter

from .state import state
from .config import CONFIG, save_config, reload_config
from .ws_client import get_current_client

router = APIRouter(prefix="/api")


@router.get("/health")
async def health():
    return {"status": "ok", "connected": state.connected, "mode": state.mode}


@router.get("/test_message")
async def get_test_message():
    """获取最近一条教师端发来的测试消息"""
    import time
    return {
        "message": state.last_test_message,
        "ts": state.last_test_message_ts,
        "time_str": time.strftime("%Y-%m-%d %H:%M:%S",
                                   time.localtime(state.last_test_message_ts))
        if state.last_test_message_ts else "",
    }


@router.get("/status")
async def get_status():
    return {
        "mode": state.mode,
        "connected": state.connected,
        "controller_url": CONFIG.get("controller_url"),
        "controller_ip": state.controller_ip,
        "hostname": state.hostname,
        "mac": state.mac,
        "filter_active": state.filter_active,
        "dns_running": state.dns_running,
        "rule_count": state.rule_count,
    }


@router.get("/config")
async def get_config():
    return CONFIG


@router.post("/config")
async def update_config(data: dict):
    CONFIG.update(data)
    save_config(CONFIG)
    return {"ok": True}


@router.post("/reload_config")
async def reload_config_endpoint():
    """重新加载 config.json，便于调试。"""
    cfg = reload_config()
    client = get_current_client()
    if client:
        client.reload_uri()
    return {"ok": True, "config": cfg}


@router.post("/apply_mode")
async def apply_mode(data: dict):
    """供前端测试：直接切换到指定模式"""
    from shared.protocol import FilterMode
    from .filter.network_filter import apply_filter_mode
    mode = data.get("mode", FilterMode.NORMAL)
    state.set_mode(mode)
    apply_filter_mode(
        mode,
        whitelist_domains=state.whitelist_domains,
        blacklist_domains=state.blacklist_domains,
        lan_subnets=state.lan_subnets,
        controller_ip=state.controller_ip,
        upstream_dns=state.upstream_dns,
    )
    return {"ok": True, "mode": mode}
