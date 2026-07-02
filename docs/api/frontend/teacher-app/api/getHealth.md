# getHealth

健康检查。

---

## 签名

```ts
export async function getHealth()
```

---

## 返回值

`Promise<AxiosResponse>`

---

## 对应后端接口

```
GET /api/health
```

---

## 使用示例

```ts
import { getHealth } from '@/api/teacher'

const res = await getHealth()
console.log(res.data) // { status: "ok" }
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
