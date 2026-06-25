import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'path'
import { spawn } from 'child_process'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

let mainWindow = null
let backendProcess = null

const BACKEND_PORT = 8771
const isDev = !app.isPackaged

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1000,
    minHeight: 600,
    title: 'Network Control 教师端',
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

function startBackend() {
  if (isDev) {
    // 开发模式：假设用户在另一个终端启动了 python -m app.main
    console.log('[Main] 开发模式：请手动启动 teacher-backend')
    return
  }

  const backendExe = path.join(process.resourcesPath, 'teacher-backend', 'teacher-backend.exe')
  console.log('[Main] 启动后端:', backendExe)

  backendProcess = spawn(backendExe, [], {
    cwd: path.dirname(backendExe),
    stdio: 'ignore',
    windowsHide: true,
  })

  backendProcess.on('error', (err) => {
    console.error('[Main] 后端启动失败:', err)
  })

  backendProcess.on('exit', (code) => {
    console.log('[Main] 后端退出:', code)
    backendProcess = null
  })
}

function stopBackend() {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill()
  }
}

// IPC 通信：转发 HTTP 请求到本地后端
ipcMain.handle('api:request', async (_event, { method, url, data }) => {
  try {
    const fullUrl = `http://127.0.0.1:${BACKEND_PORT}${url}`
    const res = await fetch(fullUrl, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: data ? JSON.stringify(data) : undefined,
    })
    return { ok: res.ok, status: res.status, data: await res.json() }
  } catch (err) {
    return { ok: false, error: err.message }
  }
})

app.whenReady().then(() => {
  startBackend()
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  stopBackend()
  if (process.platform !== 'darwin') app.quit()
})

app.on('will-quit', () => {
  stopBackend()
})
