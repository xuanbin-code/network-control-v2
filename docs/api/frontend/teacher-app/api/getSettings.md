# getSettings

获取系统设置。

---

## 签名

```ts
export async function getSettings(): Promise<Record<string, any>>
```

---

## 返回值

`Promise<Record<string, any>>` — 设置键值对。

---

## 对应后端接口

```
GET /api/settings
```

---

## 使用示例

```ts
import { getSettings } from '@/api/teacher'

const settings = await getSettings()
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
