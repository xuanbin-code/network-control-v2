# enableNetwork

一键允许全部学生端上网。

---

## 签名

```ts
export async function enableNetwork()
```

---

## 返回值

`Promise<AxiosResponse>`

---

## 对应后端接口

```
GET /api/network/enable
```

---

## 使用示例

```ts
import { enableNetwork } from '@/api/teacher'

await enableNetwork()
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
