# 教师端前端 API

> 源文件：`packages/teacher-app/src/renderer/api/teacher.ts`

---

## 基地址

```ts
const BASE = 'http://127.0.0.1:8771/api'
```

---

## 函数索引

| 函数 | 对应后端接口 | 说明 |
|------|--------------|------|
| `getHealth()` | `GET /health` | 健康检查 |
| `getMachines()` | `GET /machines` | 获取学生机列表 |
| `getStatus()` | `GET /status` | 获取学生机状态 |
| `setNetwork(mode, targets?)` | `POST /network/set` | 设置网络模式 |
| `enableNetwork()` | `GET /network/enable` | 一键开网 |
| `disableNetwork()` | `GET /network/disable` | 一键禁网 |
| `enableIp(ip)` | `GET /network/enable_ip` | 按 IP 开单台 |
| `disableIp(ip)` | `GET /network/disable_ip` | 按 IP 禁单台 |
| `getRules()` | `GET /rules` | 获取黑白名单规则 |
| `addRule(listType, domain)` | `POST /rules/{list_type}` | 添加规则 |
| `deleteRule(listType, ruleId)` | `DELETE /rules/{list_type}/{rule_id}` | 删除规则 |
| `toggleRule(listType, ruleId)` | `POST /rules/{list_type}/{rule_id}/toggle` | 切换规则启用状态 |
| `getSettings()` | `GET /settings` | 获取系统设置 |
| `updateSetting(key, value)` | `POST /settings` | 更新系统设置 |
| `scanNetwork(subnet)` | `GET /scan` | 扫描网段 |
| `sendTestMessage(message, targets?)` | `POST /test/send` | 发送测试消息 |
| `sendBlackScreen(countdownSeconds?, targets?)` | `POST /test/black_screen` | 发送黑屏指令 |
| `sendBlackScreenUnlock(targets?)` | `POST /test/black_screen_unlock` | 发送解除黑屏指令 |
| `getServerInfo()` | `GET /server_info` | 获取服务器信息 |

---

## Store 调用

上述函数主要在 `packages/teacher-app/src/renderer/stores/teacher.ts` 的 `useTeacherStore` 中被调用。
