"""WebSocket 客户端：主动连接教师端"""

import asyncio
import json
import logging
import socket
import time
import uuid

import websockets

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from shared.protocol import (
    MsgType, FilterMode,
    msg_register, msg_heartbeat, msg_status, msg_ack,
    msg_browsing_update, parse_msg, extract_payload,
)

from app.services.black_screen import start_black_screen, stop_black_screen

from app.core.config import CONFIG
from app.core.state import state
from app.services.tray_icon import current_tray

logger = logging.getLogger("ws_client")

HEARTBEAT_INTERVAL = 20
RECONNECT_DELAY = 5
BROWSING_INTERVAL = 15

# 当前活跃的 WebSocket 客户端实例，供外部（如调试 API）获取/更新
_current_client = None


def get_current_client():
    return _current_client


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_mac() -> str:
    mac = uuid.getnode()
    return ":".join(f"{(mac >> i) & 0xff:02x}" for i in range(40, -1, -8))


def parse_controller_ip(url: str) -> str:
    """从 ws://ip:port 中解析 IP，用于断网时保留教师端路由。"""
    import re
    import ipaddress
    m = re.match(r"wss?://([^:/]+)", url)
    host = m.group(1) if m else ""
    try:
        ipaddress.ip_address(host)
        return host
    except ValueError:
        return ""


class StudentWebSocketClient:
    def __init__(self):
        global _current_client
        _current_client = self
        self.uri = CONFIG.get("controller_url", "ws://192.168.1.100:8765")
        # 兼容：若 url 没有路径，追加 /ws（当前 v2 后端使用 FastAPI /ws 路由）
        if not self.uri.rstrip('/').endswith('/ws'):
            self.uri = self.uri.rstrip('/') + '/ws'
        self.ws = None
        self.running = False
        self.reconnect_interval = RECONNECT_DELAY
        self._filter_handler = None
        self._dns_server = None

    def set_filter_handler(self, handler):
        self._filter_handler = handler

    def set_dns_server(self, dns_server):
        self._dns_server = dns_server

    def reload_uri(self):
        """从最新 CONFIG 重新读取教师端地址，供调试 API 使用。"""
        new_uri = CONFIG.get("controller_url", "ws://192.168.1.100:8765")
        if not new_uri.rstrip('/').endswith('/ws'):
            new_uri = new_uri.rstrip('/') + '/ws'
        if new_uri != self.uri:
            logger.info(f"WebSocket address updated: {self.uri} -> {new_uri}")
            self.uri = new_uri

    async def run(self):
        self.running = True
        loop = asyncio.get_event_loop()
        while self.running:
            try:
                logger.info(f"Connecting to controller: {self.uri}")
                async with websockets.connect(self.uri, ping_interval=None) as ws:
                    self.ws = ws
                    state.connected = True
                    state.controller_url = self.uri
                    state.controller_ip = parse_controller_ip(self.uri)
                    state.hostname = await loop.run_in_executor(None, socket.gethostname)
                    state.mac = get_mac()
                    logger.info("Connected to controller")
                    await self._register()
                    await self._recv_loop()
            except Exception as e:
                logger.warning(f"Connection exception: {e}")
            finally:
                self.ws = None
                state.connected = False
            if self.running:
                logger.info(f"Reconnecting in {self.reconnect_interval} seconds...")
                await asyncio.sleep(self.reconnect_interval)

    async def _register(self):
        loop = asyncio.get_event_loop()
        local_ip = await loop.run_in_executor(None, get_local_ip)
        await self.send(msg_register(
            hostname=state.hostname,
            ip=local_ip,
            mac=state.mac,
            mode=state.mode,
        ))

    async def _recv_loop(self):
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        browsing_task = asyncio.create_task(self._browsing_loop())
        try:
            async for message in self.ws:
                await self._handle_message(json.loads(message))
        finally:
            heartbeat_task.cancel()
            browsing_task.cancel()
            try:
                await heartbeat_task
                await browsing_task
            except asyncio.CancelledError:
                pass

    async def _heartbeat_loop(self):
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            try:
                await self.send(msg_heartbeat(
                    filter_active=state.filter_active,
                    net_state=state.mode,
                ))
            except Exception:
                break

    async def _browsing_loop(self):
        while True:
            await asyncio.sleep(BROWSING_INTERVAL)
            try:
                domains = state.get_recent_domains()
                if domains:
                    await self.send(msg_browsing_update(domains))
            except Exception:
                break

    async def _handle_message(self, data: dict):
        msg_type = data.get("type")
        payload = extract_payload(data)
        logger.debug(f"Received: {msg_type} {payload}")

        if msg_type == MsgType.SET_FILTER:
            mode = payload.get("mode", FilterMode.NORMAL)
            enabled = payload.get("enabled", True)
            if not enabled:
                mode = FilterMode.NORMAL
            await self._apply_mode(mode)

        elif msg_type == MsgType.UPDATE_RULES:
            domains = payload.get("domains", [])
            mode = payload.get("mode", FilterMode.WHITELIST)
            state.lan_subnets = payload.get("lan_subnets", state.lan_subnets)
            state.controller_ip = payload.get("controller_ip", state.controller_ip)
            state.upstream_dns = payload.get("upstream_dns", state.upstream_dns)

            if mode == FilterMode.WHITELIST:
                state.whitelist_domains = domains
            else:
                state.blacklist_domains = domains
            state.rule_count = len(domains)

            # 更新密码
            tray_pwd_hash = payload.get("tray_pwd_hash", "")
            unlock_pwd_hash = payload.get("unlock_pwd_hash", "")
            if tray_pwd_hash:
                CONFIG["tray_password_hash"] = tray_pwd_hash
            if unlock_pwd_hash:
                CONFIG["unlock_password_hash"] = unlock_pwd_hash
            if tray_pwd_hash or unlock_pwd_hash:
                from app.core.config import save_config
                save_config(CONFIG)

            # 热更新 DNS 规则
            if self._dns_server and self._dns_server.running:
                self._dns_server.set_mode(mode)
                self._dns_server.update_domains(domains)
                self._dns_server.update_upstream(state.upstream_dns)

            await self.send(msg_ack(True, "Rules applied"))

        elif msg_type == MsgType.DISCONNECT:
            await self._apply_mode(FilterMode.DISCONNECT)

        elif msg_type == MsgType.RECONNECT:
            await self._apply_mode(FilterMode.NORMAL)

        elif msg_type == MsgType.GET_STATUS:
            await self.send(msg_status(
                filter_active=state.filter_active,
                dns_running=self._dns_server.running if self._dns_server else False,
                rule_count=state.rule_count,
                net_state=state.mode,
            ))

        elif msg_type == MsgType.TEST_MESSAGE:
            content = payload.get("content", "")
            state.last_test_message = content
            state.last_test_message_ts = time.time()
            logger.info(f"收到测试消息: {content}")

        elif msg_type == MsgType.BLACK_SCREEN:
            countdown = payload.get("countdown_seconds", 30)
            logger.info(f"收到黑屏指令，倒计时: {countdown} 秒")
            try:
                result = start_black_screen(countdown)
                if result.get("ok"):
                    await self.send(msg_ack(True, f"Black screen started: {result['countdown_seconds']}s"))
                else:
                    error_msg = result.get("error", "unknown error")
                    logger.error(f"启动黑屏失败: {error_msg}")
                    await self.send(msg_ack(False, f"Black screen failed: {error_msg}"))
            except Exception as e:
                logger.error(f"启动黑屏失败: {e}")
                await self.send(msg_ack(False, f"Black screen failed: {e}"))

        elif msg_type == MsgType.BLACK_SCREEN_UNLOCK:
            logger.info("收到解除黑屏指令")
            try:
                ok = stop_black_screen()
                await self.send(msg_ack(ok, "Black screen unlock command sent"))
            except Exception as e:
                logger.error(f"解除黑屏失败: {e}")
                await self.send(msg_ack(False, f"Black screen unlock failed: {e}"))

    async def _apply_mode(self, mode: str):
        from app.services.network_filter import apply_filter_mode
        state.set_mode(mode)
        await asyncio.get_event_loop().run_in_executor(
            None,
            apply_filter_mode,
            mode,
            state.whitelist_domains,
            state.blacklist_domains,
            state.lan_subnets,
            state.controller_ip,
            state.upstream_dns,
        )
        # Blacklist mode requires local DNS filtering
        if self._dns_server and self._dns_server.running:
            self._dns_server.set_mode(mode)
        # Sync tray icon state
        if current_tray:
            try:
                current_tray.set_net_state(mode)
            except Exception:
                pass
        await self.send(msg_status(
            filter_active=state.filter_active,
            dns_running=self._dns_server.running if self._dns_server else False,
            rule_count=state.rule_count,
            net_state=state.mode,
        ))

    async def send(self, msg: str):
        if self.ws and self._is_open(self.ws):
            try:
                await self.ws.send(msg)
            except Exception as e:
                logger.warning(f"Send failed: {e}")

    @staticmethod
    def _is_open(ws) -> bool:
        try:
            return ws.open
        except AttributeError:
            pass
        try:
            import websockets
            return ws.state == websockets.protocol.State.OPEN
        except Exception:
            return False

    def stop(self):
        self.running = False
