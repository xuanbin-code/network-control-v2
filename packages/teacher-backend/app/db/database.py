"""SQLite 数据访问层"""

import asyncio
import json
from pathlib import Path
from typing import List, Optional

import aiosqlite

from app.core.config import DB_PATH


class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._lock = asyncio.Lock()

    async def init(self):
        from app.db.init import INIT_SQL

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
