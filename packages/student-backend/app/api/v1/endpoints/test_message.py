"""测试消息"""

import time

from fastapi import APIRouter

from app.core.state import state

router = APIRouter()


@router.get("/test_message")
async def get_test_message():
    """获取最近一条教师端发来的测试消息"""
    return {
        "message": state.last_test_message,
        "ts": state.last_test_message_ts,
        "time_str": time.strftime("%Y-%m-%d %H:%M:%S",
                                   time.localtime(state.last_test_message_ts))
        if state.last_test_message_ts else "",
    }
