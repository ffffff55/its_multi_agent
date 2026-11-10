export function resolveApiUrl(path, baseUrl) {
  const suffix = path.startsWith('/') ? path : `/${path}`
  const base = String(baseUrl ?? '').trim().replace(/\/+$/, '')
  if (!base) {
    return suffix
  }
  return `${base}${suffix}`
}

export function apiUrl(path) {
  const configured = import.meta.env && import.meta.env.VITE_API_BASE_URL
  return resolveApiUrl(path, configured)
}
