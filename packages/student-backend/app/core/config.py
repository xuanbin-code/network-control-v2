"""学生端后端配置

配置优先级（从高到低）：
1. 已存在的 config.json
2. 环境变量（推荐开发环境使用 .env.development）
3. DEFAULT_CONFIG 默认值
"""

import hashlib
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 开发环境下从项目根目录加载 .env / .env.development
_ENV_PATH = BASE_DIR / ".env"
_ENV_DEV_PATH = BASE_DIR / ".env.development"
if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH, override=True)
elif _ENV_DEV_PATH.exists():
    load_dotenv(_ENV_DEV_PATH, override=True)

CONFIG_PATH = BASE_DIR / "config.json"

DEFAULT_CONFIG = {
    "controller_url": "ws://192.168.1.100:8765/ws",
    "controller_api_url": "http://192.168.1.100:8770",
    "local_api_host": "127.0.0.1",
    "local_api_port": 8772,
    "upstream_dns": "114.114.114.114",
    "lan_subnets": ["192.168.1.0/24"],
    "tray_visible": True,
    # 默认密码: admin123
    "tray_password_hash": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",
    "unlock_password_hash": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",
}


def _apply_env_overrides(cfg: dict) -> dict:
    """用环境变量覆盖配置，支持 JSON 列表/对象。"""
    env_map = {
        "NC_CONTROLLER_URL": "controller_url",
        "NC_CONTROLLER_API_URL": "controller_api_url",
        "NC_LOCAL_API_HOST": "local_api_host",
        "NC_LOCAL_API_PORT": "local_api_port",
        "NC_UPSTREAM_DNS": "upstream_dns",
        "NC_LAN_SUBNETS": "lan_subnets",
        "NC_TRAY_VISIBLE": "tray_visible",
        "NC_TRAY_PASSWORD_HASH": "tray_password_hash",
        "NC_UNLOCK_PASSWORD_HASH": "unlock_password_hash",
    }
    for env_key, cfg_key in env_map.items():
        value = os.environ.get(env_key)
        if value is None:
            continue
        if cfg_key == "local_api_port":
            try:
                value = int(value)
            except ValueError:
                continue
        elif cfg_key == "tray_visible":
            value = value.lower() in ("1", "true", "yes", "on")
        elif cfg_key == "lan_subnets":
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                continue
        cfg[cfg_key] = value
    return cfg


def load_config() -> dict:
    merged = DEFAULT_CONFIG.copy()
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            merged.update(cfg)
        except Exception as e:
            print(f"[Config] 读取配置失败: {e}, 使用默认配置")
    # 环境变量优先级高于 config.json，便于开发环境配置
    _apply_env_overrides(merged)
    return merged


def save_config(cfg: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def reload_config() -> dict:
    """重新从 config.json 加载配置，供调试使用。"""
    global CONFIG
    CONFIG = load_config()
    return CONFIG


CONFIG = load_config()
