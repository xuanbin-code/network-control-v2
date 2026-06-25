"""本地 DNS 过滤服务器（骨架）

后续实现基于 dnslib 的 127.0.0.1:53 DNS 代理与过滤。
"""


class DnsFilterServer:
    def __init__(self, upstream_dns: str = "114.114.114.114"):
        self.upstream_dns = upstream_dns
        self.running = False

    def start(self):
        self.running = True
        print(f"[DNS] DNS 过滤服务器启动（上游: {self.upstream_dns}）")

    def stop(self):
        self.running = False
        print("[DNS] DNS 过滤服务器停止")
