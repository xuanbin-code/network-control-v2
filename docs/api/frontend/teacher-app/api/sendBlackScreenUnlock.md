# sendBlackScreenUnlock

向指定学生端（或全部学生端）发送解除黑屏指令。

---

## 签名

```ts
export async function sendBlackScreenUnlock(targets?: string[])
```

---

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `targets` | string[] | 否 | 目标学生端 IP 列表，不传表示全部 |

---

## 返回值

`Promise<AxiosResponse>`

---

## 对应后端接口

```
POST /api/test/black_screen_unlock
```

---

## 使用示例

```ts
import { sendBlackScreenUnlock } from '@/api/teacher'

await sendBlackScreenUnlock(['192.168.1.101'])
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
