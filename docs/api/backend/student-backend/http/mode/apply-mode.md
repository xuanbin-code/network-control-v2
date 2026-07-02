# POST /apply_mode

本地强制切换网络模式，主要用于前端测试，不依赖教师端下发。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/apply_mode` |
| 方法 | `POST` |
| 服务 | 学生端本地 HTTP（默认 `127.0.0.1:8772`） |
| 请求体 | `application/json` |

---

## 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mode` | string | 是 | 目标模式：`normal` / `whitelist` / `blacklist` / `disconnect` |

### 请求示例

```json
{
  "mode": "whitelist"
}
```

---

## 响应示例

```json
{
  "ok": true,
  "mode": "whitelist"
}
```

---

## 处理逻辑

1. 更新全局状态 `state.mode`。
2. 在线程池中调用 `apply_filter_mode`，修改 Windows 路由表/防火墙/DNS。
3. 同步本地 DNS 服务器模式与域名规则。
4. 清除 DNS 缓存。
5. 同步托盘图标状态。

---

## 注意事项

- 修改系统网络配置需要 Windows 管理员权限。
- 正常运行时，模式由教师端通过 WebSocket 控制，不建议频繁调用此接口。

---

## 源码位置

`packages/student-backend/app/api/v1/endpoints/mode.py`
