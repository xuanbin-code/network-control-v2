# getStatus

获取学生端当前运行状态。

---

## 签名

```ts
export async function getStatus(): Promise<any>
```

---

## 返回值

`Promise<any>` — 学生端状态数据。

---

## 对应后端接口

```
GET /api/status
```

---

## 使用示例

```ts
import { getStatus } from '@/api/student'

const status = await getStatus()
```

---

## 源码位置

`packages/student-app/src/renderer/api/student.ts`
