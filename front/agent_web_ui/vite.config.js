import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const proxyTarget = env.VITE_DEV_PROXY_TARGET || 'http://127.0.0.1:8000'
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
