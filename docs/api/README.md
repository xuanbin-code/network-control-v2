# Network Control v2 — 接口文档总览

> 本文档按「后端接口」和「前端接口」分别组织，每个接口/函数单独存放一个 Markdown 文件，目录结构与代码路由保持一致。

---

## 目录结构

```
docs/api/
├── README.md                      # 本文件
├── backend/                       # 后端 HTTP / WebSocket 接口
│   ├── README.md
│   ├── teacher-backend/           # 教师端后端（Python FastAPI）
│   │   ├── README.md
│   │   ├── http/                  # HTTP REST 接口
│   │   └── websocket/             # WebSocket 消息协议
│   └── student-backend/           # 学生端后端（Python FastAPI）
│       ├── README.md
│       ├── http/
│       └── websocket/
└── frontend/                      # 前端 API 封装
    ├── README.md
    ├── teacher-app/               # 教师端 Electron + Vue3
    │   └── api/
    └── student-app/               # 学生端 Electron + Vue3
        └── api/
```

---

## 端口速查

| 服务 | 地址 | 用途 |
|------|------|------|
| 教师端本地 HTTP API | `http://127.0.0.1:8771/api/*` | 教师端 Electron 前端 |
| 教师端外部 HTTP API | `http://127.0.0.1:8770/api/*` | 第三方教学软件 |
| 教师端 WebSocket | `ws://<教师IP>:8765/ws` | 学生端长连接 |
| 学生端本地 HTTP API | `http://127.0.0.1:8772/api/*` | 学生端 Electron 前端 |

---

## 说明

- 后端文档中的接口路径均省略公共前缀 `/api`，实际请求时需拼接完整地址。
- 前端文档中的函数均来自 `src/renderer/api/*.ts`，是渲染进程调用本地后端的封装。
- 旧版聚合文档仍保留在 [`docs/student-api.md`](../student-api.md) 和 [`docs/communication-flow.md`](../communication-flow.md)。
