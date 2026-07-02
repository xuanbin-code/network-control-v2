# Network Control v2 — AI Agent 项目指南

> 本文档面向 AI 编码助手，概括项目架构、构建方式、代码组织与开发约定。
> 项目自然语言为中文，代码注释和文档优先使用中文。

---

## 1. 项目概述

Network Control v2 是一套面向教学机房/局域网场景的“网络访问控制”系统。

- **教师端**：Electron + Vue3 桌面应用，批量或单台控制学生机的上网状态。
- **学生端**：Electron + Vue3 桌面应用 + Windows 后台服务，接收教师端指令并修改本机网络配置。
- **通信方式**：WebSocket（教师端 ← 学生端长连接）+ 本地 HTTP API（Electron 前端 ↔ Python 后端）。

核心能力：

- 四种网络模式切换：`normal`（正常上网）、`whitelist`（白名单）、`blacklist`（黑名单）、`disconnect`（断网）。
- 白名单双层过滤：本地 DNS 代理 + 路由表动态放行 `/32` 主机路由。
- 开机默认断网（fail-closed），等待教师端下发规则。
- 拔网线检测、全屏锁屏、超时关机。
- 系统托盘退出需密码验证。
- 教师端对外提供 HTTP 接口，供第三方教学软件一键控制。

> 核心网络控制逻辑迁移自 [tuyaosheng/Network_Control](https://github.com/tuyaosheng/Network_Control.git)。

---

## 2. 技术栈

| 层级 | 技术 |
|------|------|
| 前端 UI | Vue 3.4 + TypeScript 5 + Composition API (`<script setup lang="ts">`) |
| 前端构建 | Vite 5 + `vite-plugin-electron` + `vite-plugin-electron-renderer` |
| 桌面壳 | Electron 30 |
| UI 组件库 | shadcn-vue + Reka UI + Tailwind CSS + `@lucide/vue` |
| 状态管理 | Pinia 2（组合式 Store） |
| 路由 | Vue Router 4（hash 模式） |
| 后端服务 | Python 3.10+ + FastAPI + Uvicorn |
| WebSocket | `websockets` 库（学生端客户端）、FastAPI 原生 WebSocket（教师端服务端） |
| 数据库 | SQLite；教师端使用 `aiosqlite` 异步裸 SQL |
| 打包 | 后端 PyInstaller 6；前端 Electron + electron-builder |
| 平台 | Windows 优先（学生端依赖 Windows 路由表/防火墙/PowerShell/pywin32） |

---

## 3. 项目结构

```
network-control-v2/
├── package.json                 # 根目录脚本入口
├── README.md                    # 面向人类的说明文档
├── .gitignore
├── scripts/
│   ├── dev-start.ps1            # 一键启动四个开发服务
│   ├── build-teacher.bat        # 打包教师端完整安装包
│   ├── build-student.bat        # 打包学生端完整安装包
│   ├── install-student-service.bat    # 安装学生端 Windows 服务
│   └── uninstall-student-service.bat  # 卸载学生端 Windows 服务
└── packages/
    ├── shared/                  # Python 共享协议与常量
    │   ├── __init__.py
    │   └── protocol.py
    ├── teacher-backend/         # 教师端 Python 后端
    │   ├── app/
    │   │   ├── main.py                      # 入口：三服务器并发
    │   │   ├── core/
    │   │   │   └── config.py                # 路径/端口/环境变量
    │   │   ├── db/
    │   │   │   ├── database.py              # Database 类 + get_db
    │   │   │   └── init.py                  # 初始化 SQL 与默认设置
    │   │   ├── schemas/
    │   │   │   └── requests.py              # Pydantic 请求模型
    │   │   ├── services/
    │   │   │   ├── scanner.py               # 局域网 IP 扫描
    │   │   │   └── ws_manager.py            # WebSocket 连接管理
    │   │   ├── websocket/
    │   │   │   └── routes.py                # WebSocket 路由注册
    │   │   └── api/
    │   │       ├── deps.py                  # 公共依赖
    │   │       └── v1/
    │   │           └── endpoints/           # HTTP API 路由（按资源拆分）
    │   ├── main.spec            # PyInstaller 配置
    │   └── requirements.txt
    ├── teacher-app/             # 教师端 Electron + Vue3 前端
    │   ├── src/
    │   │   ├── main/index.js    # Electron 主进程
    │   │   ├── preload/index.js # preload 脚本
    │   │   └── renderer/        # Vue 渲染进程
    │   ├── vite.config.js
    │   ├── electron-builder.yml
    │   └── package.json
    ├── student-backend/         # 学生端 Python 后端/代理
    │   ├── app/
    │   │   ├── main.py                      # 入口
    │   │   ├── core/
    │   │   │   ├── config.py                # config.json 读写 + 默认值
    │   │   │   └── state.py                 # 全局状态
    │   │   ├── api/
    │   │   │   └── v1/
    │   │   │       └── endpoints/           # 本地 HTTP API（按资源拆分）
    │   │   ├── services/
    │   │   │   ├── ws_client.py             # WebSocket 客户端（连接教师端）
    │   │   │   ├── network_filter.py        # 防火墙/路由/DNS 控制
    │   │   │   ├── dns_server.py            # 本地 DNS 代理
    │   │   │   ├── network_monitor.py       # 拔网线检测
    │   │   │   ├── lock_screen.py           # PyQt6 全屏锁屏
    │   │   │   └── tray_icon.py             # 系统托盘
    │   │   ├── filter/
    │   │   │   └── __init__.py              # 兼容层：重新导出 services 中的过滤 API
    │   │   ├── windows/
    │   │   │   └── service.py               # Windows 服务封装
    │   │   └── config.py                    # 兼容层：重新导出 core.config
    │   ├── main.spec
    │   └── requirements.txt
    └── student-app/             # 学生端 Electron + Vue3 前端
        ├── src/
        │   ├── main/index.js
        │   ├── preload/index.js
        │   └── renderer/
        ├── vite.config.js
        ├── electron-builder.yml
        └── package.json
```

---

## 4. 关键配置与端口

### 4.1 默认端口

| 服务 | 端口 | 说明 |
|------|------|------|
| 教师端 WebSocket | `8765` | 学生端长连接 |
| 教师端外部 HTTP | `8770` | 外部教学软件调用 |
| 教师端本地 API | `8771` | Electron 教师端前端调用 |
| 学生端本地 API | `8772` | Electron 学生端前端调用 |
| 学生端 Vite dev | `5174` | 开发服务器 |
| 教师端 Vite dev | `5173` | 开发服务器 |

端口可通过环境变量覆盖：

- 教师端：`NC_WS_PORT`、`NC_API_PORT`、`NC_LOCAL_API_PORT`、`NC_WS_HOST`、`NC_API_HOST`。
- 学生端：支持 `NC_CONTROLLER_URL`、`NC_CONTROLLER_API_URL`、`NC_LOCAL_API_HOST`、`NC_LOCAL_API_PORT`、`NC_UPSTREAM_DNS`、`NC_LAN_SUBNETS`、`NC_TRAY_VISIBLE`、`NC_TRAY_PASSWORD_HASH`、`NC_UNLOCK_PASSWORD_HASH`，可在 `.env` 或 `.env.development` 中配置。

### 4.2 学生端配置

配置优先级：`config.json` > 环境变量（`.env` / `.env.development`）> `DEFAULT_CONFIG` 默认值。

首次运行会自动生成 `packages/student-backend/config.json`，默认值见 `app/core/config.py`。开发环境下推荐直接修改 `packages/student-backend/.env.development`，无需改动 `config.json`：

```env
NC_CONTROLLER_URL=ws://127.0.0.1:8765/ws
NC_CONTROLLER_API_URL=http://127.0.0.1:8770
NC_LOCAL_API_HOST=127.0.0.1
NC_LOCAL_API_PORT=8772
NC_UPSTREAM_DNS=114.114.114.114
NC_LAN_SUBNETS=["192.168.1.0/24"]
NC_TRAY_VISIBLE=true
```

> 若需本地自定义（含密码等敏感信息），可复制 `.env.example` 为 `.env`，`.env` 已被 `.gitignore` 忽略，不会进入版本控制。

生产环境仍使用 `config.json`：

```json
{
  "controller_url": "ws://192.168.1.100:8765/ws",
  "controller_api_url": "http://192.168.1.100:8770",
  "local_api_host": "127.0.0.1",
  "local_api_port": 8772,
  "upstream_dns": "114.114.114.114",
  "lan_subnets": ["192.168.1.0/24"],
  "tray_visible": true,
  "tray_password_hash": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",
  "unlock_password_hash": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
}
```

> `tray_password_hash` / `unlock_password_hash` 默认对应明文 `admin123`，SHA-256 小写十六进制。

---

## 5. 开发环境准备

### 5.1 前置要求

- Node.js >= 20
- Python >= 3.10
- Windows 10/11（学生端功能强依赖 Windows 管理员权限）

### 5.2 安装依赖

```powershell
# Python 后端依赖
cd packages/teacher-backend
pip install -r requirements.txt

cd ../student-backend
pip install -r requirements.txt

# Node 前端依赖
cd ../teacher-app
npm install

cd ../student-app
npm install
```

### 5.3 一键启动开发环境

在项目根目录执行：

```powershell
.\scripts\dev-start.ps1
```

会同时启动：

- 教师端后端：`http://127.0.0.1:8771`
- 学生端后端：`http://127.0.0.1:8772`
- 教师端前端：`http://127.0.0.1:5173`
- 学生端前端：`http://127.0.0.1:5174`

> 学生端后端需要**管理员权限**才能修改路由/防火墙/DNS；建议以管理员身份运行 PowerShell。

### 5.4 单独启动

根目录 `package.json` 提供快捷脚本：

```bash
npm run dev:teacher-backend   # cd packages/teacher-backend && python -m app.main
npm run dev:student-backend   # cd packages/student-backend && python -m app.main
npm run dev:teacher           # cd packages/teacher-app && npm run dev
npm run dev:student           # cd packages/student-app && npm run dev
```

---

## 6. 构建与打包

### 6.1 教师端

```bat
scripts\build-teacher.bat
```

流程：

1. `pip install -r packages/teacher-backend/requirements.txt`
2. `pyinstaller packages/teacher-backend/main.spec --noconfirm` → `packages/teacher-backend/dist/teacher-backend.exe`
3. `cd packages/teacher-app && npm install && npm run build:win` → `packages/teacher-app/release/`

### 6.2 学生端

```bat
scripts\build-student.bat
```

流程：

1. `pip install -r packages/student-backend/requirements.txt`
2. `pyinstaller packages/student-backend/main.spec --noconfirm` → `packages/student-backend/dist/student-backend.exe`
3. `cd packages/student-app && npm install && npm run build:win` → `packages/student-app/release/`

### 6.3 前端单独构建

```bash
cd packages/teacher-app
npm run build        # vue-tsc --noEmit && vite build && electron-builder
npm run build:win    # 仅 Windows
npm run preview

cd packages/student-app
npm run build
npm run build:win
```

### 6.4 后端单独构建

```bash
cd packages/teacher-backend
pyinstaller main.spec --noconfirm

cd packages/student-backend
pyinstaller main.spec --noconfirm
```

### 6.5 安装学生端 Windows 服务

打包后，以管理员身份执行：

```bat
scripts\install-student-service.bat
```

服务名：`NetControlAgent`。

卸载：

```bat
scripts\uninstall-student-service.bat
```

---

## 7. 运行时架构

### 7.1 教师端三服务器模型

`teacher-backend/app/main.py` 在同一线程内启动三个 Uvicorn 实例：

| App | 监听 | 用途 |
|-----|------|------|
| `local_app` | `127.0.0.1:8771` | Electron 教师端前端调用 + 教师端本地 WebSocket |
| `external_app` | `127.0.0.1:8770` | 外部教学软件 HTTP 控制接口 |
| `ws_app` | `0.0.0.0:8765` | 学生端 WebSocket 长连接 |

所有 FastAPI 实例均开启 `CORS allow_origins=["*"]`。

### 7.2 学生端进程模型

- `student-backend.exe` 作为普通进程运行时：启动 FastAPI HTTP API、WebSocket 客户端、DNS 服务器、网络监控、系统托盘、锁屏子进程。
- 也可通过 `python -m app.windows_service install/start/remove` 注册为 Windows 服务。
- 锁屏子进程入口：`python -m app.main --lock <sha256_hash>`。

### 7.3 Electron 主进程职责

- 创建 `BrowserWindow`，加载 Vite dev URL 或 `dist/index.html`。
- 生产环境从 `process.resourcesPath/teacher-backend/teacher-backend.exe`（或 `student-backend/student-backend.exe`）启动 Python 后端。
- `preload/index.js` 仅暴露 `window.electronAPI.platform`。
- `contextIsolation: true`，`nodeIntegration: false`。

---

## 8. 协议与 API

### 8.1 共享协议（`packages/shared/protocol.py`）

`shared` 是一个纯 Python 包，无第三方依赖，被两个后端通过 `from shared.protocol import ...` 引用。

关键常量：

- `MsgType.REGISTER / HEARTBEAT / STATUS / ACK / BROWSING_UPDATE`（学生→教师）
- `MsgType.UPDATE_RULES / SET_FILTER / DISCONNECT / RECONNECT / GET_STATUS`（教师→学生）
- `FilterMode.NORMAL / WHITELIST / BLACKLIST / DISCONNECT`
- `DEFAULT_WS_PORT = 8765`，`DEFAULT_API_PORT = 8770`，`DEFAULT_LOCAL_API_PORT_TEACHER = 8771`，`DEFAULT_LOCAL_API_PORT_STUDENT = 8772`
- `HEARTBEAT_INTERVAL = 20`，`HEARTBEAT_TIMEOUT = 60`

消息默认采用 `{"type": ..., "payload": {...}}` 格式，并兼容旧版扁平格式。

### 8.2 教师端外部 HTTP 接口（`external_app`）

与原 Network_Control 兼容：

```
POST/GET /api/network/enable          # 一键开网（全部学生端）
POST/GET /api/network/disable         # 一键禁网（全部学生端）
POST/GET /api/network/enable_ip?ip=   # 按 IP 开单台
POST/GET /api/network/disable_ip?ip=  # 按 IP 禁单台
GET      /api/status                  # 学生端列表及状态
GET      /api/health                  # 健康检查
```

### 8.3 教师端本地 HTTP 接口（`local_app`）

前缀 `/api`：

- `GET /health`
- `GET /machines`
- `GET /status`
- `POST /network/set`
- `GET|POST /network/enable`、`/network/disable`、`/network/enable_ip`、`/network/disable_ip`
- `GET /scan?subnet=`
- `GET /rules`
- `POST /rules/{whitelist|blacklist}`
- `DELETE /rules/{whitelist|blacklist}/{id}`
- `POST /rules/{whitelist|blacklist}/{id}/toggle`
- `GET /browsing/{ip}?limit=`
- `GET /settings`、`POST /settings`

### 8.4 学生端本地 HTTP 接口

前缀 `/api`：

- `GET /health`
- `GET /status`
- `GET /config`
- `POST /config`
- `POST /apply_mode`

---

## 9. 数据库

仅教师端使用数据库，文件为 `packages/teacher-backend/data/teacher.db`（生产环境位于可执行文件同目录 `data/teacher.db`）。

- 使用 `aiosqlite` 异步裸 SQL，无 ORM。
- 表：`settings`、`machines`、`whitelist_rules`、`blacklist_rules`、`browsing_logs`。
- 单例 `Database` 通过 `asyncio.Lock` 保护并发访问。
- `settings` 表为 key/value 文本，列表值以 JSON 字符串存储。

---

## 10. 代码风格与约定

### 10.1 语言

- 代码注释、docstring、UI 文案、日志使用**中文**。
- 标识符、类型名、API 路由使用英文。

### 10.2 前端

- Vue SFC 使用 `<script setup lang="ts">`。
- 渲染进程使用 TypeScript；Electron 主进程/Preload 仍为 JavaScript（CommonJS）。
- 路径别名 `@/` 指向 `src/renderer/`。
- 状态管理统一使用 Pinia 组合式 Store（见 `stores/teacher.ts`、`stores/student.ts`）。
- HTTP 请求封装在 `api/teacher.ts`、`api/student.ts`，基地址分别为 `http://127.0.0.1:8771/api` 和 `http://127.0.0.1:8772/api`。
- 路由使用 Vue Router 的 `createWebHashHistory`。

### 10.3 后端

- 模块职责分离清晰：教师端 `app/api/v1/endpoints/` 负责 HTTP 路由，`app/services/ws_manager.py` 与 `app/websocket/routes.py` 负责 WebSocket，`app/db/` 负责数据，`app/core/config.py` 负责配置/路径；学生端 `app/api/v1/endpoints/` 负责 HTTP 路由，`app/services/` 负责 WebSocket/过滤/托盘/锁屏等业务逻辑，`app/core/` 负责配置与状态，`app/windows/` 负责 Windows 服务。
- 使用 `sys.path.insert(0, ...)` 在运行时将 `packages/shared` 加入 Python 路径，实现跨包导入。
- `BASE_DIR` 区分开发路径和 PyInstaller 冻结路径（`sys.frozen`）。
- 网络控制逻辑集中在 `student-backend/app/services/network_filter.py`，通过 PowerShell 修改 Windows 路由表、防火墙、DNS。`app/filter/` 仅作为兼容层保留。

### 10.4 共享包

- `packages/shared` 仅保留协议常量，不再包含 Pydantic 模型（旧 `models.py` 已移除）。
- 两个后端直接以相对包兄弟关系导入：`from shared.protocol import ...`。

---

## 11. 测试

当前项目**未配置自动化测试**。

- 无 `pytest.ini`、无 `tests/` 目录、无 `vitest.config`。
- 验证方式以手工运行和端到端联调为主：
  1. 启动教师端后端与学生端后端。
  2. 用教师端前端操作学生机模式切换。
  3. 观察学生端路由表/防火墙/DNS 变化。
  4. 测试拔网线、锁屏、托盘密码、外部 HTTP 接口。

如需新增测试，建议：

- Python 后端使用 `pytest` + `httpx.AsyncClient` 测试 FastAPI 接口。
- 共享协议 `packages/shared/protocol.py` 适合作为首批被单测覆盖的模块。
- 前端可引入 `vitest` 测试 Pinia Store 和 API 封装。

---

## 12. 安全注意事项

> 本项目用于授权的教学/机房管理场景，不当使用会影响网络可用性。

- **管理员权限**：学生端后端修改路由表、防火墙、DNS 需要 Windows 管理员权限。
- **默认密码**：`admin123`（SHA-256 哈希 `240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9`）。正式上线前必须修改学生端 `config.json` 与教师端数据库 `settings` 表中的哈希值。
- **CORS**：教师端三个 FastAPI 实例均设置 `allow_origins=["*"]`，仅绑定本地或内网，不要直接暴露到公网。
- **网络影响**：`whitelist` / `blacklist` / `disconnect` 会修改本机网络设置，开发测试请在隔离环境或虚拟机中进行。
- **学生端退出密码**：系统托盘右键退出需要密码验证，防止学生自行关闭。
- **锁屏自动关机**：全屏锁屏窗口 60 秒未解锁会触发关机，测试时请注意保存工作。

---

## 13. 常见问题

### 13.1 `ModuleNotFoundError: No module named 'shared'`

确保在对应后端目录内启动（如 `packages/student-backend`），且 `packages/shared` 与后端目录为同级包。PyInstaller `main.spec` 已通过 `pathex` 将 `shared` 目录加入打包路径。

### 13.2 学生端后端无法修改网络

以管理员身份运行 PowerShell / CMD 再启动后端。

### 13.3 教师端前端无法连接后端

检查 `127.0.0.1:8771` 是否已启动，以及防火墙是否放行。

### 13.4 打包后前端无法启动后端

确认 `electron-builder.yml` 的 `extraResources` 配置正确，且 PyInstaller 产物已生成在 `../teacher-backend/dist/` 或 `../student-backend/dist/`。

---

## 14. 给 AI 助手的快速参考

- **新增 shadcn-vue 组件**：在两个前端包内分别使用 CLI 安装，例如 `cd packages/teacher-app && npx shadcn-vue@latest add button`。组件统一放在 `src/renderer/components/ui/`。
- **新增 API**：教师端与学生端均优先在 `app/api/v1/endpoints/` 下新增资源文件，然后在 `app/api/v1/__init__.py` 中聚合。并在对应前端 `api/*.ts` 与 Store 中调用。
- **新增 WebSocket 消息类型**：在 `packages/shared/protocol.py` 的 `MsgType` 中定义常量，并补充 `msg_*` 辅助函数；两端分别处理收发。
- **新增网络模式**：修改 `FilterMode`，同步更新 `student-backend/app/services/network_filter.py` 与教师端前端 UI。
- **修改默认端口**：除代码外，注意更新根目录 `README.md`、本文件、教师端 `app/core/config.py` 与学生端默认配置。
- **数据库变更**：在 `teacher-backend/app/db/init.py` 的 `INIT_SQL` 中维护 schema 版本，当前无迁移工具，需手动处理。
