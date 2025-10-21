import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle, AlertTriangle, XCircle, Wifi, WifiOff } from 'lucide-react'
import api from '../utils/api'

export default function HealthIndicator() {
  const [health, setHealth] = useState(null)
  const [showDetails, setShowDetails] = useState(false)
  const [lastChecked, setLastChecked] = useState(null)

  useEffect(() => {
    checkHealth()
    const interval = setInterval(checkHealth, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const checkHealth = async () => {
    try {
      const response = await api.get('/health')
      setHealth(response.data)
      setLastChecked(new Date())
    } catch (error) {
      setHealth({
        status: 'error',
        message: 'Unable to connect to server'
      })
      setLastChecked(new Date())
    }
  }

  if (!health) return null

  const getStatusIcon = (status) => {
    const iconStyle = { width: '16px', height: '16px' }
    switch (status) {
      case 'healthy':
        return <CheckCircle style={{ ...iconStyle, color: 'var(--sb-success)' }} />
      case 'degraded':
        return <AlertTriangle style={{ ...iconStyle, color: 'var(--sb-warning)' }} />
      case 'error':
        return <XCircle style={{ ...iconStyle, color: 'var(--sb-error)' }} />
      default:
        return <WifiOff style={{ ...iconStyle, color: 'var(--sb-text-tertiary)' }} />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
      case 'connected':
      case 'configured':
        return { color: 'var(--sb-success)' }
      case 'degraded':
      case 'not_configured':
        return { color: 'var(--sb-warning)' }
      case 'error':
      case 'disconnected':
        return { color: 'var(--sb-error)' }
      default:
        return { color: 'var(--sb-text-tertiary)' }
    }
  }

  // Only show indicator if there are issues
  const shouldShow = health.status !== 'healthy' || showDetails

  return (
    <AnimatePresence>
      {shouldShow && (
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          className="fixed top-4 right-4 z-50"
        >
          <div 
            className="glass rounded-lg p-3 cursor-pointer"
            style={{ 
              boxShadow: 'var(--sb-shadow-md)',
              border: '1px solid var(--sb-border)'
            }}
            onClick={() => setShowDetails(!showDetails)}
          >
            <div className="flex items-center gap-2">
              {getStatusIcon(health.status)}
              <span 
                className="text-sm font-medium"
                style={{ color: 'var(--sb-text-primary)' }}
              >
                {health.status === 'healthy' ? 'System Healthy' : 'System Issues'}
              </span>
              <Wifi style={{ width: '16px', height: '16px', color: 'var(--sb-text-tertiary)' }} />
            </div>
            
            {showDetails && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-3 pt-3"
                style={{ borderTop: '1px solid var(--sb-divider)' }}
              >
                <div className="space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span style={{ color: 'var(--sb-text-secondary)' }}>Database:</span>
                    <span style={getStatusColor(health.database)}>
                      {health.database}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span style={{ color: 'var(--sb-text-secondary)' }}>Vector Store:</span>
                    <span style={getStatusColor(health.vector_store)}>
                      {health.vector_store}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span style={{ color: 'var(--sb-text-secondary)' }}>AI Features:</span>
                    <span style={getStatusColor(health.openai)}>
                      {health.openai === 'configured' ? 'enabled' : 'disabled'}
                    </span>
                  </div>
                  
                  {health.message && health.status !== 'healthy' && (
                    <div 
                      className="mt-2 p-2 rounded text-xs"
                      style={{ 
                        background: 'var(--sb-bg-tertiary)',
                        color: 'var(--sb-text-secondary)'
                      }}
                    >
                      {health.message}
                    </div>
                  )}
                  
                  <div 
                    className="mt-2 text-xs"
                    style={{ color: 'var(--sb-text-tertiary)' }}
                  >
                    Last checked: {lastChecked?.toLocaleTimeString()}
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}