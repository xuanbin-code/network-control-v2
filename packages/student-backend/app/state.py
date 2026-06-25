"""学生端全局状态"""

from shared.protocol import FilterMode


class AgentState:
    def __init__(self):
        self.mode = FilterMode.DISCONNECT
        self.connected = False
        self.controller_ip = ""
        self.hostname = ""
        self.mac = ""
        self.last_heartbeat = 0

    def set_mode(self, mode: str):
        self.mode = mode


state = AgentState()
