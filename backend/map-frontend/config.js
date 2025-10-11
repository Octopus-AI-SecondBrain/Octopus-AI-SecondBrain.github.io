// Local development configuration
const CONFIG = {
  // Always use local backend
  BACKEND_URL: 'http://localhost:8000',
    
  // Local development only
  IS_PRODUCTION: false,
  
  // Feature flags
  FEATURES: {
    DEBUG_LOGGING: true,
    CONNECTION_TESTING: true,
    ENHANCED_3D: true
  }
};

// Export for use in other files
window.SECONDBRAIN_CONFIG = CONFIG;