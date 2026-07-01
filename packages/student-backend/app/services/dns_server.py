"""本地 DNS 过滤服务器

基于 dnslib 实现 127.0.0.1:53 DNS 代理与过滤：
- 白名单：只放行指定域名（含通配符），其余 NXDOMAIN；
         解析白名单域名时把上游返回的 IP 实时传给回调（用于动态加路由）。
- 黑名单：拦截指定域名，其余正常解析。

迁移自原 Network_Control 项目的 dns_server.py。
"""

import asyncio
import logging
import socket
import threading
from typing import Callable, Optional

from dnslib import DNSRecord, RCODE, QTYPE, A, RR
from dnslib.server import DNSServer, BaseResolver

from shared.protocol import FilterMode

logger = logging.getLogger("dns_server")


class FilterResolver(BaseResolver):
    def __init__(self, domains: list[str], upstream_dns: str,
                 mode: str = FilterMode.WHITELIST,
                 on_query: Optional[Callable[[str], None]] = None,
                 on_resolved_ips: Optional[Callable[[list[str]], None]] = None,
                 loop: Optional[asyncio.AbstractEventLoop] = None,
                 block_page_ip: Optional[str] = "127.0.0.1"):
        self._lock = threading.Lock()
        self.upstream_dns = upstream_dns
        self.mode = mode
        self.on_query = on_query
        self.on_resolved_ips = on_resolved_ips
        self._loop = loop
        self.block_page_ip = block_page_ip
        self._domains: list[str] = []
        self.update_domains(domains)

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def set_block_page_ip(self, ip: Optional[str]):
        self.block_page_ip = ip

    def _block_reply(self, request):
        """返回本地拦截提示页 IP；未配置时回退到 NXDOMAIN。"""
        reply = request.reply()
        if self.block_page_ip and request.q.qtype == QTYPE.A:
            reply.add_answer(RR(request.q.qname, QTYPE.A, rdata=A(self.block_page_ip), ttl=30))
        # 非 A 查询（如 AAAA）返回空答案，让浏览器回落到 A 记录
        return reply

    def _schedule_add_routes(self, ips: list[str], qname: str):
        # 调用前 snapshot 回调，避免多线程/静态检查时出现 None 调用
        callback = self.on_resolved_ips
        if callback is None:
            return

        def _run():
            try:
                callback(ips)
            except Exception as e:
                logger.warning(f"Dynamic route add failed ({qname}): {e}")

        if self._loop:
            try:
                self._loop.run_in_executor(None, _run)
            except Exception as e:
                logger.warning(f"Failed to schedule dynamic route add ({qname}): {e}")
                _run()
        else:
            _run()

    def update_domains(self, domains: list[str]):
        normalized = [d.strip().lower().rstrip(".") for d in domains if d.strip()]
        with self._lock:
            self._domains = normalized
        logger.info(f"[{self.mode}] Rules updated, {len(normalized)} domain(s)")

    def _matches(self, qname: str) -> bool:
        name = qname.lower().rstrip(".")
        with self._lock:
            for pattern in self._domains:
                if pattern.startswith("*."):
                    base = pattern[2:]
                    if name == base or name.endswith("." + base):
                        return True
                else:
                    if name == pattern or name.endswith("." + pattern):
                        return True
        return False

    def _forward(self, request):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            sock.sendto(request.pack(), (self.upstream_dns, 53))
            data, _ = sock.recvfrom(4096)
            sock.close()
            return DNSRecord.parse(data)
        except Exception as e:
            logger.warning(f"Upstream DNS query failed: {e}")
            reply = request.reply()
            reply.header.rcode = RCODE.SERVFAIL
            return reply

    @staticmethod
    def _extract_a_records(response) -> list[str]:
        ips: list[str] = []
        try:
            for rr in response.rr:
                if rr.rtype == QTYPE.A:
                    ips.append(str(rr.rdata))
        except Exception:
            pass
        return ips

    def resolve(self, request, handler):
        qname = str(request.q.qname)
        qtype = request.q.qtype

        if self.on_query:
            clean = qname.rstrip(".")
            if "." in clean and not clean.endswith(".local") and not clean.startswith("_"):
                try:
                    self.on_query(clean)
                except Exception:
                    pass

        matched = self._matches(qname)

        if self.mode == FilterMode.WHITELIST:
            if not matched:
                logger.debug(f"[Whitelist block] {qname}")
                return self._block_reply(request)

            if qtype == QTYPE.AAAA:
                return request.reply()

            response = self._forward(request)
            if self.on_resolved_ips and response.header.rcode == RCODE.NOERROR:
                ips = self._extract_a_records(response)
                if ips:
                    # 动态加路由涉及 PowerShell 系统命令，不能阻塞 DNS 线程
                    self._schedule_add_routes(ips, qname)
            return response

        else:  # BLACKLIST
            if matched:
                logger.debug(f"[Blacklist block] {qname}")
                return self._block_reply(request)
            return self._forward(request)


class DnsFilterServer:
    def __init__(self, upstream_dns: str = "114.114.114.114",
                 mode: str = FilterMode.WHITELIST,
                 domains: Optional[list[str]] = None,
                 on_query: Optional[Callable[[str], None]] = None,
                 on_resolved_ips: Optional[Callable[[list[str]], None]] = None,
                 bind_addr: str = "127.0.0.1", port: int = 53,
                 block_page_ip: Optional[str] = "127.0.0.1"):
        self.upstream_dns = upstream_dns
        self.bind_addr = bind_addr
        self.port = port
        self._mode = mode
        self._on_query = on_query
        self._on_resolved_ips = on_resolved_ips
        self.block_page_ip = block_page_ip
        self.resolver = FilterResolver(
            domains=domains or [],
            upstream_dns=upstream_dns,
            mode=mode,
            on_query=on_query,
            on_resolved_ips=on_resolved_ips,
            loop=None,
            block_page_ip=block_page_ip,
        )
        self._server: Optional[DNSServer] = None
        self._thread: Optional[threading.Thread] = None
        self.running = False

    def start(self):
        if self.running:
            return
        # 在事件循环运行期间启动 DNS 时，把 loop 传给 resolver 用于异步执行动态加路由
        try:
            self.resolver.set_loop(asyncio.get_running_loop())
        except Exception:
            pass
        try:
            self._server = DNSServer(self.resolver,
                                     address=self.bind_addr,
                                     port=self.port,
                                     tcp=False)
            self._thread = threading.Thread(target=self._server.start, daemon=True)
            self._thread.start()
            self.running = True
            logger.info(f"DNS server started: {self.bind_addr}:{self.port} mode={self.resolver.mode}")
        except Exception as e:
            logger.error(f"DNS server start failed: {e}")
            raise

    def stop(self):
        if self._server and self.running:
            try:
                self._server.stop()
            except Exception:
                pass
            self.running = False
            logger.info("DNS server stopped")

    def update_domains(self, domains: list[str]):
        self.resolver.update_domains(domains)

    def set_mode(self, mode: str):
        self._mode = mode
        self.resolver.mode = mode

    def update_upstream(self, upstream_dns: str):
        self.upstream_dns = upstream_dns
        self.resolver.upstream_dns = upstream_dns

    def set_block_page_ip(self, ip: Optional[str]):
        self.block_page_ip = ip
        self.resolver.set_block_page_ip(ip)
