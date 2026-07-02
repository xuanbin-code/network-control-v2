# applyMode

本地强制切换网络模式。

---

## 签名

```ts
export async function applyMode(mode: string)
```

---

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mode` | string | 是 | 目标模式：`normal` / `whitelist` / `blacklist` / `disconnect` |

---

## 返回值

`Promise<AxiosResponse>`

---

## 对应后端接口

```
POST /api/apply_mode
```

---

## 使用示例

```ts
import { applyMode } from '@/api/student'

await applyMode('whitelist')
```

---

## 源码位置

`packages/student-app/src/renderer/api/student.ts`
