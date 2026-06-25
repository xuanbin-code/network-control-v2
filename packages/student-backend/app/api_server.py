"""学生端本地 HTTP API：供 Electron 前端调用"""

from fastapi import APIRouter

from .state import state
from .config import CONFIG

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
    }


@router.get("/config")
async def get_config():
    return CONFIG


@router.post("/config")
async def update_config(data: dict):
    CONFIG.update(data)
    from .config import save_config
    save_config(CONFIG)
    return {"ok": True}
