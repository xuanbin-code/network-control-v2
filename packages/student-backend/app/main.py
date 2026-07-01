"""Student backend entry point.

Run in dev mode:
    python -m app.main

服务模式下由 app.windows.service 调用 run_agent()。

Command line:
    python -m app.main --lock <hash>   # Launch lock screen window
"""

import asyncio
import hashlib
import logging
import os
import sys
import time
from pathlib import Path

# Force UTF-8 for stdout/stderr to avoid garbled output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

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
from app.services.block_page import BlockPageServer
from app.services.tray_icon import AgentTray
from app.services import tray_icon
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
block_page_server = BlockPageServer()

BLOCK_PAGE_IP = "127.0.0.1"
dns_server = DnsFilterServer(
    upstream_dns=CONFIG.get("upstream_dns", "114.114.114.114"),
    mode=FilterMode.NORMAL,
    on_query=state.on_query_domain,
    on_resolved_ips=add_host_routes_dynamic,
    block_page_ip=BLOCK_PAGE_IP,
)
state.dns_server = dns_server
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


async def _boot_open():
    """默认完全开放，等待测试页面或教师端下发规则。

    所有涉及系统命令的调用都提交到线程池，避免阻塞 asyncio 事件循环。
    """
    loop = asyncio.get_running_loop()
    logger.info("Boot open: network remains normal until rules are received")
    state.set_mode(FilterMode.NORMAL)
    try:
        await loop.run_in_executor(None, apply_filter_mode, FilterMode.NORMAL)
    except Exception as e:
        logger.warning(f"Boot open failed (administrator rights may be required): {e}")


async def _restore_network_async():
    """异步恢复网络，用于托盘退出等需要进线程池的场景。"""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, apply_filter_mode, FilterMode.NORMAL)


def _make_on_exit_confirmed(loop: asyncio.AbstractEventLoop):
    def _on_exit_confirmed():
        logger.info("User confirmed exit via tray password")
        try:
            asyncio.run_coroutine_threadsafe(_restore_network_async(), loop)
        except Exception as e:
            logger.warning(f"Failed to schedule network restore: {e}")
            apply_filter_mode(FilterMode.NORMAL)
        os._exit(0)
    return _on_exit_confirmed


async def run_agent():
    """Start WebSocket client, local API, DNS server, tray icon and network monitor."""
    loop = asyncio.get_running_loop()
    tray = AgentTray(
        password_hash=CONFIG.get("tray_password_hash",
                                 hashlib.sha256(b"admin123").hexdigest()),
        visible=CONFIG.get("tray_visible", True),
        on_exit_confirmed=_make_on_exit_confirmed(loop),
    )
    tray.start()
    tray_icon.current_tray = tray
    tray.set_net_state(FilterMode.NORMAL)

    monitor = NetworkMonitor(
        unlock_password_hash=CONFIG.get("unlock_password_hash",
                                        hashlib.sha256(b"admin123").hexdigest())
    )

    # 默认开放，便于测试页面切换模式
    await _boot_open()

    try:
        dns_server.start()
    except Exception as e:
        logger.warning(f"DNS server failed to start (administrator rights may be required): {e}")

    try:
        block_page_server.start()
    except Exception as e:
        logger.warning(f"Block page server failed to start: {e}")

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
        try:
            await asyncio.get_event_loop().run_in_executor(None, apply_filter_mode, FilterMode.NORMAL)
        except Exception:
            pass
        dns_server.stop()
        block_page_server.stop()
        tray.stop()
        monitor.stop()


def main():
    # Lock screen mode
    if len(sys.argv) >= 2 and sys.argv[1] == "--lock":
        hash_val = sys.argv[2] if len(sys.argv) > 2 else hashlib.sha256(b"admin123").hexdigest()
        from app.services.lock_screen import run_lock_screen
        run_lock_screen(hash_val)
        return

    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        print("[Student Backend] Interrupted by user")
    finally:
        apply_filter_mode(FilterMode.NORMAL)
        dns_server.stop()
        ws_client.stop()


if __name__ == "__main__":
    main()
