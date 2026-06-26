"""WebSocket 服务端：管理学生端连接"""

import asyncio
import socket
import time
from typing import Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from shared.protocol import (
    MsgType, FilterMode,
    msg_update_rules, msg_set_filter,
    parse_msg, extract_payload,
)

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

    async def broadcast(self, message: str, targets: Optional[list] = None):
        recipients = [self.students[ip] for ip in (targets or self.students.keys()) if ip in self.students]
        dead = []
        for conn in recipients:
            try:
                await conn.ws.send_text(message)
            except Exception:
                dead.append(conn)
        for conn in dead:
            self.disconnect(conn)

    async def handle_message(self, conn: StudentConnection, data: dict):
        msg_type = data.get("type")
        payload = extract_payload(data)
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
            # 下发当前规则
            rules_payload = await self._build_rules_payload()
            await conn.ws.send_text(msg_update_rules(
                domains=rules_payload["domains"],
                lan_subnets=rules_payload["lan_subnets"],
                controller_ip=self._get_local_ip(),
                upstream_dns=rules_payload["upstream_dns"],
                mode=rules_payload["mode"],
                tray_pwd_hash=rules_payload.get("tray_pwd_hash", ""),
                unlock_pwd_hash=rules_payload.get("unlock_pwd_hash", ""),
            ))
            # 下发权威状态
            row = await db.fetchone(
                "SELECT mode FROM machines WHERE ip = ?", (conn.ip,)
            )
            target_mode = row["mode"] if row else FilterMode.NORMAL
            await conn.ws.send_text(msg_set_filter(
                enabled=target_mode != FilterMode.NORMAL,
                mode=target_mode,
            ))
            print(f"[WS] 学生端注册: {conn.ip} ({conn.hostname}) -> {target_mode}")

        elif msg_type == MsgType.HEARTBEAT:
            conn.last_heartbeat = time.time()
            conn.mode = payload.get("net_state", conn.mode)
            await db.execute(
                "UPDATE machines SET online = 1, mode = ?, last_heartbeat = ? WHERE ip = ?",
                (conn.mode, conn.last_heartbeat, conn.ip),
            )

        elif msg_type == MsgType.STATUS:
            conn.mode = payload.get("net_state", conn.mode)
            await db.execute(
                "UPDATE machines SET mode = ?, online = 1, last_heartbeat = ? WHERE ip = ?",
                (conn.mode, time.time(), conn.ip),
            )

        elif msg_type == MsgType.BROWSING_UPDATE:
            domains = payload.get("domains", [])
            ts = time.time()
            for domain in domains[-50:]:
                await db.execute(
                    "INSERT INTO browsing_logs (ip, domain, ts) VALUES (?, ?, ?)",
                    (conn.ip, domain.get("domain", domain) if isinstance(domain, dict) else domain, ts),
                )

    async def _build_rules_payload(self) -> dict:
        db = get_db()
        settings = await db.get_settings()
        mode = settings.get("filter_mode", FilterMode.WHITELIST)
        lan_subnets = settings.get("lan_subnets", ["192.168.1.0/24"])
        upstream_dns = settings.get("upstream_dns", "114.114.114.114")
        if mode == FilterMode.BLACKLIST:
            rows = await db.fetchall(
                "SELECT domain FROM blacklist_rules WHERE enabled = 1"
            )
        else:
            rows = await db.fetchall(
                "SELECT domain FROM whitelist_rules WHERE enabled = 1"
            )
        return {
            "domains": [r["domain"] for r in rows],
            "lan_subnets": lan_subnets,
            "controller_ip": self._get_local_ip(),
            "upstream_dns": upstream_dns,
            "mode": mode,
            "tray_pwd_hash": settings.get("tray_password_hash", ""),
            "unlock_pwd_hash": settings.get("unlock_password_hash", ""),
        }

    async def push_rules(self, targets: Optional[list] = None):
        payload = await self._build_rules_payload()
        await self.broadcast(msg_update_rules(
            domains=payload["domains"],
            lan_subnets=payload["lan_subnets"],
            controller_ip=payload["controller_ip"],
            upstream_dns=payload["upstream_dns"],
            mode=payload["mode"],
            tray_pwd_hash=payload.get("tray_pwd_hash", ""),
            unlock_pwd_hash=payload.get("unlock_pwd_hash", ""),
        ), targets=targets)

    async def set_filter(self, mode: str, targets: Optional[list] = None):
        enabled = mode != FilterMode.NORMAL
        await self.broadcast(msg_set_filter(enabled=enabled, mode=mode), targets=targets)
        db = get_db()
        if not targets:
            await db.execute("UPDATE machines SET mode = ?", (mode,))
        else:
            for ip in targets:
                await db.execute("UPDATE machines SET mode = ? WHERE ip = ?", (mode, ip))

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

    @staticmethod
    def _get_local_ip() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"


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
