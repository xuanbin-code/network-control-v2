import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  request: (options) => ipcRenderer.invoke('api:request', options),
  showLock: () => ipcRenderer.send('lock:show'),
  hideLock: () => ipcRenderer.send('lock:hide'),
  platform: process.platform,
})
