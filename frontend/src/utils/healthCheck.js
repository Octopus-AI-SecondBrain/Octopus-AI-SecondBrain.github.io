import api from './api'

/**
 * Health check utility for detecting service status
 */
export class HealthChecker {
  constructor() {
    this.lastCheck = null
    this.status = 'unknown'
    this.listeners = new Set()
  }

  /**
   * Subscribe to health status changes
   * @param {Function} listener - Callback function that receives {status, error, data}
   * @returns {Function} Unsubscribe function
   */
  onStatusChange(listener) {
    if (typeof listener !== 'function') return () => {}
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }

  /**
   * Notify all listeners of status change
   * @param {Object} statusData - Status information
   */
  notifyListeners(statusData) {
    this.listeners.forEach(listener => {
      try {
        listener(statusData)
      } catch (e) {
        console.error('Health check listener error:', e)
      }
    })
  }

  /**
   * Perform health check
   * @returns {Promise<Object>} Health status
   */
  async checkHealth() {
    try {
      const response = await api.get('/health', { timeout: 10000 })
      const data = response.data
      
      this.status = data.status || 'healthy'
      this.lastCheck = new Date()

      const statusData = {
        status: this.status,
        healthy: this.status === 'healthy',
        data: data,
        timestamp: this.lastCheck
      }

      // Notify listeners if status changed or if there are issues
      if (this.status !== 'healthy' || data.database !== 'connected') {
        this.notifyListeners(statusData)
      }

      return statusData
    } catch (error) {
      const statusData = {
        status: 'error',
        healthy: false,
        error: error,
        timestamp: new Date()
      }

      this.status = 'error'
      this.lastCheck = new Date()
      this.notifyListeners(statusData)

      return statusData
    }
  }

  /**
   * Check if service needs database migration
   * @param {Object} healthData - Health check response
   * @returns {boolean} True if migration is needed
   */
  needsMigration(healthData) {
    return (
      healthData?.data?.database === 'schema_missing' ||
      healthData?.status === 'degraded' ||
      (healthData?.error?.response?.status === 503 &&
       healthData?.error?.response?.data?.detail?.includes('Database'))
    )
  }

  /**
   * Get user-friendly error message
   * @param {Object} healthData - Health check response
   * @returns {string} User-friendly message
   */
  getStatusMessage(healthData) {
    if (healthData.healthy) {
      return 'Service is running normally'
    }

    if (this.needsMigration(healthData)) {
      return 'Service is starting up. Database initialization in progress...'
    }

    if (healthData.error) {
      const status = healthData.error.response?.status
      if (status === 0 || healthData.error.message === 'Network Error') {
        return 'Cannot connect to server. Please check if the backend is running.'
      }
      if (status >= 500) {
        return 'Server error. Please try again later.'
      }
    }

    return 'Service temporarily unavailable'
  }

  /**
   * Get developer-friendly error message
   * @param {Object} healthData - Health check response
   * @returns {string} Developer message
   */
  getDeveloperMessage(healthData) {
    if (healthData.healthy) return null

    if (this.needsMigration(healthData)) {
      return 'Run `alembic upgrade head` in the backend directory to initialize the database schema.'
    }

    if (healthData.error) {
      const status = healthData.error.response?.status
      if (status === 0 || healthData.error.message === 'Network Error') {
        return 'Start the backend server with `cd backend && source venv/bin/activate && uvicorn backend.main:app --reload`'
      }
      if (status >= 500) {
        return 'Check server logs for detailed error information.'
      }
    }

    return 'Check backend logs and configuration.'
  }
}

// Global instance
export const healthChecker = new HealthChecker()

// Convenience functions
export const checkHealth = () => healthChecker.checkHealth()
export const onHealthChange = (listener) => healthChecker.onStatusChange(listener)