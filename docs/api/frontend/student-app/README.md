# 学生端前端 API

> 源文件：`packages/student-app/src/renderer/api/student.ts`

---

## 基地址

```ts
const BASE = 'http://127.0.0.1:8772/api'
```

---

## 函数索引

| 函数 | 对应后端接口 | 说明 |
|------|--------------|------|
| `getStatus()` | `GET /status` | 获取运行状态 |
| `getConfig()` | `GET /config` | 获取配置 |
| `updateConfig(data)` | `POST /config` | 更新配置 |
| `applyMode(mode)` | `POST /apply_mode` | 切换网络模式 |
| `reloadConfig()` | `POST /reload_config` | 重新加载配置 |
| `testBlackScreen(countdownSeconds)` | `POST /test/black_screen` | 启动黑屏测试 |
| `sendBlackScreenUnlock()` | `POST /test/black_screen_unlock` | 解除黑屏测试 |

---

## Store 调用

上述函数主要在 `packages/student-app/src/renderer/stores/student.ts` 的 `useStudentStore` 中被调用。
