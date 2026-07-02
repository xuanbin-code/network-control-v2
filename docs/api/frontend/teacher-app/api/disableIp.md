# disableIp

按 IP 禁止单台学生端上网。

---

## 签名

```ts
export async function disableIp(ip: string)
```

---

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `ip` | string | 是 | 学生端 IP |

---

## 返回值

`Promise<AxiosResponse>`

---

## 对应后端接口

```
GET /api/network/disable_ip?ip={ip}
```

---

## 使用示例

```ts
import { disableIp } from '@/api/teacher'

await disableIp('192.168.1.101')
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
