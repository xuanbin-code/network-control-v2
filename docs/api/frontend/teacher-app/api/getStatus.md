# getStatus

获取学生机状态汇总。

---

## 签名

```ts
export async function getStatus(): Promise<any>
```

---

## 返回值

`Promise<any>` — 包含 `ok` 和 `agents` 的响应数据。

---

## 对应后端接口

```
GET /api/status
```

---

## 使用示例

```ts
import { getStatus } from '@/api/teacher'

const data = await getStatus()
console.log(data.agents)
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
