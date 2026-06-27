"""学生端后端配置"""

import hashlib
import json
import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

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


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(cfg)
            return merged
        except Exception as e:
            print(f"[Config] 读取配置失败: {e}, 使用默认配置")
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def reload_config() -> dict:
    """重新从 config.json 加载配置，供调试使用。"""
    global CONFIG
    CONFIG = load_config()
    return CONFIG


CONFIG = load_config()
