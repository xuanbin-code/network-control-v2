# getMachines

获取学生机列表。

---

## 签名

```ts
export async function getMachines(): Promise<any[]>
```

---

## 返回值

`Promise<any[]>` — 学生机记录数组。

---

## 对应后端接口

```
GET /api/machines
```

---

## 使用示例

```ts
import { getMachines } from '@/api/teacher'

const machines = await getMachines()
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
