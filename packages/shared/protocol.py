"""WebSocket 消息协议常量与辅助函数

与原 Network_Control 兼容并扩展，同时支持当前 v2 的 payload 封装格式。
"""

import json
from typing import Any, Optional


class MsgType:
    # 学生端 -> 教师端
    REGISTER = "register"
    HEARTBEAT = "heartbeat"
    STATUS = "status"
    ACK = "ack"
    BROWSING_UPDATE = "browsing_update"

    # 教师端 -> 学生端
    UPDATE_RULES = "update_rules"
    SET_FILTER = "set_filter"
    DISCONNECT = "disconnect"
    RECONNECT = "reconnect"
    GET_STATUS = "get_status"
    TEST_MESSAGE = "test_message"
    BLACK_SCREEN = "black_screen"
    BLACK_SCREEN_UNLOCK = "black_screen_unlock"


class FilterMode:
    NORMAL = "normal"
    WHITELIST = "whitelist"
    BLACKLIST = "blacklist"
    DISCONNECT = "disconnect"


# 默认端口
DEFAULT_WS_PORT = 8765
DEFAULT_API_PORT = 8770
DEFAULT_LOCAL_API_PORT_TEACHER = 8771
DEFAULT_LOCAL_API_PORT_STUDENT = 8772

# 心跳间隔（秒）
HEARTBEAT_INTERVAL = 20
HEARTBEAT_TIMEOUT = 60


def make_msg(msg_type: str, payload: Optional[dict] = None, **kwargs) -> str:
    """构造一条 WebSocket 文本消息。

    优先使用 payload 字段承载业务数据；额外的 kwargs 会合并到顶层，
    以便兼容旧版扁平协议（如源仓库的 controller/agent）。
    """
    data: dict[str, Any] = {"type": msg_type}
    if payload is not None:
        data["payload"] = payload
    if kwargs:
        # 避免 kwargs 与 payload 里的同名字段冲突：kwargs 写入顶层
        data.update(kwargs)
    return json.dumps(data, ensure_ascii=False)


def parse_msg(raw: str) -> dict:
    """解析 WebSocket 消息，失败返回空字典。"""
    try:
        return json.loads(raw)
    except Exception:
        return {}


def extract_payload(msg: dict) -> dict:
    """取出消息中的 payload；若消息是旧版扁平格式，则返回除 type 外的全部字段。"""
    if "payload" in msg and isinstance(msg["payload"], dict):
        return msg["payload"]
    return {k: v for k, v in msg.items() if k != "type"}


# ── 学生端 → 教师端 ─────────────────────────────────────────────

def msg_register(hostname: str, ip: str, mac: str = "", mode: str = FilterMode.DISCONNECT) -> str:
    return make_msg(MsgType.REGISTER, payload={
        "hostname": hostname,
        "ip": ip,
        "mac": mac,
        "mode": mode,
    })


def msg_heartbeat(filter_active: bool = False, net_state: str = FilterMode.NORMAL) -> str:
    return make_msg(MsgType.HEARTBEAT, payload={
        "filter_active": filter_active,
        "net_state": net_state,
    })


def msg_status(filter_active: bool = False,
               dns_running: bool = False,
               rule_count: int = 0,
               net_state: str = FilterMode.NORMAL) -> str:
    return make_msg(MsgType.STATUS, payload={
        "filter_active": filter_active,
        "dns_running": dns_running,
        "rule_count": rule_count,
        "net_state": net_state,
    })


def msg_browsing_update(domains: list[dict]) -> str:
    """domains: [{"domain": str, "ts": str}, ...]"""
    return make_msg(MsgType.BROWSING_UPDATE, payload={"domains": domains})


def msg_ack(ok: bool, message: str = "") -> str:
    return make_msg(MsgType.ACK, payload={"ok": ok, "message": message})


# ── 教师端 → 学生端 ─────────────────────────────────────────────

def msg_update_rules(domains: list[str],
                     lan_subnets: list[str],
                     controller_ip: str,
                     upstream_dns: str,
                     mode: str = FilterMode.WHITELIST,
                     tray_pwd_hash: str = "",
                     unlock_pwd_hash: str = "") -> str:
    return make_msg(MsgType.UPDATE_RULES, payload={
        "domains": domains,
        "lan_subnets": lan_subnets,
        "controller_ip": controller_ip,
        "upstream_dns": upstream_dns,
        "mode": mode,
        "tray_pwd_hash": tray_pwd_hash,
        "unlock_pwd_hash": unlock_pwd_hash,
    })


def msg_set_filter(enabled: bool = True, mode: str = FilterMode.WHITELIST) -> str:
    return make_msg(MsgType.SET_FILTER, payload={
        "enabled": enabled,
        "mode": mode,
    })


def msg_disconnect() -> str:
    return make_msg(MsgType.DISCONNECT)


def msg_reconnect() -> str:
    return make_msg(MsgType.RECONNECT)


def msg_get_status() -> str:
    return make_msg(MsgType.GET_STATUS)


def msg_test_message(content: str) -> str:
    """教师端发送测试消息到学生端"""
    return make_msg(MsgType.TEST_MESSAGE, payload={
        "content": content,
    })


def msg_black_screen(countdown_seconds: int = 30) -> str:
    """教师端远程触发学生端黑屏安静窗口。

    Args:
        countdown_seconds: 倒计时秒数；0 表示持续黑屏，需手动/IPC 解除。
    """
    return make_msg(MsgType.BLACK_SCREEN, payload={
        "countdown_seconds": countdown_seconds,
    })


def msg_black_screen_unlock() -> str:
    """教师端远程解除学生端黑屏安静窗口。"""
    return make_msg(MsgType.BLACK_SCREEN_UNLOCK)
