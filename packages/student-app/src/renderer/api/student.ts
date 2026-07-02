import axios from 'axios'

const BASE = import.meta.env.VITE_STUDENT_API_BASE || 'http://127.0.0.1:8772/api'

const instance = axios.create({
  baseURL: BASE,
  timeout: 5000,
})

export async function getStatus() {
  const res = await instance.get('/status')
  return res.data
}

export async function getConfig() {
  const res = await instance.get('/config')
  return res.data
}

export async function updateConfig(data: Record<string, any>) {
  return instance.post('/config', data)
}

export async function applyMode(mode: string) {
  // 模式切换涉及 PowerShell/路由表/DNS 等系统命令，可能耗时数秒，放宽超时
  return instance.post('/apply_mode', { mode }, { timeout: 30000 })
}

export async function reloadConfig() {
  const res = await instance.post('/reload_config')
  return res.data
}

export async function testBlackScreen(countdownSeconds: number) {
  const res = await instance.post('/test/black_screen', {
    countdown_seconds: countdownSeconds,
  })
  return res.data
}

export async function sendBlackScreenUnlock() {
  const res = await instance.post('/test/black_screen_unlock')
  return res.data.ok === true
}
