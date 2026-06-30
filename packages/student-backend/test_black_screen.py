#!/usr/bin/env python3
"""黑屏安静测试程序

用于测试教师端对学生的控制是否生效：
- 启动后全屏黑屏，保持静默
- 显示小猫提醒图和 "请保持安静" 文字
- 倒计时结束后会自动解除黑屏
- 可独立运行：python test_black_screen.py [倒计时秒数]

实际窗口逻辑已封装到 app.services.lock_screen，本文件仅作为独立测试入口。
"""

import os
import sys
import traceback

# 设置 stdout 编码为 utf-8，避免中文乱码
# type: ignore 用于消除部分 IDE 对 sys.stdout.reconfigure 的类型误报
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
except Exception:
    pass

# 确保能导入 app 包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.lock_screen import run_black_screen_quiet, DEFAULT_BLACK_SCREEN_SECONDS


def _parse_countdown(args: list[str]) -> int | None:
    """解析倒计时参数。0 或负数表示持续黑屏，无自动倒计时。"""
    if not args:
        return DEFAULT_BLACK_SCREEN_SECONDS
    try:
        value = int(args[0])
        if value == 0:
            print("[test_black_screen] 使用持续黑屏模式，需手动点击按钮或按 ESC 解除。")
            return 0
        return value
    except ValueError:
        print(f"[test_black_screen] 警告：无法解析倒计时参数 '{args[0]}'，已使用默认值 {DEFAULT_BLACK_SCREEN_SECONDS}。")
        return DEFAULT_BLACK_SCREEN_SECONDS


def main():
    try:
        countdown = _parse_countdown(sys.argv[1:])
        if countdown and countdown > 0:
            print(f"[test_black_screen] 倒计时 {countdown} 秒，时间到后自动解除；也可点击按钮或按 ESC 提前退出。")
        else:
            print("[test_black_screen] 持续黑屏模式，需手动点击按钮或按 ESC 解除。")
        run_black_screen_quiet(countdown)
    except SystemExit:
        raise
    except Exception as e:
        print(f"[test_black_screen] 运行异常: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
