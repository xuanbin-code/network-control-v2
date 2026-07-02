# getConfig

获取学生端完整配置。

---

## 签名

```ts
export async function getConfig(): Promise<any>
```

---

## 返回值

`Promise<any>` — `config.json` 完整内容。

---

## 对应后端接口

```
GET /api/config
```

---

## 使用示例

```ts
import { getConfig } from '@/api/student'

const config = await getConfig()
```

---

## 源码位置

`packages/student-app/src/renderer/api/student.ts`
