"""WebSocket 客户端：主动连接教师端"""

import asyncio
import json
import socket
import time

import websockets

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from shared.protocol import MsgType, FilterMode

from .config import CONFIG
from .state import state


class StudentWebSocketClient:
    def __init__(self):
        self.uri = CONFIG.get("controller_url", "ws://192.168.1.100:8765")
        self.ws = None
        self.running = False
        self.reconnect_interval = 5

    async def run(self):
        self.running = True
        while self.running:
            try:
                print(f"[WS Client] 连接教师端: {self.uri}")
                async with websockets.connect(self.uri) as ws:
                    self.ws = ws
                    state.connected = True
                    await self._register()
                    await self._recv_loop()
            except Exception as e:
                print(f"[WS Client] 连接异常: {e}")
            finally:
                state.connected = False
                self.ws = None
            if self.running:
                print(f"[WS Client] {self.reconnect_interval}秒后重连...")
                await asyncio.sleep(self.reconnect_interval)

    async def _register(self):
        hostname = socket.gethostname()
        await self.send({
            "type": MsgType.REGISTER,
            "payload": {
                "hostname": hostname,
                "mac": "",
                "mode": state.mode,
            },
        })

    async def _recv_loop(self):
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        try:
            async for message in self.ws:
                await self._handle_message(json.loads(message))
        finally:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass

    async def _heartbeat_loop(self):
        while True:
            await asyncio.sleep(20)
            await self.send({
                "type": MsgType.HEARTBEAT,
                "payload": {"mode": state.mode},
            })

    async def _handle_message(self, data: dict):
        msg_type = data.get("type")
        payload = data.get("payload", {})
        print(f"[WS Client] 收到: {msg_type} {payload}")

        if msg_type == MsgType.SET_FILTER:
            mode = payload.get("mode", FilterMode.NORMAL)
            await self._apply_mode(mode)

        elif msg_type == MsgType.UPDATE_RULES:
            # 保存规则并应用（后续由 filter 模块处理）
            pass

        elif msg_type == MsgType.DISCONNECT:
            await self._apply_mode(FilterMode.DISCONNECT)

        elif msg_type == MsgType.RECONNECT:
            await self._apply_mode(FilterMode.NORMAL)

    async def _apply_mode(self, mode: str):
        from .filter.network_filter import apply_filter_mode
        state.set_mode(mode)
        apply_filter_mode(mode)
        await self.send({
            "type": MsgType.STATUS,
            "payload": {"mode": mode},
        })

    async def send(self, msg: dict):
        if self.ws and self.ws.open:
            try:
                await self.ws.send(json.dumps(msg))
            except Exception as e:
                print(f"[WS Client] 发送失败: {e}")

    def stop(self):
        self.running = False
