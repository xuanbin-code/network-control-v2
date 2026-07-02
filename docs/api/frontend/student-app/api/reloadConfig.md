# reloadConfig

重新从磁盘加载 `config.json`。

---

## 签名

```ts
export async function reloadConfig(): Promise<any>
```

---

## 返回值

`Promise<any>` — 包含 `ok` 和 `config` 的响应数据。

---

## 对应后端接口

```
POST /api/reload_config
```

---

## 使用示例

```ts
import { reloadConfig } from '@/api/student'

const data = await reloadConfig()
```

---

## 源码位置

`packages/student-app/src/renderer/api/student.ts`
