# addRule

添加一条白名单或黑名单规则。

---

## 签名

```ts
export async function addRule(listType: string, domain: string)
```

---

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `listType` | string | 是 | 规则类型：`whitelist` 或 `blacklist` |
| `domain` | string | 是 | 域名 |

---

## 返回值

`Promise<AxiosResponse>`

---

## 对应后端接口

```
POST /api/rules/{list_type}
```

---

## 使用示例

```ts
import { addRule } from '@/api/teacher'

await addRule('whitelist', 'www.baidu.com')
```

---

## 源码位置

`packages/teacher-app/src/renderer/api/teacher.ts`
