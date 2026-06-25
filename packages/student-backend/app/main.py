"""学生端后端入口

开发模式下直接启动：
    python -m app.main

服务模式下由 windows_service.py 调用 run_agent()。
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config import CONFIG
from .ws_client import StudentWebSocketClient
from .api_server import router as api_router
from .filter.network_filter import apply_filter_mode
from .filter.dns_server import DnsFilterServer
from .state import state
from shared.protocol import FilterMode


ws_client = StudentWebSocketClient()
dns_server = DnsFilterServer(CONFIG.get("upstream_dns", "114.114.114.114"))


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


async def run_agent():
    """启动 WebSocket 客户端、本地 API、DNS 服务等核心逻辑"""
    # 开机默认断网
    state.set_mode(FilterMode.DISCONNECT)
    apply_filter_mode(FilterMode.DISCONNECT)

    dns_server.start()

    host = CONFIG.get("local_api_host", "127.0.0.1")
    port = CONFIG.get("local_api_port", 8772)

    # 启动本地 API（使用 uvicorn 的 Config + Server 便于与 asyncio 协同）
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)

    await asyncio.gather(
        ws_client.run(),
        server.serve(),
    )


def main():
    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        print("[Student Backend] 用户中断")
    finally:
        dns_server.stop()
        ws_client.stop()


if __name__ == "__main__":
    main()
