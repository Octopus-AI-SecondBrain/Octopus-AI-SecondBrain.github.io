import axios from 'axios'

// Get API URL from environment variable  
// VITE_API_URL MUST be set to avoid configuration errors
const getApiUrl = () => {
  const viteApiUrl = import.meta.env.VITE_API_URL
  const isDevelopment = import.meta.env.DEV
  
  // Always require VITE_API_URL to be explicitly set
  if (!viteApiUrl) {
    const errorMsg = isDevelopment 
      ? 'VITE_API_URL must be set. Add VITE_API_URL=http://localhost:8001 to your .env.local file'
      : 'VITE_API_URL must be set in production to avoid mixed content errors'
    
    console.error(`CRITICAL: ${errorMsg}`)
    
    // In development, show a helpful error. In production, fail fast.
    if (isDevelopment) {
      throw new Error(`Missing VITE_API_URL environment variable.\n\n${errorMsg}`)
    } else {
      // Fail fast in production - don't allow invalid URLs
      throw new Error(`Production build requires VITE_API_URL to be set to the backend URL`)
    }
  }
  
  // Validate URL format
  try {
    new URL(viteApiUrl)
  } catch (e) {
    throw new Error(`Invalid VITE_API_URL format: ${viteApiUrl}. Must be a valid URL (e.g., https://api.example.com)`)
  }
  
  return viteApiUrl
}

const API_URL = getApiUrl()

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Important for cookie-based auth
  headers: {
    'Content-Type': 'application/json',
  },
})

// Lightweight pub/sub for 401 Unauthorized events
const unauthorizedListeners = new Set()

// Subscribe to 401 events. Returns an unsubscribe function.
export const onUnauthorized = (listener) => {
  if (typeof listener !== 'function') return () => {}
  unauthorizedListeners.add(listener)
  return () => unauthorizedListeners.delete(listener)
}

// Request interceptor
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Notify subscribers about unauthorized errors instead of hard reloading
      unauthorizedListeners.forEach(listener => {
        try {
          listener(error)
        } catch (e) {
          console.error('onUnauthorized listener error:', e)
        }
      })
    }
    return Promise.reject(error)
  }
)

export default api
