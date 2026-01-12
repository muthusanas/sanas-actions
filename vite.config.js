import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/sanas-actions/',
  build: {
    outDir: 'docs',
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})
