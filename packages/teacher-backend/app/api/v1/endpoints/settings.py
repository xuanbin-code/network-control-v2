"""系统设置"""

from fastapi import APIRouter

from app.db import get_db
from app.schemas import SettingUpdateRequest
from app.services.ws_manager import ws_manager

router = APIRouter()


@router.get("/settings")
async def get_settings():
    db = get_db()
    return await db.get_settings()


@router.post("/settings")
async def update_setting(req: SettingUpdateRequest):
    db = get_db()
    await db.set_setting(req.key, req.value)
    # 设置变更后重新下发规则
    if req.key in ("filter_mode", "lan_subnets", "upstream_dns"):
        await ws_manager.push_rules()
    return {"ok": True}
