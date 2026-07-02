# sendTestMessage

向指定学生端（或全部学生端）发送测试消息。

---

## 签名

```ts
export async function sendTestMessage(message: string, targets?: string[])
```

---

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message` | string | 是 | 消息内容 |
| `targets` | string[] | 否 | 目标学生端 IP 列表，不传表示全部 |

---

## 返回值

`Promise<AxiosResponse>`

---

## 对应后端接口

```
POST /api/test/send
```

---

## 使用示例

```ts
import { sendTestMessage } from '@/api/teacher'

await sendTestMessage('测试消息', ['192.168.1.101'])
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
