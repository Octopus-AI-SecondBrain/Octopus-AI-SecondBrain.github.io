// Configuration for SecondBrain
// For GitHub Pages deployment, update BACKEND_URL to your backend host
const CONFIG = {
  // Backend API URL - Update this for production deployment
  // For local dev: 'http://localhost:8000'
  // For production: 'https://your-backend-host.onrender.com' or your backend URL
  BACKEND_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://your-backend-host.onrender.com', // CHANGE THIS to your actual backend URL
    
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
  console.log('🔧 SecondBrain Config:', {
    backendUrl: CONFIG.BACKEND_URL,
    isProduction: CONFIG.IS_PRODUCTION,
    hostname: window.location.hostname
  });
}