"""黑屏安静窗口控制

供本地测试接口和教师端远程指令复用。
"""

import os
import subprocess
import sys
from pathlib import Path

import app.services.lock_screen as lock_screen_module
from app.services.lock_screen import (
    DEFAULT_BLACK_SCREEN_IPC_HOST,
    DEFAULT_BLACK_SCREEN_IPC_PORT,
    send_unlock_command,
)


def _get_backend_dir() -> str:
    """根据 lock_screen 模块位置推导 student-backend 根目录。"""
    lock_screen_file = getattr(lock_screen_module, "__file__", "")
    # app/services/lock_screen.py -> student-backend
    return os.path.dirname(os.path.dirname(os.path.dirname(lock_screen_file)))


def start_black_screen(countdown_seconds: int = 30) -> dict:
    """启动黑屏安静窗口。

    Args:
        countdown_seconds: 倒计时秒数；0 表示持续黑屏，需手动/IPC 解除。

    Returns:
        包含 pid、countdown_seconds、infinite 的字典。
    """
    countdown = countdown_seconds
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


def stop_black_screen() -> bool:
    """解除当前黑屏安静窗口。"""
    return send_unlock_command(
        host=DEFAULT_BLACK_SCREEN_IPC_HOST,
        port=DEFAULT_BLACK_SCREEN_IPC_PORT,
        timeout=2.0,
    )
