"""学生端后端入口

开发模式下直接启动：
    python -m app.main

服务模式下由 app.windows.service 调用 run_agent()。

命令行：
    python -m app.main --lock <hash>   # 启动锁屏窗口
"""

import asyncio
import hashlib
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from shared.protocol import FilterMode

from app.core.config import CONFIG, save_config
from app.core.state import state
from app.api import api_router
from app.services.ws_client import StudentWebSocketClient, parse_controller_ip
from app.services.network_filter import (
    apply_filter_mode, has_internet_route, add_host_routes_dynamic,
)
from app.services.dns_server import DnsFilterServer
from app.services.tray_icon import AgentTray
from app.services.network_monitor import NetworkMonitor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            Path(__file__).resolve().parent.parent / "student-backend.log",
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger("student-backend")

ws_client = StudentWebSocketClient()
dns_server = DnsFilterServer(
    upstream_dns=CONFIG.get("upstream_dns", "114.114.114.114"),
    mode=FilterMode.WHITELIST,
    on_query=state.on_query_domain,
    on_resolved_ips=add_host_routes_dynamic,
)
ws_client.set_dns_server(dns_server)


def create_app() -> FastAPI:
    app = FastAPI(title="Network Control Student Backend")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    return app


app = create_app()


def _boot_lockdown():
    """开机默认断网（fail-closed），但保留到教师端的路由。"""
    controller_ip = parse_controller_ip(CONFIG.get("controller_url", ""))
    if not controller_ip:
        logger.warning("controller_url 不是 IP，无法保留教师端路由，断网可能连不回教师端")

    if not has_internet_route():
        logger.warning("未检测到默认路由，跳过开机断网设置")
        state.set_mode(FilterMode.DISCONNECT)
        return

    logger.info("开机默认断网（fail-closed），等待教师端下发上次状态")
    state.set_mode(FilterMode.DISCONNECT)
    try:
        apply_filter_mode(FilterMode.DISCONNECT, controller_ip=controller_ip)
    except Exception as e:
        logger.warning(f"开机断网执行失败（可能需要管理员权限）: {e}")


def _on_exit_confirmed():
    logger.info("用户通过托盘密码验证，退出程序")
    apply_filter_mode(FilterMode.NORMAL)
    os._exit(0)


async def run_agent():
    """启动 WebSocket 客户端、本地 API、DNS 服务、托盘、网络监控等核心逻辑"""
    tray = AgentTray(
        password_hash=CONFIG.get("tray_password_hash",
                                 hashlib.sha256(b"admin123").hexdigest()),
        visible=CONFIG.get("tray_visible", True),
        on_exit_confirmed=_on_exit_confirmed,
    )
    tray.start()

    monitor = NetworkMonitor(
        unlock_password_hash=CONFIG.get("unlock_password_hash",
                                        hashlib.sha256(b"admin123").hexdigest())
    )

    # 开机即锁网
    _boot_lockdown()

    try:
        dns_server.start()
    except Exception as e:
        logger.warning(f"DNS 服务器启动失败（可能需要管理员权限）: {e}")

    host = CONFIG.get("local_api_host", "127.0.0.1")
    port = CONFIG.get("local_api_port", 8772)

    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)

    try:
        await asyncio.gather(
            ws_client.run(),
            server.serve(),
            monitor.run(),
        )
    finally:
        apply_filter_mode(FilterMode.NORMAL)
        dns_server.stop()
        tray.stop()
        monitor.stop()


def main():
    # 锁屏模式
    if len(sys.argv) >= 2 and sys.argv[1] == "--lock":
        hash_val = sys.argv[2] if len(sys.argv) > 2 else hashlib.sha256(b"admin123").hexdigest()
        from app.services.lock_screen import run_lock_screen
        run_lock_screen(hash_val)
        return

    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        print("[Student Backend] 用户中断")
    finally:
        apply_filter_mode(FilterMode.NORMAL)
        dns_server.stop()
        ws_client.stop()


if __name__ == "__main__":
    main()
