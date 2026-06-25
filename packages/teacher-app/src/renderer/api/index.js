const request = async (method, url, data = null) => {
  if (window.electronAPI) {
    return window.electronAPI.request({ method, url, data })
  }
  // 浏览器开发回退
  const res = await fetch(`http://127.0.0.1:8771${url}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: data ? JSON.stringify(data) : undefined,
  })
  return { ok: res.ok, status: res.status, data: await res.json() }
}

export const api = {
  getMachines: () => request('GET', '/api/machines'),
  setNetwork: (mode, targets = []) => request('POST', '/api/network/set', { mode, targets }),
  getRules: () => request('GET', '/api/rules'),
  addRule: (listType, domain) => request('POST', `/api/rules/${listType}`, { domain }),
  deleteRule: (listType, id) => request('DELETE', `/api/rules/${listType}/${id}`),
  getSettings: () => request('GET', '/api/settings'),
  updateSetting: (key, value) => request('POST', '/api/settings', { key, value }),
  getBrowsing: (ip) => request('GET', `/api/browsing/${ip}`),
}
