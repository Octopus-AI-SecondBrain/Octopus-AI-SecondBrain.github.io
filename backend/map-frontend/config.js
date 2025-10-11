// Configuration for SecondBrain
// This file is for backend testing only - production uses frontend/assets/js/config.js
const CONFIG = {
  // Backend API URL - Auto-detect environment
  BACKEND_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://octopus-fa0y.onrender.com',
    
  // Environment detection
  IS_PRODUCTION: window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1',
  
  // Feature flags
  FEATURES: {
    DEBUG_LOGGING: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1',
    CONNECTION_TESTING: true,
    ENHANCED_3D: true
  }
};

// Export for use in other files
window.SECONDBRAIN_CONFIG = CONFIG;

// Log configuration in development
if (CONFIG.FEATURES.DEBUG_LOGGING) {
  console.log('🔧 SecondBrain Config (Backend Test Files):', {
    backendUrl: CONFIG.BACKEND_URL,
    isProduction: CONFIG.IS_PRODUCTION,
    hostname: window.location.hostname
  });
}