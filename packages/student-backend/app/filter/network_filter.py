"""网络过滤控制（骨架实现）

后续可逐步迁移原项目 PowerShell + 路由表 + DNS 过滤逻辑。
当前阶段仅打印模式变更，便于前端/后端联调。
"""

import subprocess
import sys

from shared.protocol import FilterMode


def apply_filter_mode(mode: str):
    """应用网络过滤模式"""
    print(f"[Filter] 切换到模式: {mode}")
    if mode == FilterMode.NORMAL:
        _enable_network()
    elif mode == FilterMode.WHITELIST:
        _enable_whitelist()
    elif mode == FilterMode.BLACKLIST:
        _enable_blacklist()
    elif mode == FilterMode.DISCONNECT:
        _disable_network()


def _enable_network():
    """恢复正常上网"""
    print("[Filter] 恢复正常路由/DNS")


def _enable_whitelist():
    """白名单模式：DNS 过滤 + 路由表动态放行"""
    print("[Filter] 启用白名单过滤")


def _enable_blacklist():
    """黑名单模式：仅 DNS 拦截黑名单"""
    print("[Filter] 启用黑名单过滤")


def _disable_network():
    """断网：删除默认路由，保留到教师端路由"""
    print("[Filter] 断开默认网络，保留到教师端路由")


def run_powershell(cmd: str) -> tuple:
    """运行 PowerShell 命令"""
    p = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", cmd],
        capture_output=True,
        text=True,
        encoding="gbk" if sys.platform == "win32" else "utf-8",
    )
    return p.returncode, p.stdout, p.stderr
