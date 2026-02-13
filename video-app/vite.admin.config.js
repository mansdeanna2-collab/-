import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import fs from 'fs'

// Admin-specific Vite configuration
// This builds the admin app separately from the main web/h5 app
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiBaseUrl = env.VITE_API_BASE_URL || 'http://103.74.193.179:5000'
  
  return {
    plugins: [
      vue(),
      // Custom plugin to serve admin.html as the entry point
      {
        name: 'admin-html-serve',
        configureServer(server) {
          // Add middleware BEFORE vite's internal middleware
          server.middlewares.use((req, res, next) => {
            // Check if this is an HTML page request (not a JS/CSS/asset request)
            const isHtmlRequest = req.headers.accept?.includes('text/html')
            const isAssetRequest = /\.(js|ts|vue|css|json|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)(\?.*)?$/.test(req.url || '')
            const isViteClient = (req.url || '').startsWith('/@') || (req.url || '').startsWith('/__')
            
            // Only intercept HTML navigation requests
            if (isHtmlRequest && !isAssetRequest && !isViteClient) {
              const adminHtml = fs.readFileSync(resolve(__dirname, 'admin.html'), 'utf-8')
              server.transformIndexHtml(req.url || '/', adminHtml).then((html) => {
                res.statusCode = 200
                res.setHeader('Content-Type', 'text/html; charset=utf-8')
                res.end(html)
              }).catch((err) => {
                console.error('Error transforming admin.html:', err)
                next(err)
              })
              return
            }
            next()
          })
        }
      }
    ],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },
    server: {
      host: '0.0.0.0',
      port: 8897,
      proxy: {
        '/api': {
          target: apiBaseUrl,
          changeOrigin: true
        }
      }
    },
    build: {
      outDir: 'dist-admin',
      assetsDir: 'assets',
      sourcemap: false,
      minify: 'esbuild',
      rollupOptions: {
        input: {
          main: resolve(__dirname, 'admin.html')
        },
        output: {
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
        }
      }
    }
  }
})
