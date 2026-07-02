# toggleRule

启用或禁用一条规则。

---

## 签名

```ts
export async function toggleRule(listType: string, ruleId: number)
```

---

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `listType` | string | 是 | 规则类型：`whitelist` 或 `blacklist` |
| `ruleId` | number | 是 | 规则 ID |

---

## 返回值

`Promise<AxiosResponse>`

---

## 对应后端接口

```
POST /api/rules/{list_type}/{rule_id}/toggle
```

---

## 使用示例

```ts
import { toggleRule } from '@/api/teacher'

await toggleRule('whitelist', 1)
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
