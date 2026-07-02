# scanNetwork

扫描指定网段内的在线 IP。

---

## 签名

```ts
export async function scanNetwork(subnet: string): Promise<any>
```

---

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `subnet` | string | 是 | 网段，如 `192.168.1.0/24` |

---

## 返回值

`Promise<any>` — 扫描结果，包含 `subnet` 和 `ips`。

---

## 对应后端接口

```
GET /api/scan?subnet={subnet}
```

---

## 使用示例

```ts
import { scanNetwork } from '@/api/teacher'

const result = await scanNetwork('192.168.1.0/24')
console.log(result.ips)
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
