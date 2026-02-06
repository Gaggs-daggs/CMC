import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import compression from 'vite-plugin-compression'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    compression({
      algorithm: 'gzip',
      ext: '.gz',
      filter: /\.(js|css|html|glb|json)$/i,
    })
  ],
  server: {
    headers: {
      'Cache-Control': 'public, max-age=31536000',
    }
  },
  build: {
    chunkSizeWarningLimit: 2000,
  },
  assetsInclude: ['**/*.glb'],
})
