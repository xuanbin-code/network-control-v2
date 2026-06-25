"""教师端后端入口

启动两个服务：
- FastAPI HTTP 服务（供 Electron 和外部调用）
- WebSocket 服务（供学生端连接）

实际部署时 WebSocket 与 HTTP 共用 uvicorn，外部学生端连 ws://ip:8770/ws
"""

import asyncio
import sys
from pathlib import Path

# 把 shared 加入路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .db import get_db
from .ws_server import register_ws_routes, ws_manager
from .api_server import router as api_router
from . import config


async def lifespan(app: FastAPI):
    db = get_db()
    await db.init()
    # 启动离线清理任务
    asyncio.create_task(ws_manager.cleanup_offline())
    print(f"[Teacher Backend] 启动于 http://{config.LOCAL_API_HOST}:{config.LOCAL_API_PORT}")
    yield
    print("[Teacher Backend] 关闭")


def create_app() -> FastAPI:
    app = FastAPI(title="Network Control Teacher Backend", lifespan=lifespan)

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


app = create_app()


def main():
    uvicorn.run(
        "app.main:app",
        host=config.LOCAL_API_HOST,
        port=config.LOCAL_API_PORT,
        log_level="info",
    )


if __name__ == "__main__":
    main()
