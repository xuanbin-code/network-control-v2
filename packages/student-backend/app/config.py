"""config 兼容层

原 config.py 已迁移到 app/core/config.py。
此处重新导出公共 API，避免外部脚本（如 test_disconnect.py）导入失败。
"""

from app.core.config import (
    CONFIG,
    DEFAULT_CONFIG,
    load_config,
    save_config,
    reload_config,
    CONFIG_PATH,
    BASE_DIR,
)

__all__ = [
    "CONFIG",
    "DEFAULT_CONFIG",
    "load_config",
    "save_config",
    "reload_config",
    "CONFIG_PATH",
    "BASE_DIR",
]
