# updateConfig

部分更新学生端配置。

---

## 签名

```ts
export async function updateConfig(data: Record<string, any>)
```

---

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `data` | Record<string, any> | 是 | 需要修改的配置项 |

---

## 返回值

`Promise<AxiosResponse>`

---

## 对应后端接口

```
POST /api/config
```

---

## 使用示例

```ts
import { updateConfig } from '@/api/student'

await updateConfig({ controller_url: 'ws://192.168.1.200:8765/ws' })
```

---

## 源码位置

`packages/student-app/src/renderer/api/student.ts`
