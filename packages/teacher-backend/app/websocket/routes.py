"""WebSocket 路由注册"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.services.ws_manager import ws_manager


def register_ws_routes(app: FastAPI):
    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket):
        conn = await ws_manager.connect(ws)
        try:
            while True:
                data = await ws.receive_json()
                await ws_manager.handle_message(conn, data)
        except WebSocketDisconnect:
            await ws_manager.disconnect(conn)
        except Exception as e:
            print(f"[WS] 异常: {e}")
            await ws_manager.disconnect(conn)
