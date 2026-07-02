# disableNetwork

一键禁止全部学生端上网。

---

## 签名

```ts
export async function disableNetwork()
```

---

## 返回值

`Promise<AxiosResponse>`

---

## 对应后端接口

```
GET /api/network/disable
```

---

## 使用示例

```ts
import { disableNetwork } from '@/api/teacher'

await disableNetwork()
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
