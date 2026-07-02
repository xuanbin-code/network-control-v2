# sendBlackScreenUnlock

解除黑屏安静测试窗口。

---

## 签名

```ts
export async function sendBlackScreenUnlock(): Promise<boolean>
```

---

## 返回值

`Promise<boolean>` — 是否成功发送解除命令。

---

## 对应后端接口

```
POST /api/test/black_screen_unlock
```

---

## 使用示例

```ts
import { sendBlackScreenUnlock } from '@/api/student'

const ok = await sendBlackScreenUnlock()
```

---

## 源码位置

`packages/student-app/src/renderer/api/student.ts`
