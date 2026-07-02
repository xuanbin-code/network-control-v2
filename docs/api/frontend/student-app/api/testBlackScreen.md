# testBlackScreen

启动黑屏安静测试窗口。

---

## 签名

```ts
export async function testBlackScreen(countdownSeconds: number): Promise<any>
```

---

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `countdownSeconds` | number | 是 | 倒计时秒数，`0` 表示持续黑屏 |

---

## 返回值

`Promise<any>` — 包含 `ok`、`pid`、`countdown_seconds`、`infinite` 的响应数据。

---

## 对应后端接口

```
POST /api/test/black_screen
```

---

## 使用示例

```ts
import { testBlackScreen } from '@/api/student'

const result = await testBlackScreen(30)
```

---

## 源码位置

`packages/student-app/src/renderer/api/student.ts`
