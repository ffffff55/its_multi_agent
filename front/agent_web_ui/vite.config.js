import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolveProxyTarget } from './proxyTarget.js'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'API_PROXY_TARGET')
  const proxyTarget = resolveProxyTarget(env.API_PROXY_TARGET)
  const proxy = {
    '/api': {
      target: proxyTarget,
      changeOrigin: true,
    },
  }
  return {
    plugins: [vue()],
    server: { proxy },
    preview: { proxy },
  }
})
