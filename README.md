# Network Control v2

基于 Vue 3 + Electron + Python FastAPI 重构的局域网网络访问控制系统。

## 功能特性

- 四种网络状态切换：正常上网 / 白名单 / 黑名单 / 断网
- 教师端批量或单台控制学生机
- 白名单双层过滤：DNS 拦截 + 路由表动态放行
- 开机默认断网（fail-closed）
- 断线自动重连 + 状态恢复
- 浏览监控（DNS 查询日志）
- 拔网线检测 + 全屏锁屏 + 超时关机
- 教师端 HTTP 外部控制接口
- 系统托盘：学生机退出需密码验证

## 技术栈

- **前端 UI**：Vue 3 + Vite + Electron + Element Plus
- **后端服务**：Python + FastAPI + WebSocket
- **数据库**：SQLite（教师端）
- **打包**：PyInstaller + electron-builder
- **平台**：Windows 优先

## 项目结构

```
network-control-v2/
├── packages/
│   ├── shared/              # 共享协议、常量、Pydantic 模型
│   ├── teacher-backend/     # 教师端 Python 后端
│   ├── teacher-app/         # 教师端 Electron + Vue3
│   ├── student-backend/     # 学生端 Python 后端
│   └── student-app/         # 学生端 Electron + Vue3
├── scripts/
│   ├── dev-start.ps1        # 一键启动开发环境
│   ├── build-teacher.bat    # 打包教师端
│   ├── build-student.bat    # 打包学生端
│   ├── install-student-service.bat
│   └── uninstall-student-service.bat
└── README.md
```

## 开发环境要求

- Node.js >= 20
- Python >= 3.10
- Windows 10/11（学生端路由/防火墙/DNS 控制依赖 Windows）

## 快速开始

### 1. 安装依赖

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

### 2. 启动开发环境

在项目根目录执行：

```powershell
.\scripts\dev-start.ps1
```

会同时启动：
- 教师端后端：`http://127.0.0.1:8771`
- 学生端后端：`http://127.0.0.1:8772`
- 教师端前端：`http://127.0.0.1:5173`
- 学生端前端：`http://127.0.0.1:5174`

> 学生端后端需要**管理员权限**才能修改路由/防火墙/DNS；开发测试时建议也以管理员身份运行 PowerShell。

### 3. 配置学生端

编辑 `packages/student-backend/config.json`，把 `controller_url` 改成教师机 IP：

```json
{
  "controller_url": "ws://192.168.1.100:8765",
  "controller_api_url": "http://192.168.1.100:8770"
}
```

### 4. 打包

```bat
# 打包教师端
scripts\build-teacher.bat

# 打包学生端
scripts\build-student.bat
```

产物分别位于：
- `packages/teacher-app/release/`
- `packages/student-app/release/`

### 5. 安装学生端服务（管理员）

```bat
scripts\install-student-service.bat
```

卸载：

```bat
scripts\uninstall-student-service.bat
```

## 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 教师端 WebSocket | 8765 | 学生端连接 |
| 教师端外部 HTTP | 8770 | 外部教学软件调用 |
| 教师端本地 API | 8771 | Electron 前端调用 |
| 学生端本地 API | 8772 | Electron 前端调用 |

## 教师端 HTTP 控制接口

主控端对外提供与原 Network_Control 兼容的 HTTP 接口，供其它程序一键控制：

```bash
POST/GET /api/network/enable          # 一键开网（全部学生端）
POST/GET /api/network/disable         # 一键禁网（全部学生端）
POST/GET /api/network/enable_ip?ip=   # 按 IP 开单台
POST/GET /api/network/disable_ip?ip=  # 按 IP 禁单台
GET      /api/status                  # 学生端列表及状态
GET      /api/health                  # 健康检查
```

## 工作模式

| 状态 | DNS | 防火墙 | 路由 |
|------|-----|--------|------|
| `normal` | 上游 DNS | 全部放行 | 默认网关存在 |
| `whitelist` | 127.0.0.1 | 默认封锁 + 仅放行白名单 | 删默认路由，按 DNS 结果动态加 /32 主机路由 |
| `blacklist` | 127.0.0.1 | 清空（仅 DNS 拦截黑名单） | 默认网关存在 |
| `disconnect` | 上游 DNS | 清空 | 删默认路由，保留到教师端 /32 路由 |

## 注意事项

- 学生端需要管理员权限安装 Windows 服务。
- `controller_url` 建议填写 IP，断网状态下无法解析域名。
- 正式使用请修改默认密码（admin123）对应的 SHA256 哈希。
- 白名单/黑名单/断网模式会修改本机网络设置，请在授权的教学管理场景中使用。

## 从源码构建

```bat
:: 教师端后端
cd packages/teacher-backend
pyinstaller main.spec --noconfirm

:: 学生端后端
cd ../student-backend
pyinstaller main.spec --noconfirm
```

## 致谢

本项目核心网络控制逻辑迁移自 [tuyaosheng/Network_Control](https://github.com/tuyaosheng/Network_Control.git)。
