# getRules

获取黑白名单规则列表。

---

## 签名

```ts
export async function getRules(): Promise<any>
```

---

## 返回值

`Promise<any>` — 包含 `whitelist` 和 `blacklist` 数组的响应数据。

---

## 对应后端接口

```
GET /api/rules
```

---

## 使用示例

```ts
import { getRules } from '@/api/teacher'

const { whitelist, blacklist } = await getRules()
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
