"""Windows 服务入口兼容层

原 windows_service.py 已迁移到 app/windows/service.py。
此处保留旧命令行入口：`python -m app.windows_service install/start/remove`
"""

from app.windows.service import (
    NetworkControlAgent,
    SERVICE_NAME,
    SERVICE_DISPLAY,
    SERVICE_DESC,
    _configure_failure_recovery,
)
import win32serviceutil
import servicemanager
import sys


if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(NetworkControlAgent)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(NetworkControlAgent)
        if sys.argv[1].lower() == "install":
            _configure_failure_recovery()
