"""本地 DNS 过滤服务器

基于 dnslib 实现 127.0.0.1:53 DNS 代理与过滤：
- 白名单：只放行指定域名（含通配符），其余 NXDOMAIN；
         解析白名单域名时把上游返回的 IP 实时传给回调（用于动态加路由）。
- 黑名单：拦截指定域名，其余正常解析。

迁移自原 Network_Control 项目的 dns_server.py。
"""

import logging
import socket
import threading
from typing import Callable, Optional

from dnslib import DNSRecord, RCODE, QTYPE
from dnslib.server import DNSServer, BaseResolver

from shared.protocol import FilterMode

logger = logging.getLogger("dns_server")


class FilterResolver(BaseResolver):
    def __init__(self, domains: list[str], upstream_dns: str,
                 mode: str = FilterMode.WHITELIST,
                 on_query: Optional[Callable[[str], None]] = None,
                 on_resolved_ips: Optional[Callable[[list[str]], None]] = None):
        self._lock = threading.Lock()
        self.upstream_dns = upstream_dns
        self.mode = mode
        self.on_query = on_query
        self.on_resolved_ips = on_resolved_ips
        self._domains: list[str] = []
        self.update_domains(domains)

    def update_domains(self, domains: list[str]):
        normalized = [d.strip().lower().rstrip(".") for d in domains if d.strip()]
        with self._lock:
            self._domains = normalized
        logger.info(f"[{self.mode}] 规则已更新，共 {len(normalized)} 条域名")

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
            logger.warning(f"上游DNS查询失败: {e}")
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
                logger.debug(f"[白名单拦截] {qname}")
                reply = request.reply()
                reply.header.rcode = RCODE.NXDOMAIN
                return reply

            if qtype == QTYPE.AAAA:
                return request.reply()

            response = self._forward(request)
            if self.on_resolved_ips and response.header.rcode == RCODE.NOERROR:
                ips = self._extract_a_records(response)
                if ips:
                    try:
                        self.on_resolved_ips(ips)
                    except Exception as e:
                        logger.warning(f"动态加路由失败 ({qname}): {e}")
            return response

        else:  # BLACKLIST
            if matched:
                logger.debug(f"[黑名单拦截] {qname}")
                reply = request.reply()
                reply.header.rcode = RCODE.NXDOMAIN
                return reply
            return self._forward(request)


class DnsFilterServer:
    def __init__(self, upstream_dns: str = "114.114.114.114",
                 mode: str = FilterMode.WHITELIST,
                 domains: Optional[list[str]] = None,
                 on_query: Optional[Callable[[str], None]] = None,
                 on_resolved_ips: Optional[Callable[[list[str]], None]] = None,
                 bind_addr: str = "127.0.0.1", port: int = 53):
        self.upstream_dns = upstream_dns
        self.bind_addr = bind_addr
        self.port = port
        self._mode = mode
        self._on_query = on_query
        self._on_resolved_ips = on_resolved_ips
        self.resolver = FilterResolver(
            domains=domains or [],
            upstream_dns=upstream_dns,
            mode=mode,
            on_query=on_query,
            on_resolved_ips=on_resolved_ips,
        )
        self._server: Optional[DNSServer] = None
        self._thread: Optional[threading.Thread] = None
        self.running = False

    def start(self):
        if self.running:
            return
        try:
            self._server = DNSServer(self.resolver,
                                     address=self.bind_addr,
                                     port=self.port,
                                     tcp=False)
            self._thread = threading.Thread(target=self._server.start, daemon=True)
            self._thread.start()
            self.running = True
            logger.info(f"DNS服务器已启动: {self.bind_addr}:{self.port} 模式={self.resolver.mode}")
        except Exception as e:
            logger.error(f"DNS服务器启动失败: {e}")
            raise

    def stop(self):
        if self._server and self.running:
            try:
                self._server.stop()
            except Exception:
                pass
            self.running = False
            logger.info("DNS服务器已停止")

    def update_domains(self, domains: list[str]):
        self.resolver.update_domains(domains)

    def set_mode(self, mode: str):
        self._mode = mode
        self.resolver.mode = mode

    def update_upstream(self, upstream_dns: str):
        self.upstream_dns = upstream_dns
        self.resolver.upstream_dns = upstream_dns
