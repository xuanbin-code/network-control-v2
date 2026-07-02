# 前端接口文档

本目录收录教师端和学生端前端对本地后端的 API 封装函数。

---

## 目录

- [`teacher-app/api/`](teacher-app/api/)：教师端 Electron + Vue3 前端 API
  - 源文件：`packages/teacher-app/src/renderer/api/teacher.ts`
  - 基地址：`http://127.0.0.1:8771/api`
- [`student-app/api/`](student-app/api/)：学生端 Electron + Vue3 前端 API
  - 源文件：`packages/student-app/src/renderer/api/student.ts`
  - 基地址：`http://127.0.0.1:8772/api`

---

## 通用说明

- 所有函数均返回 `Promise`，内部使用 `axios` 发送 HTTP 请求。
- 超时时间：教师端 10 秒，学生端 5 秒（模式切换接口放宽到 30 秒）。
- 函数通常在 Pinia Store 中被调用，Vue 组件通过 Store 与后端交互。
