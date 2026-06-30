"""教师端后端入口

启动三个服务：
- FastAPI HTTP + WebSocket（Electron / 学生端备选）: 127.0.0.1:8771
- FastAPI HTTP（外部教学软件调用）: 127.0.0.1:8770
- FastAPI WebSocket（学生端主连接）: 0.0.0.0:8765
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.db import get_db
from app.websocket import register_ws_routes
from app.api import api_router
from app.services.ws_manager import ws_manager
from app.core import config


async def lifespan(app: FastAPI):
    db = get_db()
    await db.init()
    asyncio.create_task(ws_manager.cleanup_offline())
    print(f"[Teacher Backend] 本地 API + WS: http://{config.LOCAL_API_HOST}:{config.LOCAL_API_PORT}")
    print(f"[Teacher Backend] 外部 API: http://{config.API_HOST}:{config.API_PORT}")
    print(f"[Teacher Backend] WebSocket: ws://{config.WS_HOST}:{config.WS_PORT}/ws")
    yield
    print("[Teacher Backend] 关闭")


def create_local_app() -> FastAPI:
    app = FastAPI(title="Network Control Teacher Backend (Local)", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    register_ws_routes(app)
    return app


def create_external_app() -> FastAPI:
    app = FastAPI(title="Network Control Teacher Backend (External)")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    return app


def create_ws_app() -> FastAPI:
    app = FastAPI(title="Network Control Teacher Backend (WebSocket)")
    register_ws_routes(app)
    return app


local_app = create_local_app()
external_app = create_external_app()
ws_app = create_ws_app()


async def run_servers():
    cfg_local = uvicorn.Config(
        local_app,
        host=config.LOCAL_API_HOST,
        port=config.LOCAL_API_PORT,
        log_level="info",
    )
    cfg_external = uvicorn.Config(
        external_app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level="info",
    )
    cfg_ws = uvicorn.Config(
        ws_app,
        host=config.WS_HOST,
        port=config.WS_PORT,
        log_level="info",
    )
    server_local = uvicorn.Server(cfg_local)
    server_external = uvicorn.Server(cfg_external)
    server_ws = uvicorn.Server(cfg_ws)
    await asyncio.gather(
        server_local.serve(),
        server_external.serve(),
        server_ws.serve(),
    )


def main():
    asyncio.run(run_servers())


if __name__ == "__main__":
    main()
