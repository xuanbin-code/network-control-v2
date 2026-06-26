"""SQLite 数据层"""

import asyncio
import json
from pathlib import Path
from typing import List, Optional

import aiosqlite

from .config import DB_PATH


def _default_lan_subnets():
    return '["192.168.1.0/24"]'


INIT_SQL = f"""
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS machines (
    ip TEXT PRIMARY KEY,
    hostname TEXT DEFAULT '',
    mac TEXT,
    mode TEXT DEFAULT 'disconnect',
    online INTEGER DEFAULT 0,
    last_heartbeat REAL
);

CREATE TABLE IF NOT EXISTS whitelist_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL UNIQUE,
    enabled INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS blacklist_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL UNIQUE,
    enabled INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS browsing_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL,
    domain TEXT NOT NULL,
    ts REAL NOT NULL
);

INSERT OR IGNORE INTO settings (key, value) VALUES ('ws_port', '8765');
INSERT OR IGNORE INTO settings (key, value) VALUES ('api_port', '8770');
INSERT OR IGNORE INTO settings (key, value) VALUES ('heartbeat_interval', '20');
INSERT OR IGNORE INTO settings (key, value) VALUES ('heartbeat_timeout', '60');
INSERT OR IGNORE INTO settings (key, value) VALUES ('lan_subnets', '{_default_lan_subnets()}');
INSERT OR IGNORE INTO settings (key, value) VALUES ('upstream_dns', '114.114.114.114');
INSERT OR IGNORE INTO settings (key, value) VALUES ('filter_mode', 'whitelist');
INSERT OR IGNORE INTO settings (key, value) VALUES ('tray_password_hash', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9');
INSERT OR IGNORE INTO settings (key, value) VALUES ('unlock_password_hash', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9');
"""


class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._lock = asyncio.Lock()

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(INIT_SQL)
            await db.commit()

    async def execute(self, sql: str, params=()):
        async with self._lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(sql, params)
                await db.commit()

    async def fetchall(self, sql: str, params=()) -> List[dict]:
        async with self._lock:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(sql, params) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

    async def fetchone(self, sql: str, params=()) -> Optional[dict]:
        rows = await self.fetchall(sql, params)
        return rows[0] if rows else None

    async def get_settings(self) -> dict:
        rows = await self.fetchall("SELECT key, value FROM settings")
        result = {}
        for row in rows:
            value = row["value"]
            if row["key"] in ("lan_subnets",):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass
            result[row["key"]] = value
        return result

    async def set_setting(self, key: str, value):
        if isinstance(value, (list, dict)):
            value = json.dumps(value, ensure_ascii=False)
        else:
            value = str(value)
        await self.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )


_db: Optional[Database] = None


def get_db() -> Database:
    global _db
    if _db is None:
        _db = Database()
    return _db
