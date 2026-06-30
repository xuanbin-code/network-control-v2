"""学生端全局状态"""

import collections
import threading

from shared.protocol import FilterMode


class AgentState:
    def __init__(self):
        self.mode = FilterMode.DISCONNECT
        self.connected = False
        self.controller_ip = ""
        self.controller_url = ""
        self.hostname = ""
        self.mac = ""
        self.last_heartbeat = 0
        self.filter_active = False
        self.dns_running = False
        self.rule_count = 0
        self.whitelist_domains: list[str] = []
        self.blacklist_domains: list[str] = []
        self.lan_subnets: list[str] = []
        self.upstream_dns = "114.114.114.114"
        self._recent_domains: collections.deque = collections.deque(maxlen=50)
        self._domains_lock = threading.Lock()

    def set_mode(self, mode: str):
        self.mode = mode
        # disconnect 模式下网络同样处于被控状态，应视为 filter_active
        self.filter_active = mode in (FilterMode.WHITELIST, FilterMode.BLACKLIST, FilterMode.DISCONNECT)

    def on_query_domain(self, domain: str):
        from datetime import datetime
        with self._domains_lock:
            self._recent_domains.append({
                "domain": domain,
                "ts": datetime.now().strftime("%H:%M:%S"),
            })

    def get_recent_domains(self) -> list[dict]:
        with self._domains_lock:
            return list(self._recent_domains)


state = AgentState()
