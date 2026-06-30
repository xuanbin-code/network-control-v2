"""健康检查"""

from fastapi import APIRouter

from app.core.state import state

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "connected": state.connected, "mode": state.mode}
