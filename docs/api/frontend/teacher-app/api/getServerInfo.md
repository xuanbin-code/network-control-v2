# getServerInfo

获取教师端 IP 和 WebSocket 地址。

---

## 签名

```ts
export async function getServerInfo(): Promise<any>
```

---

## 返回值

`Promise<any>` — 包含 `ip`、`ws_url`、`ws_port` 的响应数据。

---

## 对应后端接口

```
GET /api/server_info
```

---

## 使用示例

```ts
import { getServerInfo } from '@/api/teacher'

const { ip, ws_url } = await getServerInfo()
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
