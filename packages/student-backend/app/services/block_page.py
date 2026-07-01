"""拦截提示页服务

为被 DNS 拦截的域名返回一个本地 HTTP 页面，提示学生不要浏览无关信息。
监听 127.0.0.1:80（可配置），由 dns_server 把被拦截域名解析到本机。
"""

import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

logger = logging.getLogger("block_page")

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 80

# 简洁的拦截提示页，告诉学生不要浏览无关信息
BLOCK_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>访问已拦截</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f3f4f6;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .card {
            background: #fff;
            padding: 48px 40px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            max-width: 480px;
            text-align: center;
        }
        .icon { font-size: 64px; margin-bottom: 16px; }
        h1 { font-size: 24px; color: #111827; margin: 0 0 12px; }
        p { color: #6b7280; line-height: 1.7; margin: 0 0 24px; }
        .footer { font-size: 12px; color: #9ca3af; }
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">🚫</div>
        <h1>访问已拦截</h1>
        <p>该网页与当前课堂内容无关，已被教师端网络管理系统拦截。<br>请专注于课堂学习，不要浏览无关信息。</p>
        <div class="footer">Network Control Student Agent</div>
    </div>
</body>
</html>
"""

BLOCK_BODY = BLOCK_HTML.encode("utf-8")


class _BlockPageHandler(BaseHTTPRequestHandler):
    """对所有路径和 Host 返回同一个拦截提示页。"""

    def do_GET(self):
        self._serve()

    def do_POST(self):
        self._serve()

    def do_HEAD(self):
        self._serve_head()

    def _serve(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(BLOCK_BODY)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(BLOCK_BODY)

    def _serve_head(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(BLOCK_BODY)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def log_message(self, format, *args):
        logger.debug(format % args)


class BlockPageServer:
    """本地拦截提示页 HTTP 服务。"""

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.running = False

    def start(self):
        if self.running:
            return
        try:
            self._server = ThreadingHTTPServer((self.host, self.port), _BlockPageHandler)
            self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._thread.start()
            self.running = True
            logger.info(f"拦截提示页服务已启动: http://{self.host}:{self.port}")
        except Exception as e:
            logger.error(f"拦截提示页服务启动失败: {e}")
            raise

    def stop(self):
        if self._server and self.running:
            try:
                self._server.shutdown()
            except Exception:
                pass
            self.running = False
            logger.info("拦截提示页服务已停止")
