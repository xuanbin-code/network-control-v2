/**
 * 将 Unix 时间戳（秒）转换为相对时间描述（中文）
 */
export function formatRelativeTime(unixTimestamp: number): string {
  const now = Date.now()
  const diff = now - unixTimestamp * 1000
  const seconds = Math.floor(diff / 1000)

  if (seconds < 0) return '刚刚'
  if (seconds < 60) return '刚刚'

  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}分钟前`

  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`

  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}天前`

  return new Date(unixTimestamp * 1000).toLocaleDateString('zh-CN')
}
