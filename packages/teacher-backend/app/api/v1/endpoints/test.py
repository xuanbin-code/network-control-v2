"""测试消息与远程功能测试"""

from fastapi import APIRouter

from app.schemas import (
    TestMessageRequest,
    BlackScreenRequest,
    BlackScreenUnlockRequest,
)
from app.services.ws_manager import ws_manager

router = APIRouter()


@router.post("/test/send")
async def send_test_message(req: TestMessageRequest):
    """向学生端发送测试消息"""
    result = await ws_manager.send_test_message(req.message, targets=req.targets or None)
    return {
        "ok": True,
        "message": req.message,
        "targets": req.targets or "all",
        "delivery": result,
    }


@router.post("/test/black_screen")
async def send_black_screen(req: BlackScreenRequest):
    """向学生端发送黑屏安静测试指令"""
    result = await ws_manager.send_black_screen(
        countdown_seconds=req.countdown_seconds,
        targets=req.targets or None,
    )
    return {
        "ok": True,
        "action": "black_screen",
        "countdown_seconds": req.countdown_seconds,
        "targets": req.targets or "all",
        "delivery": result,
    }


@router.post("/test/black_screen_unlock")
async def send_black_screen_unlock(req: BlackScreenUnlockRequest):
    """向学生端发送解除黑屏指令"""
    result = await ws_manager.send_black_screen_unlock(targets=req.targets or None)
    return {
        "ok": True,
        "action": "black_screen_unlock",
        "targets": req.targets or "all",
        "delivery": result,
    }
