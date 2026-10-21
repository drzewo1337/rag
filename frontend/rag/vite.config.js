import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
import { defineConfig } from 'vite'

const askServiceUrl = process.env.ASK_SERVICE_URL
const factsServiceUrl = process.env.FACTS_SERVICE_URL

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    babel({ presets: [reactCompilerPreset()] })
  ],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api/ask': {
        target: askServiceUrl,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/ask/, ''),
      },
      '/api/facts': {
        target: factsServiceUrl,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/facts/, ''),
      },
    },
  },
  preview: {
    host: true,
    port: 4173,
  },
})
