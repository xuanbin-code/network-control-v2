# deleteRule

删除一条白名单或黑名单规则。

---

## 签名

```ts
export async function deleteRule(listType: string, ruleId: number)
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
DELETE /api/rules/{list_type}/{rule_id}
```

---

## 使用示例

```ts
import { deleteRule } from '@/api/teacher'

await deleteRule('whitelist', 1)
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
