// Authentication page JavaScript
const state = {
  backend: localStorage.getItem('sb_backend') || (window.SECONDBRAIN_CONFIG ? window.SECONDBRAIN_CONFIG.BACKEND_URL : 'http://localhost:8000'),
  isLogin: true
};

const els = {
  loginForm: document.getElementById('loginForm'),
  registerForm: document.getElementById('registerForm'),
  loginUsername: document.getElementById('loginUsername'),
  loginPassword: document.getElementById('loginPassword'),
  registerUsername: document.getElementById('registerUsername'),
  registerPassword: document.getElementById('registerPassword'),
  confirmPassword: document.getElementById('confirmPassword'),
  showRegister: document.getElementById('showRegister'),
  showLogin: document.getElementById('showLogin'),
  backendUrl: document.getElementById('backendUrl'),
  saveBackend: document.getElementById('saveBackend')
};

// Initialize
els.backendUrl.value = state.backend;

// Form switching
els.showRegister.addEventListener('click', (e) => {
  e.preventDefault();
  els.loginForm.classList.add('hidden');
  els.registerForm.classList.remove('hidden');
  state.isLogin = false;
});

els.showLogin.addEventListener('click', (e) => {
  e.preventDefault();
  els.registerForm.classList.add('hidden');
  els.loginForm.classList.remove('hidden');
  state.isLogin = true;
});

// Backend configuration
els.saveBackend.addEventListener('click', () => {
  state.backend = els.backendUrl.value.trim() || 'http://127.0.0.1:8000';
  localStorage.setItem('sb_backend', state.backend);
  showToast('Backend URL saved!', 'success');
});

// API helper
async function apiCall(endpoint, options = {}) {
  const url = `${state.backend}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': options.isFormData ? 'application/x-www-form-urlencoded' : 'application/json',
      'Accept': 'application/json'
    },
    credentials: 'include',  // Always include cookies
    ...options
  };
  
  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`${response.status}: ${errorText}`);
    }
    
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    return await response.text();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}

// Login handler
els.loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const username = els.loginUsername.value.trim();
  const password = els.loginPassword.value.trim();
  
  if (!username || !password) {
    showToast('Please fill in all fields', 'error');
    return;
  }
  
  try {
    showLoading(els.loginForm.querySelector('.btn-primary'), 'Signing in...');
    
    const formData = new URLSearchParams();
    formData.set('username', username);
    formData.set('password', password);
    
    const response = await apiCall('/auth/token', {
      method: 'POST',
      body: formData,
      isFormData: true,
      credentials: 'include'  // Important: Include cookies in request
    });
    
    // Token is now stored in httpOnly cookie - don't store in localStorage
    // Remove any legacy token from localStorage
    localStorage.removeItem('sb_token');
    
    showToast('Login successful! Redirecting...', 'success');
    
    setTimeout(() => {
      window.location.href = './index.html';
    }, 1500);
    
  } catch (error) {
    showToast('Login failed: ' + error.message, 'error');
  } finally {
    hideLoading(els.loginForm.querySelector('.btn-primary'), 'Sign In');
  }
});

// Register handler
els.registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const username = els.registerUsername.value.trim();
  const password = els.registerPassword.value.trim();
  const confirmPassword = els.confirmPassword.value.trim();
  
  if (!username || !password || !confirmPassword) {
    showToast('Please fill in all fields', 'error');
    return;
  }
  
  if (password !== confirmPassword) {
    showToast('Passwords do not match', 'error');
    return;
  }
  
  if (password.length < 6) {
    showToast('Password must be at least 6 characters', 'error');
    return;
  }
  
  try {
    showLoading(els.registerForm.querySelector('.btn-primary'), 'Creating account...');
    
    await apiCall('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({
        username: username,
        password: password
      })
    });
    
    showToast('Account created! Please sign in.', 'success');
    
    // Switch to login form
    els.registerForm.classList.add('hidden');
    els.loginForm.classList.remove('hidden');
    els.loginUsername.value = username;
    state.isLogin = true;
    
  } catch (error) {
    showToast('Registration failed: ' + error.message, 'error');
  } finally {
    hideLoading(els.registerForm.querySelector('.btn-primary'), 'Create Account');
  }
});

// Utility functions
function showToast(message, type = 'info') {
  // Remove existing toasts
  document.querySelectorAll('.toast').forEach(toast => toast.remove());
  
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  
  // Trigger animation
  setTimeout(() => toast.classList.add('show'), 100);
  
  // Auto remove
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function showLoading(button, text) {
  button.disabled = true;
  button.textContent = text;
  button.style.opacity = '0.7';
}

function hideLoading(button, originalText) {
  button.disabled = false;
  button.textContent = originalText;
  button.style.opacity = '1';
}

// Check if already logged in
window.addEventListener('load', () => {
  // Check if authenticated via cookie by calling /auth/me
  apiCall('/auth/me', {
    credentials: 'include'
  }).then(() => {
    // User is authenticated, redirect to main app
    window.location.href = './index.html';
  }).catch(() => {
    // Not authenticated, stay on login page
    // Also clear any legacy tokens
    localStorage.removeItem('sb_token');
  });
});

// Add some keyboard shortcuts
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && e.ctrlKey) {
    if (state.isLogin) {
      els.loginForm.querySelector('.btn-primary').click();
    } else {
      els.registerForm.querySelector('.btn-primary').click();
    }
  }
});