const { app, BrowserWindow, Menu } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

let mainWindow
let backendProcess

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
      devTools: true,
    },
  })

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../../dist/index.html'))
  }

  setupWindowMenu(mainWindow)
}

function setupWindowMenu(win) {
  const template = [
    {
      label: '视图',
      submenu: [
        {
          label: '重新加载',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            win.webContents.reload()
          },
        },
        {
          label: '切换开发者工具',
          accelerator: 'F12',
          click: () => {
            win.webContents.toggleDevTools()
          },
        },
        { type: 'separator' },
        {
          label: '实际大小',
          role: 'resetZoom',
        },
        {
          label: '放大',
          role: 'zoomIn',
        },
        {
          label: '缩小',
          role: 'zoomOut',
        },
        { type: 'separator' },
        {
          label: '全屏',
          role: 'togglefullscreen',
        },
      ],
    },
    {
      label: '窗口',
      submenu: [
        {
          label: '最小化',
          role: 'minimize',
        },
        {
          label: '关闭',
          role: 'close',
        },
      ],
    },
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

function startBackend() {
  const isDev = !!process.env.VITE_DEV_SERVER_URL
  if (isDev) {
    return
  }
  const backendPath = path.join(process.resourcesPath, 'student-backend', 'student-backend.exe')
  backendProcess = spawn(backendPath, [], { detached: false })
  backendProcess.on('error', (err) => {
    console.error('学生端后端启动失败:', err)
  })
}

app.whenReady().then(() => {
  startBackend()
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (backendProcess) {
    backendProcess.kill()
  }
  if (process.platform !== 'darwin') app.quit()
})
