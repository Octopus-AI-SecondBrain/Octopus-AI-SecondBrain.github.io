import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
          // eslint-disable-next-line no-console
          console.error('onUnauthorized listener error:', e)
        }
      })
    }
    return Promise.reject(error)
  }
)

export default api
