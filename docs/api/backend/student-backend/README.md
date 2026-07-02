# 学生端后端接口

> 对应源码：`packages/student-backend/app/api/v1/endpoints/`

---

## HTTP 接口索引

| 路由 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/test_message` | GET | 获取最近一条教师端测试消息 |
| `/status` | GET | 获取运行状态 |
| `/config` | GET / POST | 获取/更新配置 |
| `/reload_config` | POST | 重新加载 `config.json` |
| `/apply_mode` | POST | 本地强制切换网络模式 |
| `/test/black_screen` | POST | 启动黑屏安静测试窗口 |
| `/test/black_screen_unlock` | POST | 解除黑屏安静测试窗口 |

---

## WebSocket 角色

学生端后端作为 **客户端** 主动连接教师端：

```
ws://<教师IP>:8765/ws
```

上行消息见 [教师端 WebSocket 文档](../teacher-backend/websocket/README.md) 中的「学生端 → 教师端」部分。

---

## 源码对应关系

```
app/api/v1/endpoints/
├── health.py          → /health
├── test_message.py    → /test_message
├── status.py          → /status
├── config.py          → /config, /reload_config
├── mode.py            → /apply_mode
└── test_features.py   → /test/black_screen, /test/black_screen_unlock
```
