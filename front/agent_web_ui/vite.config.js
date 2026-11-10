import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolveProxyTarget } from './src/apiBase.js'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  loadEnv(mode, process.cwd(), '')
  const target = resolveProxyTarget(process.env.API_PROXY_TARGET)
  const apiProxy = () => ({
    '/api': {
      target,
      changeOrigin: true,
    },
  })
  return {
    plugins: [vue()],
    server: { proxy: apiProxy() },
    preview: { proxy: apiProxy() },
  }
})
