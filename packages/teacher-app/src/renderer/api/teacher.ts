import axios from 'axios'

const BASE = 'http://127.0.0.1:8771/api'

const instance = axios.create({
  baseURL: BASE,
  timeout: 10000,
})

export async function getHealth() {
  return instance.get('/health')
}

export async function getMachines() {
  const res = await instance.get('/machines')
  return res.data.machines
}

export async function getStatus() {
  const res = await instance.get('/status')
  return res.data
}

export async function setNetwork(mode: string, targets?: string[]) {
  return instance.post('/network/set', { mode, targets })
}

export async function enableNetwork() {
  return instance.get('/network/enable')
}

export async function disableNetwork() {
  return instance.get('/network/disable')
}

export async function enableIp(ip: string) {
  return instance.get('/network/enable_ip', { params: { ip } })
}

export async function disableIp(ip: string) {
  return instance.get('/network/disable_ip', { params: { ip } })
}

export async function getRules() {
  const res = await instance.get('/rules')
  return res.data
}

export async function addRule(listType: string, domain: string) {
  return instance.post(`/rules/${listType}`, { domain })
}

export async function deleteRule(listType: string, ruleId: number) {
  return instance.delete(`/rules/${listType}/${ruleId}`)
}

export async function toggleRule(listType: string, ruleId: number) {
  return instance.post(`/rules/${listType}/${ruleId}/toggle`)
}

export async function getSettings() {
  const res = await instance.get('/settings')
  return res.data
}

export async function updateSetting(key: string, value: string) {
  return instance.post('/settings', { key, value })
}

export async function scanNetwork(subnet: string) {
  const res = await instance.get('/scan', { params: { subnet } })
  return res.data
}

export async function sendTestMessage(message: string, targets?: string[]) {
  return instance.post('/test/send', { message, targets })
}

export async function sendBlackScreen(countdownSeconds: number = 30, targets?: string[]) {
  return instance.post('/test/black_screen', { countdown_seconds: countdownSeconds, targets })
}

export async function sendBlackScreenUnlock(targets?: string[]) {
  return instance.post('/test/black_screen_unlock', { targets })
}

export async function getServerInfo() {
  const res = await instance.get('/server_info')
  return res.data
}
