import { createContext, useState, useEffect, useCallback } from 'react'
import api, { onUnauthorized } from '../utils/api'
import { checkHealth, onHealthChange } from '../utils/healthCheck'
import toast from 'react-hot-toast'

export const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [initialized, setInitialized] = useState(false)

  // Check authentication status and return explicit success/failure
  const checkAuth = useCallback(async () => {
    try {
      setLoading(true)
      const response = await api.get('/auth/me')
      setUser(response.data)
      setIsAuthenticated(true)
      return { success: true, user: response.data }
    } catch (error) {
      // Only log if it's not a 401 (expected when not logged in)
      if (error.response?.status !== 401) {
        console.error('Auth check error:', error)
      }
      setUser(null)
      setIsAuthenticated(false)
      return { success: false, error }
    } finally {
      setLoading(false)
      setInitialized(true)
    }
  }, [])

  useEffect(() => {
    let mounted = true
    
    const performAuthCheck = async () => {
      if (mounted && !initialized) {
        // Check service health first
        const health = await checkHealth()
        if (!health.healthy) {
          console.warn('Service health check failed:', health)
          // Don't block auth check, but log the issue
        }
        
        await checkAuth()
      }
    }
    
    performAuthCheck()
    
    return () => {
      mounted = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Subscribe to 401 events from the API layer
  useEffect(() => {
    const unsubscribe = onUnauthorized((err) => {
      // Clear auth state on any 401
      setUser(null)
      setIsAuthenticated(false)
      // Mark initialized so routing can react without flicker
      setInitialized(true)

      const failedUrl = err?.config?.url || ''
      // Avoid toasting during the initial /auth/me bootstrap or if not yet initialized
      if (initialized && !failedUrl.includes('/auth/me')) {
        toast.error('Session expired. Please log in again.')
      }
    })

    return () => {
      unsubscribe()
    }
  }, [initialized])

  // Subscribe to health status changes
  useEffect(() => {
    const unsubscribe = onHealthChange((health) => {
      // Only show health-related toasts if user is initialized and there's a real issue
      if (!initialized) return
      
      if (!health.healthy && health.status === 'error') {
        // Don't spam with repeated error messages
        if (health.error?.response?.status === 503) {
          console.warn('Service temporarily unavailable:', health)
        } else if (health.error?.message === 'Network Error') {
          console.warn('Network connectivity issue:', health)
        }
      }
    })

    return unsubscribe
  }, [initialized])

  const login = async (username, password) => {
    try {
      setLoading(true)
      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)

      await api.post('/auth/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      // Check auth status after login with retries for cookie propagation
      let authResult = null
      for (let attempt = 1; attempt <= 3; attempt++) {
        await new Promise(resolve => setTimeout(resolve, attempt * 200)) // Progressive delay
        authResult = await checkAuth()
        if (authResult.success) {
          break
        }
      }
      
      if (authResult?.success) {
        toast.success('Welcome back! 🧠')
        return { success: true, user: authResult.user }
      } else {
        toast.success('Login successful! If you experience issues, please refresh the page.')
        return { success: true }
      }
    } catch (error) {
      let message = 'Login failed. Please check your credentials.'

      // Handle different error types
      const data = error?.response?.data
      const status = error?.response?.status

      if (typeof data?.detail === 'string') {
        // Backend provided a clear string message
        message = data.detail
        
        // Differentiate between service issues and credential problems
        if (status === 503) {
          if (message.includes('Database')) {
            message = 'Service is initializing. Please try again in a moment.'
          } else {
            message = 'Service temporarily unavailable. Please try again later.'
          }
        }
      } else if (status === 0 || error?.message === 'Network Error') {
        message = 'Cannot reach server. Please check your connection.'
      } else if (status >= 500) {
        message = 'Server error. Please try again later.'
      } else if (status === 401) {
        message = 'Invalid username or password.'
      }

      toast.error(message)
      return { success: false, error: message }
    } finally {
      setLoading(false)
    }
  }

  const signup = async (username, password, email = null) => {
    try {
      const cleanUsername = (username || '').trim()
      const cleanEmail = email ? (email || '').trim() : null

      // Attempt signup
      await api.post('/auth/signup', { 
        username: cleanUsername, 
        password,
        email: cleanEmail 
      })

      // Auto-login after signup with improved error handling
      const loginResult = await login(cleanUsername, password)
      
      if (loginResult.success) {
        toast.success('Account created successfully! Welcome to SecondBrain! 🧠')
      }
      
      return loginResult
    } catch (error) {
      let message = 'Signup failed. Please try again.'

      // Handle FastAPI validation errors (422) which return an array in data.detail
      const data = error?.response?.data
      const status = error?.response?.status

      if (Array.isArray(data?.detail)) {
        // Collect unique messages for readability
        const msgs = [...new Set(data.detail.map(d => d?.msg).filter(Boolean))]
        if (msgs.length) {
          message = msgs.join('\n')
        }
      } else if (typeof data?.detail === 'string') {
        // Backend provided a clear string message (e.g., username taken, migration needed)
        message = data.detail
        
        // Differentiate between service issues and validation problems
        if (status === 503) {
          if (message.includes('Database')) {
            message = 'Service is initializing. Please try again in a moment.'
          } else {
            message = 'Service temporarily unavailable. Please try again later.'
          }
        } else if (status === 400 && message.includes('already taken')) {
          message = 'Username is already taken. Please choose a different one.'
        } else if (status === 400 && message.includes('already registered')) {
          message = 'Email is already registered. Please use a different email.'
        }
      } else if (status === 0 || error?.message === 'Network Error') {
        message = 'Cannot reach server. Please check your connection.'
      } else if (status >= 500) {
        message = 'Server error. Please try again later.'
      }

      toast.error(message)
      return { success: false, error: message }
    }
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
      setUser(null)
      setIsAuthenticated(false)
      toast.success('Logged out successfully')
    } catch (error) {
      console.error('Logout error:', error)
      // Clear state anyway
      setUser(null)
      setIsAuthenticated(false)
    }
  }

  const value = {
    user,
    loading,
    isAuthenticated,
    initialized,
    login,
    signup,
    logout,
    checkAuth,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
