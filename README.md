# Network Control v2

基于 Vue 3 + Electron + Python FastAPI 重构的局域网网络访问控制系统。

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
- Windows 10/11

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

### 3. 打包

```bat
# 打包教师端
scripts\build-teacher.bat

# 打包学生端
scripts\build-student.bat
```

产物分别位于：
- `packages/teacher-app/release/`
- `packages/student-app/release/`

### 4. 安装学生端服务

```bat
scripts\install-student-service.bat
```

## 核心功能

- 四种网络状态切换：正常上网 / 白名单 / 黑名单 / 断网
- 教师端批量或单台控制学生机
- 白名单双层过滤：DNS 拦截 + 路由表动态放行
- 开机默认断网（fail-closed）
- 断线自动重连 + 状态恢复
- 浏览监控（DNS 查询日志）
- 拔网线检测 + 全屏锁屏 + 超时关机
- 教师端 HTTP 外部控制接口

## 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 教师端 WebSocket | 8765 | 学生端连接 |
| 教师端外部 HTTP | 8770 | 外部教学软件调用 |
| 教师端本地 API | 8771 | Electron 前端调用 |
| 学生端本地 API | 8772 | Electron 前端调用 |

## 注意事项

- 学生端需要管理员权限安装 Windows 服务。
- 当前为骨架版本，DNS/路由表/锁屏等核心控制逻辑已预留接口，后续逐步迁移原项目实现。
- 开发时学生端需手动配置 `controller_url` 指向教师端 IP。
