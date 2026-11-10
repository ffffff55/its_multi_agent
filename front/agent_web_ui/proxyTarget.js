/** 只给 Vite 开发服务器和 preview 用。不要放进 src，也不要用 VITE_ 前缀。 */

export function resolveProxyTarget(target) {
  const value = String(target ?? '').trim().replace(/\/+$/, '')
  return value || 'http://127.0.0.1:8000'
}
