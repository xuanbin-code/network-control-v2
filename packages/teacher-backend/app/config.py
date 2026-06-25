"""教师端后端配置"""

import os
import sys
from pathlib import Path

# 兼容 PyInstaller 打包后的路径
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "teacher.db"

WS_HOST = os.environ.get("NC_WS_HOST", "0.0.0.0")
WS_PORT = int(os.environ.get("NC_WS_PORT", "8765"))
API_HOST = os.environ.get("NC_API_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("NC_API_PORT", "8770"))
LOCAL_API_HOST = os.environ.get("NC_LOCAL_API_HOST", "127.0.0.1")
LOCAL_API_PORT = int(os.environ.get("NC_LOCAL_API_PORT", "8771"))

HEARTBEAT_INTERVAL = int(os.environ.get("NC_HEARTBEAT_INTERVAL", "20"))
HEARTBEAT_TIMEOUT = int(os.environ.get("NC_HEARTBEAT_TIMEOUT", "60"))
