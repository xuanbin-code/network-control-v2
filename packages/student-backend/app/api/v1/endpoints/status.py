"""运行状态"""

from fastapi import APIRouter

from app.core.config import CONFIG
from app.core.state import state

router = APIRouter()


@router.get("/status")
async def get_status():
    return {
        "mode": state.mode,
        "connected": state.connected,
        "controller_url": CONFIG.get("controller_url"),
        "controller_ip": state.controller_ip,
        "hostname": state.hostname,
        "mac": state.mac,
        "filter_active": state.filter_active,
        "dns_running": state.dns_running,
        "rule_count": state.rule_count,
        "last_test_message": state.last_test_message,
        "last_test_message_ts": state.last_test_message_ts,
    }
