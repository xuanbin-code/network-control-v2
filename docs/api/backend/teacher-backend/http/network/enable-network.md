# GET/POST /network/enable

一键允许全部学生端上网（切换到 `normal` 模式）。兼容原 Network_Control 的 HTTP 控制接口。

---

## 基本信息

| 项目 | 值 |
|------|-----|
| 路径 | `/api/network/enable` |
| 方法 | `GET`、`POST` |
| 服务 | `local_app`（8771）、`external_app`（8770） |

---

## 请求参数

无。

---

## 响应示例

```json
{
  "ok": true,
  "action": "enable",
  "message": "已下发『全部允许上网』指令"
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `ok` | boolean | 是否成功 |
| `action` | string | 固定为 `"enable"` |
| `message` | string | 操作结果描述 |

---

## 源码位置

`packages/teacher-backend/app/api/v1/endpoints/network.py`
