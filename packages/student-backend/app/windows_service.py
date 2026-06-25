"""Windows 服务入口

使用 pywin32 注册为系统服务：NetControlAgent
"""

import os
import sys
import time
import threading

import win32serviceutil
import win32service
import win32event
import servicemanager

# 兼容 PyInstaller 路径
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.main import run_agent
import asyncio


class NetworkControlAgent(win32serviceutil.ServiceFramework):
    _svc_name_ = "NetControlAgent"
    _svc_display_name_ = "Network Control Student Agent"
    _svc_description_ = "Network Control 学生端网络访问控制代理服务"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.loop = None
        self.thread = None
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
            self.loop.close()
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, ""),
            )


def install_service():
    win32serviceutil.HandleCommandLine(NetworkControlAgent, argv=[sys.argv[0], "--startup=auto", "install"])


def uninstall_service():
    win32serviceutil.HandleCommandLine(NetworkControlAgent, argv=[sys.argv[0], "remove"])


def run_service():
    win32serviceutil.HandleCommandLine(NetworkControlAgent)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(NetworkControlAgent)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(NetworkControlAgent)
