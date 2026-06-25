const request = async (method, url, data = null) => {
  if (window.electronAPI) {
    return window.electronAPI.request({ method, url, data })
  }
  const res = await fetch(`http://127.0.0.1:8772${url}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: data ? JSON.stringify(data) : undefined,
  })
  return { ok: res.ok, status: res.status, data: await res.json() }
}

export const api = {
  getStatus: () => request('GET', '/api/status'),
  getConfig: () => request('GET', '/api/config'),
  updateConfig: (data) => request('POST', '/api/config', data),
}
