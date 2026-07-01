const { app, BrowserWindow, Menu } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const http = require('http')

let mainWindow
let backendProcess

const LOCAL_API_PORT = 8772
const HEALTH_PATH = '/api/health'

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

function checkBackendReady(port, timeoutMs = 30000) {
  return new Promise((resolve, reject) => {
    const start = Date.now()
    const tryConnect = () => {
      const req = http.get(
        `http://127.0.0.1:${port}${HEALTH_PATH}`,
        { timeout: 2000 },
        (res) => {
          if (res.statusCode === 200) {
            resolve(true)
          } else {
            retry()
          }
        }
      )
      req.on('error', retry)
      req.on('timeout', () => {
        req.destroy()
        retry()
      })
    }
    const retry = () => {
      if (Date.now() - start > timeoutMs) {
        reject(new Error(`后端在 ${timeoutMs}ms 内未就绪`))
        return
      }
      setTimeout(tryConnect, 500)
    }
    tryConnect()
  })
}

async function startBackend() {
  const isDev = !!process.env.VITE_DEV_SERVER_URL

  // 开发模式下若 8772 已有后端运行（例如已手动以管理员启动），则直接复用
  if (isDev) {
    try {
      await checkBackendReady(LOCAL_API_PORT, 3000)
      console.log(`[Dev] 检测到已有学生端后端: http://127.0.0.1:${LOCAL_API_PORT}，跳过启动`)
      return
    } catch (err) {
      // 没有已有后端，继续启动
    }

    const backendDir = path.join(__dirname, '../../../student-backend')
    console.log(`[Dev] 启动学生端后端: python -m app.main (cwd: ${backendDir})`)
    backendProcess = spawn('python', ['-m', 'app.main'], {
      cwd: backendDir,
      detached: false,
      stdio: 'pipe',
    })
    backendProcess.stdout.on('data', (data) => {
      console.log(`[student-backend] ${data.toString().trim()}`)
    })
    backendProcess.stderr.on('data', (data) => {
      console.error(`[student-backend] ${data.toString().trim()}`)
    })
    backendProcess.on('error', (err) => {
      console.error('学生端后端启动失败:', err)
    })
    backendProcess.on('exit', (code) => {
      console.log(`学生端后端退出，代码: ${code}`)
      backendProcess = null
    })
    return
  }

  const backendPath = path.join(process.resourcesPath, 'student-backend', 'student-backend.exe')
  backendProcess = spawn(backendPath, [], { detached: false })
  backendProcess.on('error', (err) => {
    console.error('学生端后端启动失败:', err)
  })
}

app.whenReady().then(async () => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })

  startBackend()

  if (backendProcess) {
    try {
      await checkBackendReady(LOCAL_API_PORT)
      console.log(`[Dev] 学生端后端已就绪: http://127.0.0.1:${LOCAL_API_PORT}`)
    } catch (err) {
      console.error('[Dev] 等待后端就绪失败:', err.message)
    }
  }
})

app.on('window-all-closed', () => {
  if (backendProcess) {
    backendProcess.kill()
  }
  if (process.platform !== 'darwin') app.quit()
})
