"""学生端本地 HTTP API：供 Electron 前端调用"""

import os
import subprocess
import sys

from fastapi import APIRouter

from .state import state
from .config import CONFIG, save_config, reload_config
from .ws_client import get_current_client
from .tray_icon import current_tray

router = APIRouter(prefix="/api")


@router.get("/health")
async def health():
    return {"status": "ok", "connected": state.connected, "mode": state.mode}


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
    # 同步托盘图标状态
    if current_tray:
        try:
            current_tray.set_net_state(mode)
        except Exception:
            pass
    return {"ok": True, "mode": mode}


@router.post("/test/black_screen")
async def test_black_screen(data: dict):
    """启动黑屏安静测试窗口。"""
    countdown = data.get("countdown_seconds", 30)
    if countdown is None:
        countdown = 0
    try:
        countdown = int(countdown)
    except (TypeError, ValueError):
        countdown = 30

    backend_dir = os.path.dirname(os.path.abspath(__file__))
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NO_WINDOW

    proc = subprocess.Popen(
        [sys.executable, "-m", "app.black_screen", str(countdown)],
        cwd=backend_dir,
        creationflags=creationflags,
    )

    return {
        "ok": True,
        "pid": proc.pid,
        "countdown_seconds": countdown,
        "infinite": countdown <= 0,
    }


@router.post("/test/black_screen_unlock")
async def test_black_screen_unlock():
    """向本地黑屏安静 IPC 服务器发送解除命令。"""
    from .black_screen import (
        DEFAULT_BLACK_SCREEN_IPC_HOST,
        DEFAULT_BLACK_SCREEN_IPC_PORT,
        send_unlock_command,
    )

    ok = send_unlock_command(
        host=DEFAULT_BLACK_SCREEN_IPC_HOST,
        port=DEFAULT_BLACK_SCREEN_IPC_PORT,
        timeout=2.0,
    )
    return {"ok": ok}
