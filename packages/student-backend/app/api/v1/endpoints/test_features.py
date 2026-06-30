"""测试功能接口

供前端测试组调用，用于在本地触发各类功能演示/测试。
"""

import os
import subprocess
import sys

from fastapi import APIRouter

import app.services.lock_screen as lock_screen_module

router = APIRouter()


def _get_backend_dir() -> str:
    """根据 lock_screen 模块位置推导 student-backend 根目录。"""
    lock_screen_file = getattr(lock_screen_module, "__file__", "")
    # app/services/lock_screen.py -> student-backend
    return os.path.dirname(os.path.dirname(os.path.dirname(lock_screen_file)))


@router.post("/test/black_screen")
async def test_black_screen(data: dict):
    """启动黑屏安静测试窗口。

    参数:
        countdown_seconds: 倒计时秒数，默认 30 秒；
                          传入 0 或 None 表示持续黑屏，需手动/IPC 解除。
    """
    countdown = data.get("countdown_seconds", 30)
    if countdown is None:
        countdown = 0
    try:
        countdown = int(countdown)
    except (TypeError, ValueError):
        countdown = 30

    backend_dir = _get_backend_dir()
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NO_WINDOW

    proc = subprocess.Popen(
        [sys.executable, "-m", "app.services.lock_screen", str(countdown)],
        cwd=backend_dir,
        creationflags=creationflags,
    )

    return {
        "ok": True,
        "pid": proc.pid,
        "countdown_seconds": countdown,
        "infinite": countdown <= 0,
    }


@router.post("/test/black_screen_unlock")
async def test_black_screen_unlock():
    """向本地黑屏安静 IPC 服务器发送解除命令。"""
    from app.services.lock_screen import (
        DEFAULT_BLACK_SCREEN_IPC_HOST,
        DEFAULT_BLACK_SCREEN_IPC_PORT,
        send_unlock_command,
    )

    ok = send_unlock_command(
        host=DEFAULT_BLACK_SCREEN_IPC_HOST,
        port=DEFAULT_BLACK_SCREEN_IPC_PORT,
        timeout=2.0,
    )
    return {"ok": ok}
