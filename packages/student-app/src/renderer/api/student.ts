import axios from 'axios'

const BASE = 'http://127.0.0.1:8772/api'

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
  return instance.post('/apply_mode', { mode })
}

export async function reloadConfig() {
  const res = await instance.post('/reload_config')
  return res.data
}
