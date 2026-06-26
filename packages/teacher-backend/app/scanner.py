"""局域网 IP 扫描：发现可能运行学生端后端的机器"""

import asyncio
import ipaddress
from typing import List


async def scan_ip_range(subnet: str, port: int = 8765, timeout: float = 0.5) -> List[str]:
    """扫描指定网段的 port 端口，返回可达 IP 列表。"""
    try:
        network = ipaddress.IPv4Network(subnet, strict=False)
    except Exception:
        return []

    results = []

    async def check(ip_str: str):
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(ip_str, port), timeout=timeout
            )
            writer.close()
            await writer.wait_closed()
            results.append(ip_str)
        except Exception:
            pass

    await asyncio.gather(*[check(str(ip)) for ip in network.hosts()])
    return sorted(results)
