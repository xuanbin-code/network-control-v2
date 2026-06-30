"""配置管理"""

from fastapi import APIRouter

from app.core.config import CONFIG, save_config, reload_config
from app.services.ws_client import get_current_client

router = APIRouter()


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
