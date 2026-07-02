# GET /machines

获取已注册的学生机列表，按在线状态优先、IP 升序排列。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/machines` |
| 方法 | `GET` |
| 服务 | `local_app`（8771） |

---

## 请求参数

无。

---

## 响应示例

```json
{
  "machines": [
    {
      "ip": "192.168.1.101",
      "hostname": "STU-001",
      "mac": "aa:bb:cc:dd:ee:ff",
      "mode": "whitelist",
      "online": 1,
      "last_heartbeat": 1719500000.123
    },
    {
      "ip": "192.168.1.102",
      "hostname": "STU-002",
      "mac": "aa:bb:cc:dd:ee:00",
      "mode": "disconnect",
      "online": 0,
      "last_heartbeat": 1719499900.456
    }
  ]
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `machines` | array | 学生机记录数组 |
| `machines[].ip` | string | 学生端 IP |
| `machines[].hostname` | string | 学生端主机名 |
| `machines[].mac` | string | 学生端 MAC 地址 |
| `machines[].mode` | string | 当前网络模式 |
| `machines[].online` | integer | 是否在线：`1` 在线，`0` 离线 |
| `machines[].last_heartbeat` | number | 最后心跳时间（Unix 时间戳） |

---

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/machines.py`
