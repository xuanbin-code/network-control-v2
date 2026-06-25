"""Pydantic 共享数据模型"""

from typing import List, Optional
from pydantic import BaseModel, Field


class MachineInfo(BaseModel):
    ip: str
    hostname: str = ""
    mac: Optional[str] = None
    mode: str = "disconnect"
    online: bool = True
    last_heartbeat: Optional[float] = None


class RuleItem(BaseModel):
    id: Optional[int] = None
    domain: str
    enabled: bool = True


class NetworkSettings(BaseModel):
    ws_port: int = 8765
    api_port: int = 8770
    heartbeat_interval: int = 20
    heartbeat_timeout: int = 60
    lan_subnets: List[str] = Field(default_factory=lambda: ["192.168.1.0/24"])
    upstream_dns: str = "114.114.114.114"


class WsMessage(BaseModel):
    type: str
    payload: dict = Field(default_factory=dict)
    ts: Optional[float] = None
