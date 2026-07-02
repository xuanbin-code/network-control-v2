import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import electron from 'vite-plugin-electron'
import renderer from 'vite-plugin-electron-renderer'
import { resolve } from 'path'

// 外部环境中若设置了 ELECTRON_RUN_AS_NODE，Electron 会以 Node 模式启动，必须删除该变量
delete process.env.ELECTRON_RUN_AS_NODE

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const devPort = parseInt(env.VITE_DEV_PORT || '5174', 10)

  return {
    server: {
      port: devPort,
      strictPort: true,
      hmr: {
        protocol: 'ws',
        host: 'localhost',
      },
      watch: {
        // Windows 上部分文件系统需要轮询才能检测到变更
        usePolling: true,
        interval: 500,
      },
    },
    plugins: [
      vue(),
      electron([
        {
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
  }
})
