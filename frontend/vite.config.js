import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'
import process from 'node:process'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  // Load environment variables
  const env = loadEnv(mode, process.cwd(), '')
  
  // Determine base path for GitHub Pages
  // Use environment variable VITE_REPO_NAME if set, otherwise derive from git remote
  const getBasePath = () => {
    if (mode === 'production') {
      // For GitHub Pages, use the repository name as base path
      // Can be overridden with VITE_BASE_PATH environment variable
      return env.VITE_BASE_PATH || '/secondbrain/'
    }
    return '/'
  }

  // Validate required environment variables for production
  if (command === 'build' && mode === 'production') {
    if (!env.VITE_API_URL) {
      console.error('ERROR: VITE_API_URL must be set for production builds')
      console.error('Example: VITE_API_URL=https://your-backend.onrender.com')
      process.exit(1)
    }
    
    console.log(`Building for production with:`)
    console.log(`  API URL: ${env.VITE_API_URL}`)
    console.log(`  Base path: ${getBasePath()}`)
  }

  return {
    plugins: [react()],
    base: getBasePath(),
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: true,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom', 'react-router-dom'],
            three: ['three', 'react-force-graph'],
            animation: ['framer-motion'],
          },
        },
      },
    },
    // Define additional environment variables
    define: {
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
      __MODE__: JSON.stringify(mode),
    },
  }
})
