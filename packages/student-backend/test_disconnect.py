#!/usr/bin/env python3
"""学生端断网测试脚本

功能：
  1. 启动本地 DNS 服务器（127.0.0.1:53），将除白名单外的所有域名解析到本地封锁页面。
  2. 启动本地 HTTP 服务器（127.0.0.1:8080），返回“网络已断开”提示页。
  3. 修改系统 DNS 指向本地 DNS，并断开默认路由（保留到教师端的路由）。
  4. 按 Enter 或 Ctrl+C 结束后自动恢复联网和 DNS。

用法（需要管理员权限）：
  cd packages/student-backend
  python test_disconnect.py

注意：
  - 教师端地址从 config.json / config.py 的 controller_url 读取，IP 形式最佳。
  - 若 controller_url 是域名，会加入 DNS 白名单，避免教师端连接被屏蔽。
"""

import ctypes
import ipaddress
import json
import re
import signal
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# 保证 stdout 输出 UTF-8，避免中文乱码
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# 让脚本能找到 shared 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dnslib import A, DNSRecord, QTYPE, RCODE, RR
from dnslib.server import BaseResolver, DNSServer

from app.config import CONFIG
from app.filter.network_filter import (
    disconnect_internet,
    reconnect_internet,
    restore_adapter_dns,
    set_adapter_dns,
)

# 封锁页面（任意域名访问都会落到这个页面）
BLOCK_PAGE_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>网络已断开</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f3f4f6;
      font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
      color: #374151;
    }
    .box {
      text-align: center;
      padding: 40px;
      background: #fff;
      border-radius: 16px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.08);
      max-width: 480px;
    }
    .icon {
      width: 72px;
      height: 72px;
      margin: 0 auto 20px;
      background: #fee2e2;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 36px;
      color: #dc2626;
    }
    h1 { font-size: 26px; margin-bottom: 12px; color: #b91c1c; }
    p { font-size: 16px; line-height: 1.6; margin-bottom: 8px; }
    .tip { font-size: 13px; color: #6b7280; margin-top: 20px; }
  </style>
</head>
<body>
  <div class="box">
    <div class="icon">!</div>
    <h1>网络已断开</h1>
    <p>当前正处于断网测试模式，无法访问互联网。</p>
    <p>请关闭测试脚本或按提示恢复联网。</p>
    <div class="tip">教师端连接已被保留，不受影响。</div>
  </div>
</body>
</html>
"""

REDIRECT_IP = "127.0.0.1"
HTTP_PORT = 8080
DNS_PORT = 53


def parse_controller_ip(url: str) -> str:
    """从 ws://ip:port 或域名中解析 IP。"""
    m = re.match(r"wss?://([^:/]+)", url)
    host = m.group(1) if m else ""
    try:
        ipaddress.ip_address(host)
        return host
    except ValueError:
        return ""


def get_controller_host(url: str) -> str:
    """获取 controller_url 中的 host（IP 或域名）。"""
    m = re.match(r"wss?://([^:/]+)", url)
    return m.group(1) if m else ""


class BlockPageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = BLOCK_PAGE_HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

    def log_message(self, fmt, *args):
        # 屏蔽默认访问日志，保持界面干净
        pass


class RedirectResolver(BaseResolver):
    """DNS 解析器：白名单域名走正常解析，其余解析到 REDIRECT_IP。"""

    def __init__(self, redirect_ip: str, upstream_dns: str, whitelist: list[str]):
        self.redirect_ip = redirect_ip
        self.upstream_dns = upstream_dns
        self.whitelist = [d.lower().rstrip(".") for d in whitelist if d.strip()]

    def _is_whitelisted(self, qname: str) -> bool:
        name = qname.lower().rstrip(".")
        for pattern in self.whitelist:
            if pattern.startswith("*."):
                base = pattern[2:]
                if name == base or name.endswith("." + base):
                    return True
            else:
                if name == pattern or name.endswith("." + pattern):
                    return True
        return False

    def _forward(self, request: DNSRecord) -> DNSRecord:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        try:
            sock.sendto(request.pack(), (self.upstream_dns, 53))
            data, _ = sock.recvfrom(4096)
            return DNSRecord.parse(data)
        finally:
            sock.close()

    def resolve(self, request: DNSRecord, handler):
        qname = str(request.q.qname)
        qtype = request.q.qtype
        reply = request.reply()

        # 只处理 A 记录，其他类型返回空响应
        if qtype != QTYPE.A:
            return reply

        if self._is_whitelisted(qname):
            try:
                return self._forward(request)
            except Exception as e:
                print(f"[DNS] 白名单上游查询失败 {qname}: {e}")
                reply.header.rcode = RCODE.SERVFAIL
                return reply

        # 重定向到封锁页面
        reply.add_answer(RR(qname, QTYPE.A, rdata=A(self.redirect_ip), ttl=5))
        return reply


class TestDisconnect:
    def __init__(self):
        self.controller_url = CONFIG.get("controller_url", "ws://192.168.1.100:8765/ws")
        self.controller_ip = parse_controller_ip(self.controller_url)
        self.controller_host = get_controller_host(self.controller_url)
        self.upstream_dns = CONFIG.get("upstream_dns", "114.114.114.114")
        self.dns_server: DNSServer | None = None
        self.http_server: ThreadingHTTPServer | None = None
        self.http_thread: threading.Thread | None = None
        self._restore_done = False

    def _build_whitelist(self) -> list[str]:
        whitelist = [
            "localhost",
            "*.local",
            self.upstream_dns,          # 上游 DNS 本身
        ]
        if self.controller_host and self.controller_host != self.controller_ip:
            # controller_url 是域名，放行该域名
            whitelist.append(self.controller_host)
            whitelist.append(f"*.{self.controller_host}")
        # 放行局域网常见后缀（可根据需要扩展）
        for suffix in CONFIG.get("lan_subnets", []):
            # 仅把网段转成域名的场景很少，这里保持简单
            pass
        return whitelist

    def _start_http(self):
        self.http_server = ThreadingHTTPServer((REDIRECT_IP, HTTP_PORT), BlockPageHandler)
        self.http_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
        self.http_thread.start()
        print(f"[HTTP] 封锁页面已启动: http://{REDIRECT_IP}:{HTTP_PORT}")

    def _start_dns(self):
        whitelist = self._build_whitelist()
        resolver = RedirectResolver(REDIRECT_IP, self.upstream_dns, whitelist)
        self.dns_server = DNSServer(resolver, address=REDIRECT_IP, port=DNS_PORT, tcp=False)
        thread = threading.Thread(target=self.dns_server.start, daemon=True)
        thread.start()
        print(f"[DNS] 已启动: {REDIRECT_IP}:{DNS_PORT}，白名单: {whitelist}")

    def _stop_http(self):
        if self.http_server:
            self.http_server.shutdown()
            self.http_server.server_close()
            print("[HTTP] 已停止")

    def _stop_dns(self):
        if self.dns_server:
            self.dns_server.stop()
            print("[DNS] 已停止")

    def _apply_disconnect(self):
        print(f"[网络] 教师端地址: {self.controller_url} (IP: {self.controller_ip or '域名未解析'})")
        print("[网络] 正在设置本地 DNS...")
        set_adapter_dns(REDIRECT_IP)
        print("[网络] 正在断开默认网络（保留教师端路由）...")
        disconnect_internet(controller_ip=self.controller_ip)
        print("[网络] 断网测试模式已开启")

    def _restore(self):
        if self._restore_done:
            return
        self._restore_done = True
        print("\n[网络] 正在恢复联网...")
        self._stop_dns()
        self._stop_http()
        reconnect_internet()
        restore_adapter_dns()
        print("[网络] 已恢复联网")

    def run(self):
        try:
            self._start_http()
            self._start_dns()
            self._apply_disconnect()
            print("\n" + "=" * 50)
            print("断网测试已生效，请打开浏览器访问任意网站测试。")
            print(f"所有非白名单域名都会被重定向到 http://{REDIRECT_IP}:{HTTP_PORT}")
            print("教师端连接已保留。")
            print("=" * 50)
            print("按 Enter 键恢复联网并退出...")
            input()
        except KeyboardInterrupt:
            print("\n[信息] 收到 Ctrl+C")
        finally:
            self._restore()


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def main():
    print("=" * 50)
    print("Network Control v2 — 学生端断网测试脚本")
    print("=" * 50)

    if not is_admin():
        print("\n[错误] 本脚本需要管理员权限才能修改 DNS 和路由表。")
        print("请以管理员身份运行 PowerShell，然后执行：")
        print("  python test_disconnect.py")
        sys.exit(1)

    td = TestDisconnect()

    # 注册信号处理，确保意外退出也能恢复
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda _s, _f: (td._restore(), sys.exit(0)))

    try:
        td.run()
    except Exception as e:
        print(f"\n[错误] 运行异常: {e}")
        td._restore()
        raise


if __name__ == "__main__":
    main()
