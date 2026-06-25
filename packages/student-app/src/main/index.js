import { app, BrowserWindow, ipcMain, Tray, Menu } from 'electron'
import path from 'path'
import { spawn } from 'child_process'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

let mainWindow = null
let lockWindow = null
let tray = null
let backendProcess = null

const LOCAL_API_PORT = 8772
const isDev = !app.isPackaged

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 500,
    height: 400,
    show: false,
    title: 'Network Control 学生端设置',
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  if (isDev) {
    mainWindow.loadURL('http://localhost:5174')
  } else {
    mainWindow.loadFile(path.join(__dirname, '../../dist/index.html'))
  }

  mainWindow.on('close', (event) => {
    event.preventDefault()
    mainWindow.hide()
  })
}

function createLockWindow() {
  if (lockWindow) return
  lockWindow = new BrowserWindow({
    fullscreen: true,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    focusable: true,
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  if (isDev) {
    lockWindow.loadURL('http://localhost:5174#/lock')
  } else {
    lockWindow.loadFile(path.join(__dirname, '../../dist/index.html'), { hash: '#/lock' })
  }

  lockWindow.on('closed', () => {
    lockWindow = null
  })
}

function createTray() {
  tray = new Tray(path.join(__dirname, '../../build/icon.png'))
  const contextMenu = Menu.buildFromTemplate([
    { label: '设置', click: () => mainWindow && mainWindow.show() },
    { label: '退出', click: () => app.quit() },
  ])
  tray.setToolTip('Network Control 学生端')
  tray.setContextMenu(contextMenu)
  tray.on('click', () => {
    if (mainWindow) mainWindow.show()
  })
}

function startBackend() {
  if (isDev) {
    console.log('[Main] 开发模式：请手动启动 student-backend')
    return
  }
  const backendExe = path.join(process.resourcesPath, 'student-backend', 'student-backend.exe')
  backendProcess = spawn(backendExe, [], {
    cwd: path.dirname(backendExe),
    stdio: 'ignore',
    windowsHide: true,
  })
  backendProcess.on('error', (err) => console.error('[Main] 后端启动失败:', err))
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

ipcMain.handle('api:request', async (_event, { method, url, data }) => {
  try {
    const fullUrl = `http://127.0.0.1:${LOCAL_API_PORT}${url}`
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

ipcMain.on('lock:show', () => {
  createLockWindow()
})

ipcMain.on('lock:hide', () => {
  if (lockWindow) {
    lockWindow.close()
    lockWindow = null
  }
})

app.whenReady().then(() => {
  startBackend()
  createMainWindow()
  createTray()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createMainWindow()
  })
})

app.on('window-all-closed', () => {
  // 学生端保持托盘运行
})

app.on('before-quit', () => {
  stopBackend()
})
