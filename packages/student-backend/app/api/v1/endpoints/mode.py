"""模式切换（供前端测试）"""

from fastapi import APIRouter

from shared.protocol import FilterMode

from app.core.state import state
from app.services.network_filter import apply_filter_mode

router = APIRouter()


@router.post("/apply_mode")
async def apply_mode(data: dict):
    """供前端测试：直接切换到指定模式"""
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
