# GET/POST /network/disable_ip

按 IP 禁止单台学生端上网（切换到 `disconnect` 模式）。兼容原 Network_Control 的 HTTP 控制接口。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/network/disable_ip` |
| 方法 | `GET`、`POST` |
| 服务 | `local_app`（8771）、`external_app`（8770） |

---

## 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `ip` | string | 是 | 学生端 IP |

### 请求示例

```
GET /api/network/disable_ip?ip=192.168.1.101
```

---

## 响应示例

```json
{
  "ok": true,
  "action": "disable_ip",
  "ip": "192.168.1.101",
  "message": "已下发『禁止上网』指令: 192.168.1.101"
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `ok` | boolean | 是否成功 |
| `action` | string | 固定为 `"disable_ip"` |
| `ip` | string | 目标学生端 IP |
| `message` | string | 操作结果描述 |

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 400 | 缺少 `ip` 参数 |

---

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/network.py`
