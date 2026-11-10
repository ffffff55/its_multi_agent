/** 对话页请求主服务时用的地址。不要在页面里写死主机和端口。 */

/**
 * 基地址为空时返回站点相对路径，开发时由 Vite 代理转发，构建后由反向代理转发。
 * 基地址是绝对地址时，浏览器直接请求那台机器。
 */
export function resolveApiUrl(path, baseUrl) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  const base = String(baseUrl ?? '').trim().replace(/\/+$/, '')
  if (!base) return normalizedPath
  return `${base}${normalizedPath}`
}

/** 开发服务器把 /api 转到这里。没配时用本机主服务的默认地址。 */
export function resolveProxyTarget(target) {
  const value = String(target ?? '').trim().replace(/\/+$/, '')
  return value || 'http://127.0.0.1:8000'
}

export function apiUrl(path) {
  return resolveApiUrl(path, import.meta.env?.VITE_API_BASE_URL)
}
