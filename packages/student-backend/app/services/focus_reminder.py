"""专注提示触发器

当学生访问被拦截的网页时，通过 DNS 查询事件触发全屏提示窗，
提醒学生专心学习、不要访问无关网页。
"""

import logging
import os
import subprocess
import sys
import threading
import time

from shared.protocol import FilterMode

from app.core.state import state

logger = logging.getLogger("focus_reminder")

DEFAULT_COOLDOWN_SECONDS = 15
DEFAULT_DURATION_SECONDS = 8


class FocusReminder:
    """基于 DNS 查询的专注提示触发器。"""

    def __init__(self,
                 cooldown_seconds: int = DEFAULT_COOLDOWN_SECONDS,
                 duration_seconds: int = DEFAULT_DURATION_SECONDS):
        self.cooldown_seconds = cooldown_seconds
        self.duration_seconds = duration_seconds
        self._last_trigger = 0.0
        self._lock = threading.Lock()

    def _matches(self, domain: str, patterns: list[str]) -> bool:
        """通配符域名匹配，与 dns_server.FilterResolver._matches 逻辑一致。"""
        name = domain.lower().rstrip(".")
        for pattern in patterns:
            pattern = pattern.strip().lower().rstrip(".")
            if not pattern:
                continue
            if pattern.startswith("*."):
                base = pattern[2:]
                if name == base or name.endswith("." + base):
                    return True
            else:
                if name == pattern or name.endswith("." + pattern):
                    return True
        return False

    def is_blocked(self, domain: str) -> bool:
        """根据当前模式判断域名是否应被拦截。"""
        mode = state.mode
        if mode == FilterMode.NORMAL:
            return False
        if mode == FilterMode.DISCONNECT:
            return True
        if mode == FilterMode.WHITELIST:
            return not self._matches(domain, state.whitelist_domains)
        if mode == FilterMode.BLACKLIST:
            return self._matches(domain, state.blacklist_domains)
        return False

    def should_trigger(self) -> bool:
        """检查冷却时间，避免频繁弹窗。"""
        with self._lock:
            now = time.time()
            if now - self._last_trigger < self.cooldown_seconds:
                return False
            self._last_trigger = now
            return True

    def trigger(self, domain: str):
        """启动专注提示窗子进程。"""
        try:
            exe = sys.executable
            cmd = [
                exe, "-m", "app.services.lock_screen",
                "--focus-reminder", str(self.duration_seconds),
            ]
            # 子进程独立运行，不需要等待；继承当前工作目录
            subprocess.Popen(
                cmd,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                cwd=os.path.dirname(exe) or None,
            )
            logger.info(f"专注提示窗已触发（domain={domain}）")
        except Exception as e:
            logger.warning(f"启动专注提示窗失败: {e}")

    def on_dns_query(self, domain: str):
        """DNS 查询回调入口，由 dns_server 在每次查询时调用。"""
        if not self.is_blocked(domain):
            return
        if not self.should_trigger():
            logger.debug(f"专注提示冷却中，跳过: {domain}")
            return
        self.trigger(domain)


# 全局单例
focus_reminder = FocusReminder()


def on_dns_query(domain: str):
    """供 dns_server 调用的便捷入口。"""
    focus_reminder.on_dns_query(domain)
