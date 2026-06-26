"""拔网线检测 + 锁屏启动器"""

import asyncio
import logging
import os
import subprocess
import sys

logger = logging.getLogger("network_monitor")


def _is_network_up() -> bool:
    try:
        result = subprocess.run(
            ['powershell', '-Command',
             '(Get-NetAdapter | Where-Object {$_.Status -eq "Up" -and $_.Name -notmatch "Loopback"}).Count'],
            capture_output=True, text=True, timeout=5,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        s = result.stdout.strip()
        return int(s) > 0 if s.isdigit() else True
    except Exception:
        return True


def _close_lock_screen():
    ps = ("Get-CimInstance Win32_Process | Where-Object "
          "{ $_.CommandLine -like '*--lock*' -and $_.ProcessId -ne $PID } | "
          "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }")
    try:
        subprocess.run(['powershell', '-NonInteractive', '-Command', ps],
                       capture_output=True, timeout=15,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        logger.info("已关闭全部锁屏进程(--lock)")
    except Exception as e:
        logger.warning(f"关闭锁屏进程失败: {e}")


def _is_process_alive(pid: int) -> bool:
    try:
        import win32api
        import win32process
        import win32con
        handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
        code = win32process.GetExitCodeProcess(handle)
        win32api.CloseHandle(handle)
        return code == 259  # STILL_ACTIVE
    except Exception:
        return False


def _launch_lock_screen(unlock_hash: str) -> int | None:
    exe = sys.executable
    try:
        import win32ts
        import win32process
        import win32security
        import win32con
        import win32api
        import win32profile

        session_id = win32ts.WTSGetActiveConsoleSessionId()
        if session_id == 0xFFFFFFFF:
            raise RuntimeError("无活动用户会话")

        user_token = win32ts.WTSQueryUserToken(session_id)
        primary_token = win32security.DuplicateTokenEx(
            user_token,
            win32security.SecurityImpersonation,
            win32con.TOKEN_ALL_ACCESS,
            win32security.TokenPrimary,
        )
        si = win32process.STARTUPINFO()
        si.lpDesktop = "winsta0\\default"
        cmd = f'"{exe}" --lock "{unlock_hash}"'
        try:
            env = win32profile.CreateEnvironmentBlock(user_token, False)
        except Exception:
            env = None
        workdir = os.path.dirname(exe) or None
        CREATE_UNICODE_ENVIRONMENT = 0x00000400
        info = win32process.CreateProcessAsUser(
            primary_token, None, cmd, None, None, False,
            win32con.NORMAL_PRIORITY_CLASS | CREATE_UNICODE_ENVIRONMENT,
            env, workdir, si
        )
        pid = info[2]
        win32api.CloseHandle(info[0])
        win32api.CloseHandle(info[1])
        logger.info(f"锁屏进程已启动 PID={pid}")
        return pid
    except Exception as e:
        logger.warning(f"WTS 方式启动锁屏失败({e})，降级为当前会话直接启动")

    try:
        proc = subprocess.Popen(
            [exe, "--lock", unlock_hash],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        logger.info(f"锁屏进程已启动(降级模式) PID={proc.pid}")
        return proc.pid
    except Exception as e2:
        logger.error(f"启动锁屏失败: {e2}")
        return None


class NetworkMonitor:
    def __init__(self, unlock_password_hash: str):
        self.unlock_password_hash = unlock_password_hash
        self._network_was_up = True
        self._lock_screen_pid: int | None = None
        self._stop = False

    async def run(self):
        await asyncio.sleep(5)
        while not self._stop:
            await asyncio.sleep(3)
            try:
                up = await asyncio.get_event_loop().run_in_executor(None, _is_network_up)
                if not up and self._network_was_up:
                    self._network_was_up = False
                    logger.warning("检测到网线断开，启动锁屏")
                    self._lock_screen_pid = await asyncio.get_event_loop().run_in_executor(
                        None, _launch_lock_screen, self.unlock_password_hash
                    )
                elif up and not self._network_was_up:
                    self._network_was_up = True
                    logger.info("网络已恢复，关闭锁屏")
                    await asyncio.get_event_loop().run_in_executor(None, _close_lock_screen)
                    self._lock_screen_pid = None

                if not self._network_was_up and self._lock_screen_pid:
                    if not _is_process_alive(self._lock_screen_pid):
                        logger.info("锁屏进程退出，重新启动")
                        self._lock_screen_pid = await asyncio.get_event_loop().run_in_executor(
                            None, _launch_lock_screen, self.unlock_password_hash
                        )
            except Exception as e:
                logger.debug(f"网络监控异常: {e}")

    def stop(self):
        self._stop = True
