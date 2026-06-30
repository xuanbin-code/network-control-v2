"""Windows 服务入口

使用 pywin32 注册为系统服务：NetControlAgent
命令行：
    python -m app.windows.service install
    python -m app.windows.service start
    python -m app.windows.service remove
"""

import os
import subprocess
import sys
import time

import win32serviceutil
import win32service
import win32event
import servicemanager

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 兼容：service.py 当前位于 app/windows/，BASE_DIR 应指向 student-backend 根目录
if not getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(os.path.dirname(BASE_DIR))

from app.main import run_agent
import asyncio

SERVICE_NAME = "NetControlAgent"
SERVICE_DISPLAY = "网络控制-被控端"
SERVICE_DESC = "Network Control 学生端网络访问控制代理服务"


class NetworkControlAgent(win32serviceutil.ServiceFramework):
    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = SERVICE_DISPLAY
    _svc_description_ = SERVICE_DESC
    _svc_startType_ = win32service.SERVICE_AUTO_START
    _svc_deps_ = ["Tcpip", "Dnscache"]

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.loop = None
        self.running = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        self.running = True
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(run_agent())
        except Exception as e:
            servicemanager.LogErrorMsg(str(e))
        finally:
            if self.loop:
                self.loop.close()
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, ""),
            )


def _configure_failure_recovery():
    subprocess.run([
        "sc", "failure", SERVICE_NAME,
        "reset=", "86400",
        "actions=", "restart/30000/restart/30000/restart/30000"
    ], capture_output=True)
    subprocess.run([
        "sc", "config", SERVICE_NAME, "start=", "auto"
    ], capture_output=True)
    print("Configured failure recovery restart policy + auto start on boot")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(NetworkControlAgent)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(NetworkControlAgent)
        if sys.argv[1].lower() == "install":
            _configure_failure_recovery()
