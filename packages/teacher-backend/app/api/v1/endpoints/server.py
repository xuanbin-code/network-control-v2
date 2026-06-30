"""服务端信息"""

from fastapi import APIRouter

from app.core.config import WS_PORT
from app.services.ws_manager import ws_manager

router = APIRouter()


@router.get("/server_info")
async def server_info():
    """返回教师端 IP 和 WebSocket 地址"""
    local_ip = ws_manager._get_local_ip()
    return {
        "ip": local_ip,
        "ws_url": f"ws://{local_ip}:{WS_PORT}/ws",
        "ws_port": WS_PORT,
    }
