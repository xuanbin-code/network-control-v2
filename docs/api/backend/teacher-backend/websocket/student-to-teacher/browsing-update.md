# browsing_update（学生端 → 教师端）

学生端批量上报最近的 DNS 查询记录，供教师端查看浏览日志。

---

## 消息方向

学生端 → 教师端

---

## 发送频率

每 **15 秒** 发送一次。

---

## 消息格式

```json
{
  "type": "browsing_update",
  "payload": {
    "domains": [
      { "domain": "www.baidu.com", "ts": "20:15:30" },
      { "domain": "www.example.com", "ts": "20:15:31" }
    ]
  }
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `domains` | array | DNS 查询记录数组 |
| `domains[].domain` | string | 域名 |
| `domains[].ts` | string | 查询时间（格式化字符串） |

---

## 教师端处理逻辑

将记录写入 `browsing_logs` 表，每次最多处理最近 50 条。

---

## 源码位置

- 发送：`packages/student-backend/app/services/ws_client.py`
- 接收处理：`packages/teacher-backend/app/services/ws_manager.py`
- 协议定义：`packages/shared/protocol.py`
