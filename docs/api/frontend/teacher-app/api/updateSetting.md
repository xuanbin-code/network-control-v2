# updateSetting

更新一项系统设置。

---

## 签名

```ts
export async function updateSetting(key: string, value: string)
```

---

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `key` | string | 是 | 设置项名称 |
| `value` | string | 是 | 设置项值 |

---

## 返回值

`Promise<AxiosResponse>`

---

## 对应后端接口

```
POST /api/settings
```

---

## 使用示例

```ts
import { updateSetting } from '@/api/teacher'

await updateSetting('upstream_dns', '8.8.8.8')
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
