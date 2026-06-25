"""WebSocket 服务端：管理学生端连接"""

import asyncio
import time
from typing import Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from shared.protocol import MsgType, FilterMode

from .db import get_db
from .config import HEARTBEAT_TIMEOUT


class StudentConnection:
    def __init__(self, ws: WebSocket, ip: str):
        self.ws = ws
        self.ip = ip
        self.hostname = ""
        self.mac = ""
        self.mode = FilterMode.DISCONNECT
        self.last_heartbeat = time.time()


class WsManager:
    def __init__(self):
        self.students: Dict[str, StudentConnection] = {}

    async def connect(self, ws: WebSocket):
        await ws.accept()
        ip = ws.client.host if ws.client else "unknown"
        conn = StudentConnection(ws, ip)
        self.students[ip] = conn
        print(f"[WS] 学生端连接: {ip}")
        return conn

    def disconnect(self, conn: StudentConnection):
        if conn.ip in self.students:
            del self.students[conn.ip]
        print(f"[WS] 学生端断开: {conn.ip}")

    async def broadcast(self, message: dict, targets: Optional[list] = None):
        recipients = [self.students[ip] for ip in (targets or self.students.keys())]
        dead = []
        for conn in recipients:
            try:
                await conn.ws.send_json(message)
            except Exception:
                dead.append(conn)
        for conn in dead:
            self.disconnect(conn)

    async def handle_message(self, conn: StudentConnection, data: dict):
        msg_type = data.get("type")
        payload = data.get("payload", {})
        db = get_db()

        if msg_type == MsgType.REGISTER:
            conn.hostname = payload.get("hostname", "")
            conn.mac = payload.get("mac", "")
            conn.mode = payload.get("mode", FilterMode.DISCONNECT)
            await db.execute(
                """INSERT OR REPLACE INTO machines
                   (ip, hostname, mac, mode, online, last_heartbeat)
                   VALUES (?, ?, ?, ?, 1, ?)""",
                (conn.ip, conn.hostname, conn.mac, conn.mode, time.time()),
            )
            # 下发当前规则与权威状态
            await conn.ws.send_json({
                "type": MsgType.UPDATE_RULES,
                "payload": await self._build_rules_payload(),
            })
            # 下发 set_filter 恢复权威状态
            row = await db.fetchone(
                "SELECT mode FROM machines WHERE ip = ?", (conn.ip,)
            )
            target_mode = row["mode"] if row else FilterMode.NORMAL
            await conn.ws.send_json({
                "type": MsgType.SET_FILTER,
                "payload": {"mode": target_mode},
            })

        elif msg_type == MsgType.HEARTBEAT:
            conn.last_heartbeat = time.time()
            await db.execute(
                "UPDATE machines SET online = 1, last_heartbeat = ? WHERE ip = ?",
                (conn.last_heartbeat, conn.ip),
            )

        elif msg_type == MsgType.STATUS:
            conn.mode = payload.get("mode", conn.mode)
            await db.execute(
                "UPDATE machines SET mode = ? WHERE ip = ?",
                (conn.mode, conn.ip),
            )

        elif msg_type == MsgType.BROWSING_UPDATE:
            domains = payload.get("domains", [])
            ts = time.time()
            for domain in domains[-50:]:
                await db.execute(
                    "INSERT INTO browsing_logs (ip, domain, ts) VALUES (?, ?, ?)",
                    (conn.ip, domain, ts),
                )

    async def _build_rules_payload(self) -> dict:
        db = get_db()
        whitelist = await db.fetchall(
            "SELECT domain, enabled FROM whitelist_rules WHERE enabled = 1"
        )
        blacklist = await db.fetchall(
            "SELECT domain, enabled FROM blacklist_rules WHERE enabled = 1"
        )
        return {
            "whitelist": [r["domain"] for r in whitelist],
            "blacklist": [r["domain"] for r in blacklist],
        }

    async def cleanup_offline(self):
        while True:
            await asyncio.sleep(10)
            now = time.time()
            offline_ips = [
                ip for ip, conn in self.students.items()
                if now - conn.last_heartbeat > HEARTBEAT_TIMEOUT
            ]
            for ip in offline_ips:
                conn = self.students.pop(ip, None)
                if conn:
                    try:
                        await conn.ws.close()
                    except Exception:
                        pass
                db = get_db()
                await db.execute(
                    "UPDATE machines SET online = 0 WHERE ip = ?", (ip,)
                )
                print(f"[WS] 标记离线: {ip}")


ws_manager = WsManager()


def register_ws_routes(app: FastAPI):
    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket):
        conn = await ws_manager.connect(ws)
        try:
            while True:
                data = await ws.receive_json()
                await ws_manager.handle_message(conn, data)
        except WebSocketDisconnect:
            ws_manager.disconnect(conn)
        except Exception as e:
            print(f"[WS] 异常: {e}")
            ws_manager.disconnect(conn)
