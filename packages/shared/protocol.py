"""WebSocket 消息协议常量

与原 Network_Control 兼容并扩展。
"""


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
