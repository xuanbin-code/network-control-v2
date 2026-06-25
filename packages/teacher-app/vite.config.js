import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import electron from 'vite-plugin-electron'
import renderer from 'vite-plugin-electron-renderer'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    electron([
      {
        // Main process entry
        entry: 'src/main/index.js',
        onstart(options) {
          if (options.startup) {
            options.startup()
          }
        },
        vite: {
          build: {
            sourcemap: true,
            minify: process.env.NODE_ENV === 'production',
            outDir: 'dist-electron/main',
            rollupOptions: {
              external: ['electron'],
            },
          },
        },
      },
      {
        // Preload scripts entry
        entry: 'src/preload/index.js',
        onstart(options) {
          options.reload()
        },
        vite: {
          build: {
            sourcemap: 'inline',
            minify: process.env.NODE_ENV === 'production',
            outDir: 'dist-electron/preload',
            rollupOptions: {
              external: ['electron'],
            },
          },
        },
      },
    ]),
    renderer(),
  ],
  root: '.',
  base: './',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        index: resolve(__dirname, 'index.html'),
      },
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src/renderer'),
    },
  },
})
