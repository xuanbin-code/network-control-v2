"""filter 兼容层

原 network_filter.py / dns_server.py 已迁移到 app/services/。
此处重新导出公共 API，避免外部脚本（如 test_disconnect.py）导入失败。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.services.network_filter import (
    apply_filter_mode,
    has_internet_route,
    reconnect_internet,
    add_host_routes_dynamic,
    disconnect_internet,
    restore_adapter_dns,
    set_adapter_dns,
)
from app.services.dns_server import DnsFilterServer

__all__ = [
    "apply_filter_mode",
    "has_internet_route",
    "reconnect_internet",
    "add_host_routes_dynamic",
    "disconnect_internet",
    "restore_adapter_dns",
    "set_adapter_dns",
    "DnsFilterServer",
]
