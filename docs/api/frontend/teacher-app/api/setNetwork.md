# setNetwork

设置指定学生端或全部学生端的网络模式。

---

## 签名

```ts
export async function setNetwork(mode: string, targets?: string[])
```

---

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mode` | string | 是 | 目标模式：`normal` / `whitelist` / `blacklist` / `disconnect` |
| `targets` | string[] | 否 | 目标学生端 IP 列表，不传表示全部 |

---

## 返回值

`Promise<AxiosResponse>`

---

## 对应后端接口

```
POST /api/network/set
```

---

## 使用示例

```ts
import { setNetwork } from '@/api/teacher'

await setNetwork('whitelist', ['192.168.1.101'])
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
