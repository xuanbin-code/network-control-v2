"""测试功能接口

供前端测试组调用，用于在本地触发各类功能演示/测试。
"""

from fastapi import APIRouter

from app.services.black_screen import start_black_screen, stop_black_screen

router = APIRouter()


@router.post("/test/black_screen")
async def test_black_screen(data: dict):
    """启动黑屏安静测试窗口。

    参数:
        countdown_seconds: 倒计时秒数，默认 30 秒；
                          传入 0 或 None 表示持续黑屏，需手动/IPC 解除。
    """
    countdown = data.get("countdown_seconds", 30)
    return start_black_screen(countdown)


@router.post("/test/black_screen_unlock")
async def test_black_screen_unlock():
    """向本地黑屏安静 IPC 服务器发送解除命令。"""
    ok = stop_black_screen()
    return {"ok": ok}
