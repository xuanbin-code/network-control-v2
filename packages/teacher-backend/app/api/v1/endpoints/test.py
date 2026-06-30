"""测试消息"""

from fastapi import APIRouter

from app.schemas import TestMessageRequest
from app.services.ws_manager import ws_manager

router = APIRouter()


@router.post("/test/send")
async def send_test_message(req: TestMessageRequest):
    """向学生端发送测试消息"""
    await ws_manager.send_test_message(req.message, targets=req.targets or None)
    return {
        "ok": True,
        "message": req.message,
        "targets": req.targets or "all",
    }
