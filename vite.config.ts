import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './', // Use relative paths so it works both locally and on GitHub Pages
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
