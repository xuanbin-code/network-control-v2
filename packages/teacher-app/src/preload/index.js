import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  // HTTP API 请求转发
  request: (options) => ipcRenderer.invoke('api:request', options),

  // 平台信息
  platform: process.platform,
})
