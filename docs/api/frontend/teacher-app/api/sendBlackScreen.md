# sendBlackScreen

向指定学生端（或全部学生端）发送黑屏安静测试指令。

---

## 签名

```ts
export async function sendBlackScreen(countdownSeconds: number = 30, targets?: string[])
```

---

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `countdownSeconds` | number | 否 | 30 | 倒计时秒数；`0` 表示持续黑屏 |
| `targets` | string[] | 否 | — | 目标学生端 IP 列表，不传表示全部 |

---

## 返回值

`Promise<AxiosResponse>`

---

## 对应后端接口

```
POST /api/test/black_screen
```

---

## 使用示例

```ts
import { sendBlackScreen } from '@/api/teacher'

await sendBlackScreen(30, ['192.168.1.101'])
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
