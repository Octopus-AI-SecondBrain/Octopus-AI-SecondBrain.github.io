// SecondBrain Neural Map Application with 3D Obsidian-like Visualization
const state = {
  backend: localStorage.getItem('sb_backend') || (window.SECONDBRAIN_CONFIG ? window.SECONDBRAIN_CONFIG.BACKEND_URL : 'http://localhost:8000'),
  token: localStorage.getItem('sb_token') || null,
  cy: null,
  is3D: false,
  three: {
    scene: null,
    camera: null,
    renderer: null,
    controls: null,
    nodes: [],
    edges: [],
    raycaster: null,
    mouse: null,
    nodeGeometries: new Map(),
    nodeMaterials: new Map()
  },
  mapData: { nodes: [], edges: [] },
  nodeTypes: {
    note: { color: 0x8b5cf6, size: 1.0, shape: 'sphere' },
    concept: { color: 0x5ee3ff, size: 1.2, shape: 'octahedron' },
    topic: { color: 0xf59e0b, size: 1.4, shape: 'dodecahedron' },
    important: { color: 0xef4444, size: 1.6, shape: 'icosahedron' }
  }
};

// Global error handler and notification system
class NotificationManager {
  constructor() {
    this.container = this.createContainer();
    document.body.appendChild(this.container);
    
    // Handle uncaught errors
    window.addEventListener('error', (event) => {
      console.error('Global error:', event.error);
      this.showError('An unexpected error occurred. Please try again.');
    });
    
    window.addEventListener('unhandledrejection', (event) => {
      console.error('Unhandled promise rejection:', event.reason);
      this.showError('A network or processing error occurred. Please check your connection.');
      event.preventDefault();
    });
  }
  
  createContainer() {
    const container = document.createElement('div');
    container.className = 'notification-container';
    container.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 10000;
      max-width: 400px;
    `;
    return container;
  }
  
  show(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
      padding: 12px 16px;
      margin-bottom: 8px;
      border-radius: 6px;
      color: white;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      font-size: 14px;
      line-height: 1.4;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      transform: translateX(100%);
      transition: transform 0.3s ease;
      background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
    `;
    
    notification.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <span>${message}</span>
        <button onclick="this.parentElement.parentElement.remove()" 
                style="background: none; border: none; color: white; cursor: pointer; font-size: 16px; margin-left: 8px;">&times;</button>
      </div>
    `;
    
    this.container.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto remove
    if (duration > 0) {
      setTimeout(() => {
        if (notification.parentElement) {
          notification.style.transform = 'translateX(100%)';
          setTimeout(() => notification.remove(), 300);
        }
      }, duration);
    }
    
    return notification;
  }
  
  showError(message, duration = 8000) {
    return this.show(message, 'error', duration);
  }
  
  showSuccess(message, duration = 4000) {
    return this.show(message, 'success', duration);
  }
  
  showWarning(message, duration = 6000) {
    return this.show(message, 'warning', duration);
  }
  
  showInfo(message, duration = 5000) {
    return this.show(message, 'info', duration);
  }
}

const notifications = new NotificationManager();

// Dynamic Visual Effects System
class VisualEffects {
  constructor() {
    this.particles = [];
    this.init();
  }
  
  init() {
    this.createFloatingParticles();
    this.animateElements();
  }
  
  createFloatingParticles() {
    const container = document.getElementById('particles');
    if (!container) return;
    
    // Create 50 floating particles
    for (let i = 0; i < 50; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      
      // Random starting position
      particle.style.left = Math.random() * 100 + '%';
      particle.style.animationDelay = Math.random() * 15 + 's';
      particle.style.animationDuration = (15 + Math.random() * 10) + 's';
      
      // Random size variation
      const size = 1 + Math.random() * 3;
      particle.style.width = size + 'px';
      particle.style.height = size + 'px';
      
      container.appendChild(particle);
      this.particles.push(particle);
    }
  }
  
  animateElements() {
    // Add staggered animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';
      card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      
      setTimeout(() => {
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      }, index * 100);
    });
  }
  
  addPulseEffect(element) {
    element.style.animation = 'pulse 0.6s ease-in-out';
    setTimeout(() => {
      element.style.animation = '';
    }, 600);
  }
}

// Initialize visual effects
const visualEffects = new VisualEffects();

// Initialize backend URL
document.getElementById('backendUrl').value = state.backend;

// Test backend connection on page load
console.log('Page loaded, testing backend connection...');
testBackendConnection();

// Helper functions
function setToken(token) {
  state.token = token;
  if (token) {
    localStorage.setItem('sb_token', token);
    document.getElementById('authStatus').textContent = 'Authenticated';
  } else {
    localStorage.removeItem('sb_token');
    document.getElementById('authStatus').textContent = 'Not authenticated';
  }
}

function apiUrl(path) { 
  return state.backend + path; 
}

async function apiFetch(path, opts = {}) {
  const headers = Object.assign(
    { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    opts.headers || {}
  );
  if (state.token) headers['Authorization'] = 'Bearer ' + state.token;
  
  const fullUrl = apiUrl(path);
  console.log('API Request:', opts.method || 'GET', fullUrl);
  console.log('Headers:', headers);
  
  try {
    const res = await fetch(fullUrl, { ...opts, headers });
    
    if (!res.ok) {
      let errorMessage = `${res.status} ${res.statusText}`;
      
      try {
        const errorData = await res.json();
        if (errorData.detail) {
          errorMessage += `: ${errorData.detail}`;
        }
      } catch {
        const textError = await res.text().catch(() => '');
        if (textError) {
          errorMessage += `: ${textError}`;
        }
      }
      
      // Handle specific error codes
      if (res.status === 401) {
        notifications.showError('Authentication failed. Please log in again.');
        logout();
        throw new Error('Authentication required');
      } else if (res.status === 403) {
        notifications.showError('Access denied. Check your permissions.');
        throw new Error('Access forbidden');
      } else if (res.status === 429) {
        notifications.showError('Too many requests. Please wait a moment and try again.');
        throw new Error('Rate limit exceeded');
      } else if (res.status >= 500) {
        notifications.showError('Server error. Please try again later.');
        throw new Error('Server error');
      }
      
      throw new Error(errorMessage);
    }
    
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) return res.json();
    return res.text();
    
  } catch (error) {
    console.error('API Fetch Error:', error);
    console.log('Request URL was:', fullUrl);
    console.log('Request options:', opts);
    
    if (error instanceof TypeError && error.message.includes('fetch')) {
      // Network error - likely CORS or server not accessible
      const errorMsg = `Failed to connect to backend at ${state.backend}. Please check if the server is running and the URL is correct.`;
      notifications.showError(errorMsg);
      throw new Error('Network/CORS error: ' + error.message);
    }
    
    if (error.name === 'TypeError') {
      notifications.showError('Network error. Please check your internet connection and backend URL.');
      throw new Error('Network error: ' + error.message);
    }
    
    throw error;
  }
}

// Authentication
document.getElementById('btnLogin').addEventListener('click', async (e) => {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();
  
  if (!username || !password) {
    notifications.showError('Please enter both username and password');
    return;
  }
  
  // Add visual feedback
  const btn = e.target;
  visualEffects.addPulseEffect(btn);
  btn.disabled = true;
  btn.textContent = 'Logging in...';
  
  try {
    notifications.showInfo('Connecting to backend...');
    console.log('Attempting login for user:', username);
    
    const body = new URLSearchParams();
    body.set('username', username);
    body.set('password', password);
    
    console.log('Sending login request to:', apiUrl('/auth/token'));
    
    const res = await fetch(apiUrl('/auth/token'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body
    });
    
    console.log('Login response status:', res.status);
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error('Login error response:', errorText);
      throw new Error(errorText);
    }
    
    const data = await res.json();
    console.log('Login successful, received token');
    
    setToken(data.access_token);
    notifications.showSuccess('Login successful! Loading your neural map...');
    
    // Animate successful login
    btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
    btn.textContent = '✓ Success';
    
    setTimeout(async () => {
      await refreshMap();
      
      // Auto-enable 3D mode for demo
      const toggle3D = document.getElementById('toggle3D');
      if (!toggle3D.checked) {
        toggle3D.checked = true;
        toggle3DMode();
      }
    }, 1000);
    
  } catch (e) { 
    console.error('Login error:', e);
    notifications.showError('Login failed: ' + e.message);
    
    // Reset button
    btn.style.background = '';
    btn.textContent = 'Login';
  } finally {
    btn.disabled = false;
  }
});

document.getElementById('btnLogout').addEventListener('click', () => {
  setToken(null);
});

document.getElementById('saveBackendUrl').addEventListener('click', () => {
  state.backend = document.getElementById('backendUrl').value.trim() || 'http://localhost:8000';
  localStorage.setItem('sb_backend', state.backend);
  notifications.showSuccess('Backend URL saved! Testing connection...');
  
  // Test the connection immediately
  testBackendConnection();
  refreshMap();
});

// Add a test connection function
async function testBackendConnection() {
  try {
    console.log('Testing backend connection to:', state.backend);
    const response = await fetch(state.backend + '/', {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      notifications.showSuccess('✅ Backend connection successful: ' + data.message);
      console.log('Backend test successful:', data);
    } else {
      notifications.showError('❌ Backend responded with error: ' + response.status);
    }
  } catch (error) {
    console.error('Backend connection test failed:', error);
    notifications.showError('❌ Cannot connect to backend. Check if server is running at: ' + state.backend);
  }
}

// Slider feedback
document.getElementById('minSim').addEventListener('input', () => {
  document.getElementById('simVal').textContent = (+document.getElementById('minSim').value).toFixed(2);
});
document.getElementById('topK').addEventListener('input', () => {
  document.getElementById('kVal').textContent = document.getElementById('topK').value;
});
document.getElementById('maxNodes').addEventListener('input', () => {
  document.getElementById('maxNodesVal').textContent = document.getElementById('maxNodes').value;
});

// 2D Graph
function initCytoscape() {
  try {
    if (state.cy) { 
      state.cy.destroy(); 
    }
    
    // Determine layout configuration based on current layout
    let layoutConfig;
    try {
      switch (currentLayout) {
        case 'tree':
          layoutConfig = { 
            name: 'breadthfirst', 
            directed: false, 
            roots: function(nodes) {
              try {
                // Find the most connected node as root
                let maxDegree = 0;
                let rootNode = null;
                nodes.forEach(node => {
                  const degree = node.degree();
                  if (degree > maxDegree) {
                    maxDegree = degree;
                    rootNode = node;
                  }
                });
                return rootNode ? [rootNode] : (nodes.length > 0 ? [nodes[0]] : []);
              } catch (e) {
                console.warn('Root selection error:', e);
                return nodes.length > 0 ? [nodes[0]] : [];
              }
            },
            animate: true, 
            animationDuration: 1000,
            padding: 50,
            spacingFactor: 1.5,
            avoidOverlap: true,
            nodeDimensionsIncludeLabels: true
          };
          break;
        case 'radial':
          layoutConfig = { 
            name: 'concentric', 
            concentric: function(node) { 
              try {
                return node.degree(); 
              } catch (e) {
                return 1;
              }
            }, 
            levelWidth: function() { 
              return 3; 
            },
            animate: true, 
            animationDuration: 1000,
            padding: 50,
            spacingFactor: 1.5,
            avoidOverlap: true,
            startAngle: -Math.PI / 2, // Start from top
            clockwise: true
          };
          break;
        default: // force
          layoutConfig = { 
            name: 'cose', 
            animate: 'end', 
            animationDuration: 1000,
            fit: true, 
            padding: 30,
            nodeOverlap: 20,
            idealEdgeLength: 100,
            edgeElasticity: 100,
            nestingFactor: 5,
            gravity: 80,
            numIter: 1000,
            coolingFactor: 0.95,
            minTemp: 1.0
          };
      }
    } catch (layoutError) {
      console.warn('Layout config error, using default:', layoutError);
      layoutConfig = { name: 'grid', animate: true, fit: true };
    }
    
    state.cy = cytoscape({
      container: document.getElementById('cy'),
      boxSelectionEnabled: false,
      wheelSensitivity: 0.3,
      style: [
      {
        selector: 'node',
        style: {
          'background-color': function(node) {
            const degree = node.data('degree') || 1;
            if (degree > 8) return '#f59e0b'; // Highly connected nodes (gold)
            if (degree > 5) return '#8b5cf6'; // Very connected (purple)
            if (degree > 3) return '#5ee3ff'; // Moderately connected (cyan)
            return '#10b981'; // Low connectivity (green)
          },
          'label': 'data(label)',
          'color': '#ffffff',
          'font-size': function(node) {
            const degree = node.data('degree') || 1;
            return Math.max(8, Math.min(16, 8 + degree));
          },
          'font-weight': function(node) {
            const degree = node.data('degree') || 1;
            return degree > 5 ? 'bold' : 'normal';
          },
          'text-outline-color': '#000000',
          'text-outline-width': 2,
          'width': function(node) {
            const degree = node.data('degree') || 1;
            return Math.max(20, Math.min(60, 20 + degree * 3));
          },
          'height': function(node) {
            const degree = node.data('degree') || 1;
            return Math.max(20, Math.min(60, 20 + degree * 3));
          },
          'overlay-padding': '6px',
          'z-index': 2,
          'transition-property': 'background-color, width, height',
          'transition-duration': '0.4s',
          'border-width': function(node) {
            const degree = node.data('degree') || 1;
            return degree > 5 ? 3 : 1;
          },
          'border-color': function(node) {
            const degree = node.data('degree') || 1;
            return degree > 8 ? '#fbbf24' : degree > 5 ? '#a855f7' : '#06b6d4';
          }
        }
      },
      {
        selector: 'node:selected',
        style: {
          'background-color': '#ef4444',
          'border-width': 4,
          'border-color': '#ffffff',
          'z-index': 10
        }
      },
      {
        selector: 'node.highlighted',
        style: {
          'background-color': '#fbbf24',
          'border-width': 3,
          'border-color': '#ffffff',
          'z-index': 5
        }
      },
      {
        selector: 'edge',
        style: {
          'line-color': function(edge) {
            const weight = edge.data('weight') || 0.5;
            if (weight > 0.8) return '#f59e0b'; // Strong connections (gold)
            if (weight > 0.6) return '#8b5cf6'; // Medium connections (purple)
            return '#6b7280'; // Weak connections (gray)
          },
          'width': function(edge) {
            const weight = edge.data('weight') || 0.5;
            return Math.max(1, Math.min(8, weight * 10));
          },
          'opacity': function(edge) {
            const weight = edge.data('weight') || 0.5;
            return Math.max(0.3, Math.min(1, weight + 0.2));
          },
          'curve-style': currentLayout === 'tree' ? 'straight' : 'haystack',
          'transition-property': 'line-color, width, opacity',
          'transition-duration': '0.4s',
          'target-arrow-color': function(edge) {
            const weight = edge.data('weight') || 0.5;
            return weight > 0.7 ? '#f59e0b' : '#8b5cf6';
          },
          'target-arrow-shape': currentLayout === 'tree' ? 'triangle' : 'none'
        }
      },
      {
        selector: 'edge:selected',
        style: {
          'line-color': '#ef4444',
          'width': 6,
          'opacity': 1,
          'z-index': 10
        }
      },
      {
        selector: 'edge.highlighted',
        style: {
          'line-color': '#fbbf24',
          'width': function(edge) {
            const weight = edge.data('weight') || 0.5;
            return Math.max(3, Math.min(10, weight * 12));
          },
          'opacity': 1,
          'z-index': 5
        }
      }
    ],
    layout: layoutConfig
  });

  // Enhanced interactions
  state.cy.on('mouseover', 'node', (evt) => {
    const n = evt.target.data();
    showTip(n.title, n.preview, evt.renderedPosition);
    
    // Highlight connected nodes
    const connectedEdges = evt.target.connectedEdges();
    const connectedNodes = connectedEdges.connectedNodes();
    
    connectedNodes.addClass('highlighted');
    connectedEdges.addClass('highlighted');
  });
  
  state.cy.on('mouseout', 'node', (evt) => {
    hideTip();
    
    // Remove highlights
    state.cy.elements().removeClass('highlighted');
  });
  
  state.cy.on('tap', 'node', (evt) => {
    const n = evt.target.data();
    alert(n.title + '\n\n' + (n.preview || ''));
  });
  
  // Add dragging capability
  state.cy.on('free', 'node', (evt) => {
    // Save position when node is moved
    const node = evt.target;
    const position = node.position();
    console.log(`Node ${node.data('title')} moved to:`, position);
  });
  
  } catch (error) {
    console.error('Error initializing Cytoscape:', error);
    if (notifications) {
      notifications.show('Layout initialization failed - using simple view', 'warning');
    }
    // Fallback to simple cytoscape instance
    state.cy = cytoscape({
      container: document.getElementById('cy'),
      elements: [],
      style: [{ selector: 'node', style: { 'background-color': '#666' } }],
      layout: { name: 'grid' }
    });
  }
}

function getHighestDegreeNodes() {
  if (!state.cy || !state.cy.nodes()) return [];
  
  return state.cy.nodes().max((node) => node.degree()).element;
}

function showTip(title, text, pos) {
  const tooltip = document.getElementById('tooltip');
  tooltip.innerHTML = '<strong>' + escapeHtml(title || '') + '</strong><br>' + escapeHtml(text || '');
  tooltip.style.left = pos.x + 'px';
  tooltip.style.top = pos.y + 'px';
  tooltip.classList.remove('hidden');
}

function hideTip() { 
  document.getElementById('tooltip').classList.add('hidden'); 
}

function escapeHtml(s) { 
  return s.replace(/[&<>"']/g, function(c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  }); 
}

// 3D Neural Network Visualization (Obsidian-like)
function init3D() {
  console.log('Initializing 3D visualization...');
  
  if (typeof THREE === 'undefined') {
    console.error('THREE.js not loaded!');
    return false;
  }
  
  const container = document.getElementById('threeContainer');
  if (!container) {
    console.error('3D container not found!');
    return false;
  }
  
  const rect = container.getBoundingClientRect();
  console.log('Container dimensions:', rect.width, 'x', rect.height);
  
  try {
    // Scene setup
    state.three.scene = new THREE.Scene();
    state.three.scene.background = new THREE.Color(0x0a0a0a);
    state.three.scene.fog = new THREE.Fog(0x0a0a0a, 100, 2000);
    
    // Camera setup
    state.three.camera = new THREE.PerspectiveCamera(75, rect.width / rect.height, 0.1, 2000);
  state.three.camera.position.set(0, 0, 300);
  
  // Renderer setup
  state.three.renderer = new THREE.WebGLRenderer({ 
    antialias: true, 
    alpha: true,
    precision: 'highp'
  });
  state.three.renderer.setSize(rect.width, rect.height);
  state.three.renderer.setPixelRatio(window.devicePixelRatio);
  state.three.renderer.shadowMap.enabled = true;
  state.three.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  state.three.renderer.toneMapping = THREE.ACESFilmicToneMapping;
  state.three.renderer.toneMappingExposure = 1.5;
  container.appendChild(state.three.renderer.domElement);
  
  // Enhanced Controls setup with WASD, dragging, and auto-rotation
  if (typeof THREE.OrbitControls === 'undefined' && typeof window.OrbitControls === 'undefined') {
    console.error('OrbitControls not loaded. Using enhanced fallback controls.');
    setupEnhancedFallbackControls(container);
  } else {
    // Use OrbitControls if available
    const OrbitControlsClass = THREE.OrbitControls || window.OrbitControls;
    state.three.controls = new OrbitControlsClass(state.three.camera, state.three.renderer.domElement);
    state.three.controls.enableDamping = true;
    state.three.controls.dampingFactor = 0.05; // Smoother damping
    state.three.controls.minDistance = 50;
    state.three.controls.maxDistance = 1500;
    state.three.controls.autoRotate = false;
    state.three.controls.enablePan = true;
    state.three.controls.panSpeed = 2;
    state.three.controls.rotateSpeed = 1;
    state.three.controls.zoomSpeed = 1.2;
  }
  
  // Add WASD keyboard controls and auto-rotation toggle
  setupKeyboardControls(container);
  setupNodeDragging(container);
  
  // Lighting setup (Neural network ambiance)
  const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
  state.three.scene.add(ambientLight);
  
  const directionalLight = new THREE.DirectionalLight(0x8b5cf6, 0.8);
  directionalLight.position.set(200, 200, 100);
  directionalLight.castShadow = true;
  directionalLight.shadow.mapSize.width = 2048;
  directionalLight.shadow.mapSize.height = 2048;
  state.three.scene.add(directionalLight);
  
  const pointLight1 = new THREE.PointLight(0x5ee3ff, 0.6, 500);
  pointLight1.position.set(-200, -200, 200);
  state.three.scene.add(pointLight1);
  
  const pointLight2 = new THREE.PointLight(0xf59e0b, 0.4, 300);
  pointLight2.position.set(200, -100, -100);
  state.three.scene.add(pointLight2);
  
  // Raycaster for interaction
  state.three.raycaster = new THREE.Raycaster();
  state.three.mouse = new THREE.Vector2();
  
  // Event listeners
  container.addEventListener('mousemove', onMouse3DMove);
  container.addEventListener('click', onMouse3DClick);
  container.addEventListener('dblclick', onMouse3DDoubleClick);
  window.addEventListener('resize', onResize3D);
  
  // Create geometries and materials for different node types
  createNodeAssets();
  
  animate3D();
  
  console.log('3D visualization initialized successfully');
  return true;
  
  } catch (error) {
    console.error('Error initializing 3D visualization:', error);
    return false;
  }
}

function createNodeAssets() {
  try {
    console.log('Creating node assets...');
    
    // Check if THREE is available
    if (typeof THREE === 'undefined') {
      throw new Error('THREE.js not loaded');
    }
    
    // Create geometries for different node types
    state.three.nodeGeometries.set('sphere', new THREE.SphereGeometry(1, 16, 16));
    state.three.nodeGeometries.set('octahedron', new THREE.OctahedronGeometry(1));
    state.three.nodeGeometries.set('dodecahedron', new THREE.DodecahedronGeometry(1));
    state.three.nodeGeometries.set('icosahedron', new THREE.IcosahedronGeometry(1));
    
    console.log('Created geometries:', state.three.nodeGeometries.size);
    
    // Create enhanced materials for different node types with better glowing
    Object.entries(state.nodeTypes).forEach(([type, config]) => {
      const material = new THREE.MeshPhongMaterial({
        color: config.color,
        emissive: config.color,
        emissiveIntensity: 0.15, // Increased base glow
        shininess: 150,
        transparent: true,
        opacity: 0.95,
        specular: new THREE.Color(0x111111)
      });
      state.three.nodeMaterials.set(type, material);
    });
    
    console.log('Created materials:', state.three.nodeMaterials.size);
    
  } catch (error) {
    console.error('Error creating node assets:', error);
    notifications.showError('Failed to create 3D assets: ' + error.message);
    throw error;
  }
}

function determineNodeType(node) {
  const degree = node.degree || 0;
  const titleLower = (node.title || '').toLowerCase();
  
  // Determine node type based on content and connections
  if (titleLower.includes('important') || titleLower.includes('critical') || degree > 10) {
    return 'important';
  } else if (degree > 5 || titleLower.includes('concept') || titleLower.includes('idea')) {
    return 'concept';
  } else if (degree > 2 || titleLower.includes('topic') || titleLower.includes('category')) {
    return 'topic';
  } else {
    return 'note';
  }
}

function createNodeMesh(node, position) {
  const nodeType = determineNodeType(node);
  const degree = node.degree || 0;
  
  // Scale and glow based on connections
  const baseScale = 1 + Math.min(degree * 0.2, 3); // Scale from 1 to 4
  const glowIntensity = 0.1 + Math.min(degree * 0.1, 1.0); // Glow from 0.1 to 1.1
  
  // Get geometry and material
  const geometry = state.three.nodeGeometries.get(nodeType === 'important' ? 'icosahedron' :
                   nodeType === 'concept' ? 'dodecahedron' :
                   nodeType === 'topic' ? 'octahedron' : 'sphere');
  
  // Create custom material with connection-based properties
  const baseColor = state.nodeTypes[nodeType].color;
  const material = new THREE.MeshPhongMaterial({
    color: baseColor,
    emissive: baseColor,
    emissiveIntensity: glowIntensity,
    shininess: 100 + degree * 10, // More connections = more shiny
    transparent: true,
    opacity: 0.85 + Math.min(degree * 0.03, 0.15) // More opaque with more connections
  });
  
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(position.x, position.y, position.z);
  mesh.scale.setScalar(baseScale);
  
  // Store original values for animations
  mesh.userData = {
    data: node,
    nodeType: nodeType,
    originalScale: baseScale,
    originalEmissive: glowIntensity,
    degree: degree
  };
  
  return mesh;
}

function render3DMap(nodes, edges) {
  if (!state.three.scene) {
    console.error('3D scene not initialized');
    return;
  }
  
  console.log(`Rendering 3D map with ${nodes.length} nodes and ${edges.length} edges`);
  
  try {
    // Performance optimization: Use object pooling for large datasets
    const maxNodes = 1000; // Limit for performance
    const maxEdges = 2000;
    
    // Limit nodes and edges if dataset is too large
    const limitedNodes = nodes.length > maxNodes ? 
      nodes.slice(0, maxNodes) : nodes;
    const limitedEdges = edges.length > maxEdges ? 
      edges.slice(0, maxEdges) : edges;
    
    if (nodes.length > maxNodes) {
      notifications.showWarning(`Showing ${maxNodes} of ${nodes.length} nodes for performance. Use filters to see specific nodes.`);
    }
  
    // Clear existing objects efficiently
    state.three.nodes.forEach(nodeObj => {
      if (nodeObj.mesh && nodeObj.mesh.parent) {
        state.three.scene.remove(nodeObj.mesh);
      }
      // Dispose of geometry and material to free memory
      if (nodeObj.mesh && nodeObj.mesh.geometry) {
        nodeObj.mesh.geometry.dispose();
      }
      if (nodeObj.mesh && nodeObj.mesh.material) {
        nodeObj.mesh.material.dispose();
      }
    });
    
    state.three.edges.forEach(edgeObj => {
      if (edgeObj.mesh && edgeObj.mesh.parent) {
        state.three.scene.remove(edgeObj.mesh);
      }
      if (edgeObj.mesh && edgeObj.mesh.geometry) {
        edgeObj.mesh.geometry.dispose();
      }
      if (edgeObj.mesh && edgeObj.mesh.material) {
        edgeObj.mesh.material.dispose();
      }
    });
    
    state.three.nodes = [];
    state.three.edges = [];
  
    // Calculate 3D positions using force-directed layout
    const positions = calculate3DPositions(limitedNodes, limitedEdges);
    
    // Performance: Use instanced meshes for nodes of the same type
    const nodeGroups = {};
    
    // Create node meshes with enhanced connection-based styling
    limitedNodes.forEach((node, index) => {
    const pos = positions[index];
    const degree = node.degree || 0;
    
    // Use our new enhanced node mesh creation
    const mesh = createNodeMesh(node, pos);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.userData.index = index;
    mesh.userData.type = 'node';
    
    state.three.scene.add(mesh);
    state.three.nodes.push({ mesh, data: node, type: mesh.userData.nodeType });
    
    // Add pulsing animation for highly connected nodes
    if (degree > 3) {
      animateNodePulse(mesh);
    }
  });
  
  // Create edge connections with neural network styling
  edges.forEach(edge => {
    const sourceNode = nodes.find(n => n.id === edge.source);
    const targetNode = nodes.find(n => n.id === edge.target);
    if (!sourceNode || !targetNode) return;
    
    const sourceIndex = nodes.indexOf(sourceNode);
    const targetIndex = nodes.indexOf(targetNode);
    const sourcePos = positions[sourceIndex];
    const targetPos = positions[targetIndex];
    
    // Create curved connection line
    const curve = createCurvedConnection(sourcePos, targetPos);
    const geometry = new THREE.TubeGeometry(curve, 20, 0.3, 8, false);
    
    // Material based on connection strength
    const weight = edge.weight || 0.5;
    const material = new THREE.MeshPhongMaterial({
      color: weight > 0.7 ? 0x5ee3ff : weight > 0.5 ? 0x8b5cf6 : 0x6b7280,
      emissive: weight > 0.7 ? 0x1a4d5c : weight > 0.5 ? 0x3d1a66 : 0x2d3748,
      emissiveIntensity: weight * 0.3,
      transparent: true,
      opacity: Math.max(0.3, weight * 0.8),
      shininess: 50
    });
    
    const line = new THREE.Mesh(geometry, material);
    line.userData = { type: 'edge', data: edge };
    
    state.three.scene.add(line);
    state.three.edges.push({ mesh: line, data: edge });
  });
  
  // Add network particles for visual flair
  addNetworkParticles();
  
  console.log('3D map rendered successfully');
  
  } catch (error) {
    console.error('Error rendering 3D map:', error);
    notifications.showError('Failed to render 3D visualization. Try switching to 2D mode.');
  }
}

function createCurvedConnection(start, end) {
  const startVec = new THREE.Vector3(start.x, start.y, start.z);
  const endVec = new THREE.Vector3(end.x, end.y, end.z);
  
  // Create a slight curve for more organic connections
  const midPoint = startVec.clone().lerp(endVec, 0.5);
  const distance = startVec.distanceTo(endVec);
  const offset = distance * 0.1;
  
  // Add some randomness to the curve
  midPoint.x += (Math.random() - 0.5) * offset;
  midPoint.y += (Math.random() - 0.5) * offset;
  midPoint.z += (Math.random() - 0.5) * offset;
  
  return new THREE.QuadraticBezierCurve3(startVec, midPoint, endVec);
}

function addNetworkParticles() {
  const particleCount = 200;
  const particles = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  
  for (let i = 0; i < particleCount * 3; i += 3) {
    positions[i] = (Math.random() - 0.5) * 1000;
    positions[i + 1] = (Math.random() - 0.5) * 1000;
    positions[i + 2] = (Math.random() - 0.5) * 1000;
  }
  
  particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  
  const particleMaterial = new THREE.PointsMaterial({
    color: 0x8b5cf6,
    size: 1,
    transparent: true,
    opacity: 0.3,
    sizeAttenuation: true
  });
  
  const particleSystem = new THREE.Points(particles, particleMaterial);
  state.three.scene.add(particleSystem);
}

function animateNodePulse(mesh) {
  const originalScale = mesh.userData.originalScale;
  const pulseSpeed = 0.002 + Math.random() * 0.003;
  
  const animate = () => {
    if (!mesh.parent) return; // Stop if node is removed
    
    const time = Date.now() * pulseSpeed;
    const scale = originalScale + Math.sin(time) * 0.2;
    mesh.scale.setScalar(scale);
    
    const emissive = mesh.userData.originalEmissive + Math.sin(time) * 0.1;
    mesh.material.emissiveIntensity = Math.max(0, emissive);
    
    requestAnimationFrame(animate);
  };
  
  animate();
}

function calculate3DPositions(nodes, edges) {
  // Use layout-specific positioning
  let positions2D;
  
  switch (currentLayout) {
    case 'tree':
      positions2D = createTreeLayout(nodes, edges);
      break;
    case 'radial':
      positions2D = createRadialLayout(nodes, edges);
      break;
    default: // force
      positions2D = createForceLayout(nodes, edges);
  }
  
  // Convert 2D positions to 3D with some Z variation
  return nodes.map(node => {
    const pos2D = positions2D[node.id] || {x: 0, y: 0, z: 0};
    return {
      x: pos2D.x,
      y: pos2D.y,
      z: pos2D.z + (Math.random() - 0.5) * 50 // Add Z variation for 3D effect
    };
  });
}

function createForceLayout(nodes, edges) {
  const positions = {};
  
  // Initialize with random positions
  nodes.forEach(node => {
    positions[node.id] = {
      x: (Math.random() - 0.5) * 500,
      y: (Math.random() - 0.5) * 500,
      z: (Math.random() - 0.5) * 500
    };
  });
  
  // Enhanced force-directed layout with better clustering
  for (let iter = 0; iter < 150; iter++) {
    const forces = {};
    nodes.forEach(node => {
      forces[node.id] = { x: 0, y: 0, z: 0 };
    });
    
    // Repulsion between all nodes
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const nodeA = nodes[i];
        const nodeB = nodes[j];
        const posA = positions[nodeA.id];
        const posB = positions[nodeB.id];
        
        const dx = posA.x - posB.x;
        const dy = posA.y - posB.y;
        const dz = posA.z - posB.z;
        const dist = Math.sqrt(dx*dx + dy*dy + dz*dz) + 1;
        const force = 2000 / (dist * dist);
        
        forces[nodeA.id].x += (dx / dist) * force;
        forces[nodeA.id].y += (dy / dist) * force;
        forces[nodeA.id].z += (dz / dist) * force;
        forces[nodeB.id].x -= (dx / dist) * force;
        forces[nodeB.id].y -= (dy / dist) * force;
        forces[nodeB.id].z -= (dz / dist) * force;
      }
    }
    
    // Attraction for connected nodes
    edges.forEach(edge => {
      const posA = positions[edge.source];
      const posB = positions[edge.target];
      if (!posA || !posB) return;
      
      const dx = posB.x - posA.x;
      const dy = posB.y - posA.y;
      const dz = posB.z - posA.z;
      const dist = Math.sqrt(dx*dx + dy*dy + dz*dz) + 1;
      const idealDistance = 80 + (edge.weight || 0.5) * 40;
      const force = (dist - idealDistance) * 0.1 * (edge.weight || 0.5);
      
      forces[edge.source].x += (dx / dist) * force;
      forces[edge.source].y += (dy / dist) * force;
      forces[edge.source].z += (dz / dist) * force;
      forces[edge.target].x -= (dx / dist) * force;
      forces[edge.target].y -= (dy / dist) * force;
      forces[edge.target].z -= (dz / dist) * force;
    });
    
    // Apply forces with damping
    const damping = 0.8;
    nodes.forEach(node => {
      const pos = positions[node.id];
      const force = forces[node.id];
      pos.x += force.x * 0.1 * damping;
      pos.y += force.y * 0.1 * damping;
      pos.z += force.z * 0.1 * damping;
    });
  }
  
  return positions;
}

function setupEnhancedFallbackControls(container) {
  let mouseDown = false;
  let rightMouseDown = false;
  let middleMouseDown = false;
  let lastMouseX = 0, lastMouseY = 0;
  let momentum = { x: 0, y: 0, rotX: 0, rotY: 0 };
  
  container.addEventListener('mousedown', (e) => {
    if (e.button === 0) { // Left click - rotation
      mouseDown = true;
    } else if (e.button === 1) { // Middle click - zoom
      middleMouseDown = true;
      e.preventDefault();
    } else if (e.button === 2) { // Right click - pan
      rightMouseDown = true;
      e.preventDefault();
    }
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
  });
  
  container.addEventListener('mouseup', (e) => {
    if (e.button === 0) mouseDown = false;
    if (e.button === 1) middleMouseDown = false;
    if (e.button === 2) rightMouseDown = false;
  });
  
  container.addEventListener('contextmenu', (e) => e.preventDefault());
  
  container.addEventListener('mousemove', (e) => {
    const deltaX = e.clientX - lastMouseX;
    const deltaY = e.clientY - lastMouseY;
    
    if (mouseDown) {
      // Enhanced rotation with momentum
      const rotationSpeed = 0.008;
      const spherical = new THREE.Spherical();
      spherical.setFromVector3(state.three.camera.position);
      spherical.theta -= deltaX * rotationSpeed;
      spherical.phi += deltaY * rotationSpeed;
      spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));
      
      state.three.camera.position.setFromSpherical(spherical);
      state.three.camera.lookAt(0, 0, 0);
      
      // Store momentum for smooth continuation
      momentum.rotX = deltaY * rotationSpeed;
      momentum.rotY = deltaX * rotationSpeed;
    } else if (rightMouseDown) {
      // Enhanced 3D panning
      const panSpeed = 3;
      const direction = new THREE.Vector3();
      state.three.camera.getWorldDirection(direction);
      const right = new THREE.Vector3().crossVectors(direction, state.three.camera.up).normalize();
      const up = new THREE.Vector3().crossVectors(right, direction).normalize();
      
      const panX = right.multiplyScalar(-deltaX * panSpeed);
      const panY = up.multiplyScalar(deltaY * panSpeed);
      
      state.three.camera.position.add(panX).add(panY);
      
      // Store momentum
      momentum.x = -deltaX * panSpeed * 0.5;
      momentum.y = deltaY * panSpeed * 0.5;
    } else if (middleMouseDown) {
      // Middle mouse zoom
      const zoomSpeed = 0.02;
      const zoom = deltaY > 0 ? 1 + zoomSpeed : 1 - zoomSpeed;
      state.three.camera.position.multiplyScalar(zoom);
      
      // Keep camera within bounds
      const distance = state.three.camera.position.length();
      if (distance < 30) {
        state.three.camera.position.normalize().multiplyScalar(30);
      } else if (distance > 2000) {
        state.three.camera.position.normalize().multiplyScalar(2000);
      }
    }
    
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
  });
  
  container.addEventListener('wheel', (e) => {
    e.preventDefault();
    const zoomSpeed = 0.1;
    const scale = e.deltaY > 0 ? 1 + zoomSpeed : 1 - zoomSpeed;
    state.three.camera.position.multiplyScalar(scale);
    
    // Keep camera within reasonable bounds
    const distance = state.three.camera.position.length();
    if (distance < 30) {
      state.three.camera.position.normalize().multiplyScalar(30);
    } else if (distance > 2000) {
      state.three.camera.position.normalize().multiplyScalar(2000);
    }
  });
  
  // Apply momentum for smooth movement
  function applyMomentum() {
    const damping = 0.95;
    
    if (Math.abs(momentum.x) > 0.01 || Math.abs(momentum.y) > 0.01) {
      const direction = new THREE.Vector3();
      state.three.camera.getWorldDirection(direction);
      const right = new THREE.Vector3().crossVectors(direction, state.three.camera.up).normalize();
      const up = new THREE.Vector3().crossVectors(right, direction).normalize();
      
      const panX = right.multiplyScalar(momentum.x);
      const panY = up.multiplyScalar(momentum.y);
      
      state.three.camera.position.add(panX).add(panY);
      
      momentum.x *= damping;
      momentum.y *= damping;
    }
    
    requestAnimationFrame(applyMomentum);
  }
  
  applyMomentum();
}

function setupKeyboardControls(container) {
  const keys = {};
  let autoRotateEnabled = false;
  const moveSpeed = 12; // Increased for better movement
  let gravityEnabled = true;
  
  // Focus container to receive keyboard events
  container.setAttribute('tabindex', '0');
  container.style.outline = 'none';
  
  // Show enhanced control help
  setTimeout(() => {
    if (notifications) {
      notifications.show('Enhanced 3D Controls: Click here first, then use WASD/QE, G for gravity, F to flip nodes, T to arrange by connections', 'info');
    }
  }, 1000);
  
  container.addEventListener('keydown', (e) => {
    keys[e.key.toLowerCase()] = true;
    
    // Enhanced keyboard shortcuts
    switch (e.key.toLowerCase()) {
      case 'r': // Toggle auto-rotation
        autoRotateEnabled = !autoRotateEnabled;
        if (state.three.controls && state.three.controls.autoRotate !== undefined) {
          state.three.controls.autoRotate = autoRotateEnabled;
        }
        if (notifications) {
          notifications.show(`Auto-rotation: ${autoRotateEnabled ? 'ON' : 'OFF'}`, 'info');
        }
        break;
        
      case 'c': // Reset camera position
        state.three.camera.position.set(0, 0, 300);
        state.three.camera.lookAt(0, 0, 0);
        if (notifications) {
          notifications.show('Camera reset to center', 'info');
        }
        break;
        
      case 'g': // Toggle gravity mode
        gravityEnabled = !gravityEnabled;
        if (gravityEnabled) {
          applyGravityLayout();
        }
        if (notifications) {
          notifications.show(`Gravity mode: ${gravityEnabled ? 'ON - Most connected at top' : 'OFF'}`, 'info');
        }
        break;
        
      case 'f': // Flip/reorganize nodes
        flipNodesArrangement();
        if (notifications) {
          notifications.show('Nodes flipped and reorganized', 'info');
        }
        break;
        
      case 't': // Arrange by connections (top-down)
        arrangeByConnections();
        if (notifications) {
          notifications.show('Arranged by connection count', 'info');
        }
        break;
        
      case 'x': // Reset all node positions
        resetNodePositions();
        if (notifications) {
          notifications.show('Node positions reset', 'info');
        }
        break;
    }
  });
  
  container.addEventListener('keyup', (e) => {
    keys[e.key.toLowerCase()] = false;
  });
  
  // Enhanced movement with 6DOF and smooth acceleration
  function animateKeyboardMovement() {
    if (!state.three.camera) return;
    
    const direction = new THREE.Vector3();
    state.three.camera.getWorldDirection(direction);
    const right = new THREE.Vector3().crossVectors(direction, state.three.camera.up).normalize();
    const up = new THREE.Vector3().crossVectors(right, direction).normalize();
    
    let moved = false;
    const acceleration = keys['shift'] ? 2.0 : (keys['alt'] ? 0.3 : 1.0); // Speed modifiers
    const currentSpeed = moveSpeed * acceleration;
    
    // Forward/Backward movement
    if (keys['w'] || keys['arrowup']) {
      state.three.camera.position.add(direction.clone().multiplyScalar(currentSpeed));
      moved = true;
    }
    if (keys['s'] || keys['arrowdown']) {
      state.three.camera.position.add(direction.clone().multiplyScalar(-currentSpeed));
      moved = true;
    }
    
    // Left/Right strafe
    if (keys['a'] || keys['arrowleft']) {
      state.three.camera.position.add(right.clone().multiplyScalar(-currentSpeed));
      moved = true;
    }
    if (keys['d'] || keys['arrowright']) {
      state.three.camera.position.add(right.clone().multiplyScalar(currentSpeed));
      moved = true;
    }
    
    // Up/Down movement (multiple keys supported)
    if (keys['q'] || keys[' '] || keys['pageup']) { 
      state.three.camera.position.add(up.clone().multiplyScalar(currentSpeed));
      moved = true;
    }
    if (keys['e'] || keys['control'] || keys['pagedown']) { 
      state.three.camera.position.add(up.clone().multiplyScalar(-currentSpeed));
      moved = true;
    }
    
    // Rotation controls (hold and move)
    if (keys['j']) { // Rotate left
      const spherical = new THREE.Spherical();
      spherical.setFromVector3(state.three.camera.position);
      spherical.theta += 0.02;
      state.three.camera.position.setFromSpherical(spherical);
      state.three.camera.lookAt(0, 0, 0);
    }
    if (keys['l']) { // Rotate right
      const spherical = new THREE.Spherical();
      spherical.setFromVector3(state.three.camera.position);
      spherical.theta -= 0.02;
      state.three.camera.position.setFromSpherical(spherical);
      state.three.camera.lookAt(0, 0, 0);
    }
    if (keys['i']) { // Rotate up
      const spherical = new THREE.Spherical();
      spherical.setFromVector3(state.three.camera.position);
      spherical.phi -= 0.02;
      spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));
      state.three.camera.position.setFromSpherical(spherical);
      state.three.camera.lookAt(0, 0, 0);
    }
    if (keys['k']) { // Rotate down
      const spherical = new THREE.Spherical();
      spherical.setFromVector3(state.three.camera.position);
      spherical.phi += 0.02;
      spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));
      state.three.camera.position.setFromSpherical(spherical);
      state.three.camera.lookAt(0, 0, 0);
    }
    
    // Auto-rotation fallback for browsers without OrbitControls
    if (autoRotateEnabled && (!state.three.controls || !state.three.controls.autoRotate)) {
      const spherical = new THREE.Spherical();
      spherical.setFromVector3(state.three.camera.position);
      spherical.theta += 0.005; // Slower rotation
      state.three.camera.position.setFromSpherical(spherical);
      state.three.camera.lookAt(0, 0, 0);
    }
    
    // Keep camera within reasonable bounds
    if (moved) {
      const distance = state.three.camera.position.length();
      if (distance < 20) {
        state.three.camera.position.normalize().multiplyScalar(20);
      } else if (distance > 3000) {
        state.three.camera.position.normalize().multiplyScalar(3000);
      }
    }
    
    requestAnimationFrame(animateKeyboardMovement);
  }
  
  animateKeyboardMovement();
}

function applyGravityLayout() {
  if (!state.three.nodes || state.three.nodes.length === 0) return;
  
  try {
    console.log('Applying gravity layout...');
    
    // Sort nodes by connection count
    const sortedNodes = [...state.three.nodes].sort((a, b) => {
      const degreeA = a.data.degree || 0;
      const degreeB = b.data.degree || 0;
      return degreeB - degreeA;
    });
    
    const totalNodes = sortedNodes.length;
    const verticalSpacing = 120;
    const horizontalSpacing = 100;
    const maxNodesPerLevel = Math.ceil(Math.sqrt(totalNodes));
    
    sortedNodes.forEach((nodeObj, index) => {
      const level = Math.floor(index / maxNodesPerLevel);
      const positionInLevel = index % maxNodesPerLevel;
      const nodesInThisLevel = Math.min(maxNodesPerLevel, totalNodes - level * maxNodesPerLevel);
      
      // Calculate position with most connected at top
      const x = (positionInLevel - (nodesInThisLevel - 1) / 2) * horizontalSpacing;
      const y = 200 - (level * verticalSpacing); // Top = positive Y
      const z = (Math.random() - 0.5) * 50;
      
      // Animate to new position
      animateNodeToPosition(nodeObj.mesh, { x, y, z });
    });
    
    if (notifications) {
      notifications.show('Applied gravity layout - most connected nodes at top', 'success');
    }
  } catch (error) {
    console.error('Error applying gravity layout:', error);
  }
}

function flipNodesArrangement() {
  if (!state.three.nodes || state.three.nodes.length === 0) return;
  
  try {
    state.three.nodes.forEach(nodeObj => {
      const mesh = nodeObj.mesh;
      const currentPos = mesh.position;
      
      // Flip Y and Z coordinates for interesting rearrangement
      const newPos = {
        x: -currentPos.x + (Math.random() - 0.5) * 20,
        y: -currentPos.y,
        z: currentPos.z + (Math.random() - 0.5) * 100
      };
      
      animateNodeToPosition(mesh, newPos);
    });
    
    if (notifications) {
      notifications.show('Nodes flipped and scattered', 'info');
    }
  } catch (error) {
    console.error('Error flipping nodes:', error);
  }
}

function arrangeByConnections() {
  if (!state.three.nodes || state.three.nodes.length === 0) return;
  
  try {
    // Group nodes by connection tiers
    const tiers = {
      high: [], // 8+ connections
      medium: [], // 4-7 connections  
      low: [], // 1-3 connections
      isolated: [] // 0 connections
    };
    
    state.three.nodes.forEach(nodeObj => {
      const degree = nodeObj.data.degree || 0;
      if (degree >= 8) tiers.high.push(nodeObj);
      else if (degree >= 4) tiers.medium.push(nodeObj);
      else if (degree >= 1) tiers.low.push(nodeObj);
      else tiers.isolated.push(nodeObj);
    });
    
    // Arrange each tier
    const tierConfigs = [
      { tier: tiers.high, y: 250, radius: 80, color: 0xffd700 },
      { tier: tiers.medium, y: 100, radius: 150, color: 0x8b5cf6 },
      { tier: tiers.low, y: -50, radius: 220, color: 0x5ee3ff },
      { tier: tiers.isolated, y: -200, radius: 300, color: 0x10b981 }
    ];
    
    tierConfigs.forEach(config => {
      config.tier.forEach((nodeObj, index) => {
        if (config.tier.length === 1) {
          // Single node at center
          animateNodeToPosition(nodeObj.mesh, { x: 0, y: config.y, z: 0 });
        } else {
          // Arrange in circle
          const angle = (index / config.tier.length) * 2 * Math.PI;
          const x = Math.cos(angle) * config.radius;
          const z = Math.sin(angle) * config.radius;
          animateNodeToPosition(nodeObj.mesh, { x, y: config.y, z });
        }
      });
    });
    
    if (notifications) {
      notifications.show(`Arranged by connections: ${tiers.high.length} high, ${tiers.medium.length} medium, ${tiers.low.length} low, ${tiers.isolated.length} isolated`, 'success');
    }
  } catch (error) {
    console.error('Error arranging by connections:', error);
  }
}

function resetNodePositions() {
  if (!state.three.nodes || state.three.nodes.length === 0) return;
  
  try {
    // Reset to original calculated positions or random
    state.three.nodes.forEach((nodeObj, index) => {
      const angle = (index / state.three.nodes.length) * 2 * Math.PI;
      const radius = 150 + Math.random() * 100;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      const y = (Math.random() - 0.5) * 200;
      
      animateNodeToPosition(nodeObj.mesh, { x, y, z });
    });
    
    if (notifications) {
      notifications.show('Node positions reset to circular arrangement', 'info');
    }
  } catch (error) {
    console.error('Error resetting positions:', error);
  }
}

function animateNodeToPosition(mesh, targetPosition, duration = 1000) {
  if (!mesh || !targetPosition) return;
  
  const startPosition = mesh.position.clone();
  const startTime = Date.now();
  
  function animate() {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // Easing function for smooth animation
    const easeProgress = 1 - Math.pow(1 - progress, 3);
    
    mesh.position.lerpVectors(startPosition, new THREE.Vector3(targetPosition.x, targetPosition.y, targetPosition.z), easeProgress);
    
    // Update edge connections
    updateNodeConnections(mesh);
    
    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  }
  
  animate();
}

function setupNodeDragging(container) {
  let draggedNode = null;
  let dragPlane = new THREE.Plane();
  let intersection = new THREE.Vector3();
  
  container.addEventListener('mousedown', (e) => {
    if (e.button !== 0 || e.shiftKey) return; // Only left click + shift for dragging
    
    state.three.raycaster.setFromCamera(state.three.mouse, state.three.camera);
    const intersects = state.three.raycaster.intersectObjects(
      state.three.nodes.map(n => n.mesh)
    );
    
    if (intersects.length > 0 && e.shiftKey) {
      draggedNode = intersects[0].object;
      dragPlane.setFromNormalAndCoplanarPoint(
        state.three.camera.getWorldDirection(new THREE.Vector3()),
        draggedNode.position
      );
      e.stopPropagation();
    }
  });
  
  container.addEventListener('mousemove', (e) => {
    if (draggedNode) {
      state.three.raycaster.setFromCamera(state.three.mouse, state.three.camera);
      if (state.three.raycaster.ray.intersectPlane(dragPlane, intersection)) {
        draggedNode.position.copy(intersection);
        
        // Update connections
        updateNodeConnections(draggedNode);
      }
    }
  });
  
  container.addEventListener('mouseup', () => {
    draggedNode = null;
  });
}

function updateNodeConnections(draggedMesh) {
  const draggedNodeData = draggedMesh.userData.data;
  
  // Update edge positions for this node
  state.three.edges.forEach(edgeObj => {
    const edge = edgeObj.userData.data;
    if (edge.source === draggedNodeData.id || edge.target === draggedNodeData.id) {
      const sourceNode = state.three.nodes.find(n => n.data.id === edge.source);
      const targetNode = state.three.nodes.find(n => n.data.id === edge.target);
      
      if (sourceNode && targetNode) {
        const geometry = edgeObj.geometry;
        const positions = geometry.attributes.position.array;
        
        positions[0] = sourceNode.mesh.position.x;
        positions[1] = sourceNode.mesh.position.y;
        positions[2] = sourceNode.mesh.position.z;
        positions[3] = targetNode.mesh.position.x;
        positions[4] = targetNode.mesh.position.y;
        positions[5] = targetNode.mesh.position.z;
        
        geometry.attributes.position.needsUpdate = true;
      }
    }
  });
}

function animate3D() {
  if (!state.three.renderer || !state.three.scene || !state.three.camera) return;
  
  requestAnimationFrame(animate3D);
  
  // Update controls if they exist
  if (state.three.controls && state.three.controls.update) {
    state.three.controls.update();
  }
  
  state.three.renderer.render(state.three.scene, state.three.camera);
}

function onMouse3DMove(event) {
  if (!state.three.camera) return;
  
  const rect = event.target.getBoundingClientRect();
  state.three.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  state.three.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  
  state.three.raycaster.setFromCamera(state.three.mouse, state.three.camera);
  const intersects = state.three.raycaster.intersectObjects(
    state.three.nodes.map(n => n.mesh)
  );
  
  // Reset all node highlights
  state.three.nodes.forEach(nodeObj => {
    const material = nodeObj.mesh.material;
    material.emissiveIntensity = nodeObj.mesh.userData.originalEmissive;
    nodeObj.mesh.scale.setScalar(nodeObj.mesh.userData.originalScale);
  });
  
  if (intersects.length > 0) {
    const intersectedMesh = intersects[0].object;
    const node = intersectedMesh.userData.data;
    
    // Highlight hovered node
    intersectedMesh.material.emissiveIntensity = 0.5;
    intersectedMesh.scale.setScalar(intersectedMesh.userData.originalScale * 1.2);
    
    // Show tooltip
    const pos = { x: event.clientX, y: event.clientY };
    showTip(node.title, node.preview, pos);
  } else {
    hideTip();
  }
}

function onMouse3DClick(event) {
  if (!state.three.camera) return;
  
  state.three.raycaster.setFromCamera(state.three.mouse, state.three.camera);
  const intersects = state.three.raycaster.intersectObjects(
    state.three.nodes.map(n => n.mesh)
  );
  
  if (intersects.length > 0) {
    const node = intersects[0].object.userData.data;
    const nodeType = intersects[0].object.userData.nodeType;
    
    // Show detailed node information
    const typeEmoji = {
      note: '📝',
      concept: '💡', 
      topic: '🏷️',
      important: '⭐'
    };
    
    alert(`${typeEmoji[nodeType]} ${node.title}\n\n${node.preview || 'No preview available'}\n\n🔗 Connections: ${node.degree || 0}\n📁 Type: ${nodeType.charAt(0).toUpperCase() + nodeType.slice(1)}`);
  }
}

function onMouse3DDoubleClick(event) {
  if (!state.three.camera) return;
  
  state.three.raycaster.setFromCamera(state.three.mouse, state.three.camera);
  const intersects = state.three.raycaster.intersectObjects(
    state.three.nodes.map(n => n.mesh)
  );
  
  if (intersects.length > 0) {
    // Focus camera on the double-clicked node
    const targetPosition = intersects[0].object.position.clone();
    const direction = targetPosition.clone().sub(state.three.camera.position).normalize();
    const distance = 100;
    const newPosition = targetPosition.clone().sub(direction.multiplyScalar(distance));
    
    // Smooth camera transition
    animateCameraTo(newPosition, targetPosition);
  }
}

function animateCameraTo(position, target) {
  const startPos = state.three.camera.position.clone();
  const startTarget = state.three.controls.target.clone();
  let progress = 0;
  
  const animate = () => {
    progress += 0.05;
    if (progress >= 1) {
      state.three.camera.position.copy(position);
      state.three.controls.target.copy(target);
      state.three.controls.update();
      return;
    }
    
    state.three.camera.position.lerpVectors(startPos, position, progress);
    state.three.controls.target.lerpVectors(startTarget, target, progress);
    state.three.controls.update();
    
    requestAnimationFrame(animate);
  };
  
  animate();
}

function onResize3D() {
  if (!state.three.camera || !state.three.renderer) return;
  
  const container = document.getElementById('threeContainer');
  const rect = container.getBoundingClientRect();
  
  state.three.camera.aspect = rect.width / rect.height;
  state.three.camera.updateProjectionMatrix();
  state.three.renderer.setSize(rect.width, rect.height);
}

function toggle3DMode() {
  state.is3D = document.getElementById('toggle3D').checked;
  console.log('Toggling 3D mode:', state.is3D);
  
  if (state.is3D) {
    document.getElementById('cy').style.display = 'none';
    document.getElementById('threeContainer').style.display = 'block';
    
    if (!state.three.scene) {
      console.log('Initializing 3D scene...');
      const success = init3D();
      if (!success) {
        console.error('Failed to initialize 3D scene');
        // Fallback to 2D
        document.getElementById('toggle3D').checked = false;
        state.is3D = false;
        document.getElementById('cy').style.display = 'block';
        document.getElementById('threeContainer').style.display = 'none';
        alert('3D visualization failed to load. Using 2D mode.');
        return;
      }
    }
    
    if (state.mapData.nodes && state.mapData.nodes.length > 0) {
      console.log('Rendering 3D map with', state.mapData.nodes.length, 'nodes');
      render3DMap(state.mapData.nodes, state.mapData.edges);
    } else {
      console.log('No data to render in 3D mode');
    }
  } else {
    document.getElementById('cy').style.display = 'block';
    document.getElementById('threeContainer').style.display = 'none';
  }
}

// Add 3D toggle event listener
document.getElementById('toggle3D').addEventListener('change', toggle3DMode);

// Enhanced Bulk Import for Apple Notes and other formats
function parseNotesText(text, filename = '') {
  const notes = [];
  
  // Detect format based on content and filename
  const format = detectFileFormat(text, filename);
  
  switch (format) {
    case 'apple_notes':
      return parseAppleNotesFormat(text);
    case 'markdown':
      return parseMarkdownFormat(text);
    case 'json':
      return parseJSONFormat(text);
    case 'csv':
      return parseCSVFormat(text);
    default:
      return parseGenericTextFormat(text);
  }
}

function detectFileFormat(text, filename) {
  const extension = filename.toLowerCase().split('.').pop();
  
  // Check by file extension first
  if (extension === 'json') return 'json';
  if (extension === 'csv') return 'csv';
  if (extension === 'md' || extension === 'markdown') return 'markdown';
  
  // Check by content patterns
  if (text.includes('Note created:') || text.includes('Apple Notes')) return 'apple_notes';
  if (text.startsWith('[') && text.endsWith(']')) return 'json';
  if (text.includes('\t') || (text.split('\n')[0] || '').includes(',')) return 'csv';
  if (text.includes('# ') || text.includes('## ')) return 'markdown';
  
  return 'generic';
}

function parseAppleNotesFormat(text) {
  const notes = [];
  
  // Apple Notes export patterns
  const applePatterns = [
    // Pattern 1: Note title followed by content
    /^(.+?)\n(Created: .+?\n)?((?:(?!^.+\nCreated:).|\n)*)/gm,
    // Pattern 2: Title with creation date
    /^(.+?)\n(?:Created: .+?\n)?([\s\S]*?)(?=\n\n.+?\n(?:Created:|$))/gm,
    // Pattern 3: Simple title-content pairs
    /^(.+?)\n([\s\S]*?)(?=\n{2,}.+|$)/gm
  ];
  
  for (const pattern of applePatterns) {
    const matches = [...text.matchAll(pattern)];
    if (matches.length > 0) {
      matches.forEach(match => {
        const title = match[1].trim();
        let content = (match[3] || match[2] || '').trim();
        
        // Skip if title looks like metadata
        if (title.includes('Created:') || title.includes('Modified:')) return;
        
        // Clean up content
        content = content
          .replace(/^Created: .+?\n/gm, '')
          .replace(/^Modified: .+?\n/gm, '')
          .replace(/\n{3,}/g, '\n\n')
          .trim();
        
        if (title && title.length > 0 && title.length < 200) {
          notes.push({
            title: cleanTitle(title),
            content: content || title
          });
        }
      });
      
      if (notes.length > 0) break; // Use first successful pattern
    }
  }
  
  // Fallback to generic parsing if no Apple Notes pattern worked
  if (notes.length === 0) {
    return parseGenericTextFormat(text);
  }
  
  return notes;
}

function parseMarkdownFormat(text) {
  const notes = [];
  
  // Split by H1 or H2 headers
  const sections = text.split(/^#{1,2}\s+/gm);
  
  for (let i = 1; i < sections.length; i++) {
    const section = sections[i];
    const lines = section.split('\n');
    const title = lines[0].trim();
    const content = lines.slice(1).join('\n').trim();
    
    if (title) {
      notes.push({
        title: cleanTitle(title),
        content: content || title
      });
    }
  }
  
  return notes.length > 0 ? notes : parseGenericTextFormat(text);
}

function parseJSONFormat(text) {
  try {
    const data = JSON.parse(text);
    const notes = [];
    
    if (Array.isArray(data)) {
      data.forEach(item => {
        if (typeof item === 'object' && item.title) {
          notes.push({
            title: cleanTitle(item.title),
            content: item.content || item.body || item.text || item.title
          });
        } else if (typeof item === 'string') {
          const title = generateTitleFromContent(item);
          notes.push({ title, content: item });
        }
      });
    } else if (typeof data === 'object') {
      Object.entries(data).forEach(([key, value]) => {
        notes.push({
          title: cleanTitle(key),
          content: typeof value === 'string' ? value : JSON.stringify(value)
        });
      });
    }
    
    return notes;
  } catch (e) {
    console.warn('Failed to parse as JSON, falling back to text:', e);
    return parseGenericTextFormat(text);
  }
}

function parseCSVFormat(text) {
  const notes = [];
  const lines = text.split('\n').filter(line => line.trim());
  
  if (lines.length < 2) return parseGenericTextFormat(text);
  
  const headers = lines[0].split(/[,\t]/).map(h => h.trim().toLowerCase());
  const titleCol = headers.findIndex(h => h.includes('title') || h.includes('name') || h.includes('subject'));
  const contentCol = headers.findIndex(h => h.includes('content') || h.includes('body') || h.includes('text') || h.includes('note'));
  
  for (let i = 1; i < lines.length; i++) {
    const cols = lines[i].split(/[,\t]/);
    const title = titleCol >= 0 ? cols[titleCol]?.trim() : '';
    const content = contentCol >= 0 ? cols[contentCol]?.trim() : '';
    
    if (title || content) {
      notes.push({
        title: cleanTitle(title) || generateTitleFromContent(content),
        content: content || title
      });
    }
  }
  
  return notes.length > 0 ? notes : parseGenericTextFormat(text);
}

function parseGenericTextFormat(text) {
  // Enhanced generic parser with multiple splitting strategies
  const strategies = [
    // Strategy 1: Triple newlines or dashes
    () => text.split(/\n\s*---+\s*\n|\n\s*\n\s*\n/),
    // Strategy 2: Double newlines
    () => text.split(/\n\s*\n/),
    // Strategy 3: Numbered lists
    () => text.split(/\n\d+\.\s+/),
    // Strategy 4: Bullet points
    () => text.split(/\n[-*•]\s+/),
    // Strategy 5: Empty lines followed by text
    () => text.split(/\n\s*\n(?=\S)/)
  ];
  
  let bestNotes = [];
  let maxNotes = 0;
  
  for (const strategy of strategies) {
    const parts = strategy();
    const candidateNotes = [];
    
    parts.forEach(part => {
      const trimmed = part.trim();
      if (!trimmed || trimmed.length < 5) return;
      
      const lines = trimmed.split('\n');
      let title = lines[0].trim();
      let content = lines.slice(1).join('\n').trim();
      
      // If first line is too long or looks like content, generate title
      if (title.length > 100 || (title.includes('.') && lines.length > 1)) {
        title = generateTitleFromContent(trimmed);
        content = trimmed;
      }
      
      // If content is too short, use title as content
      if (content.length < 10) {
        content = title;
        title = generateTitleFromContent(content);
      }
      
      candidateNotes.push({
        title: cleanTitle(title) || 'Untitled',
        content: content || title
      });
    });
    
    if (candidateNotes.length > maxNotes) {
      maxNotes = candidateNotes.length;
      bestNotes = candidateNotes;
    }
  }
  
  return bestNotes;
}

function cleanTitle(title) {
  if (!title) return '';
  
  return title
    .replace(/^#+\s*/, '') // Remove markdown headers
    .replace(/^\d+\.\s*/, '') // Remove numbered list markers
    .replace(/^[-*•]\s*/, '') // Remove bullet points
    .replace(/\s+/g, ' ') // Normalize whitespace
    .trim()
    .substring(0, 100); // Limit length
}

function generateTitleFromContent(content) {
  if (!content) return 'Untitled';
  
  // Try to extract meaningful title
  const sentences = content.split(/[.!?]/);
  const firstSentence = sentences[0].trim();
  
  if (firstSentence && firstSentence.length <= 60 && firstSentence.length > 5) {
    return firstSentence;
  }
  
  // Fallback to first line or truncated content
  const firstLine = content.split('\n')[0].trim();
  if (firstLine.length <= 60) {
    return firstLine;
  }
  
  return content.substring(0, 50).trim() + '...';
}

async function handleBulkImport() {
  try {
    let notesToImport = [];
    
    // Handle file upload
    const files = document.getElementById('bulkImport').files;
    if (files.length > 0) {
      for (const file of files) {
        try {
          const text = await readFileAsText(file);
          const notes = parseNotesText(text, file.name);
          notesToImport.push(...notes);
        } catch (e) {
          console.error('Failed to process file:', file.name, e);
          alert(`Failed to process file: ${file.name}`);
        }
      }
    }

    // Handle text area content
    const bulkTextValue = document.getElementById('bulkText').value.trim();
    if (bulkTextValue) {
      const notes = parseNotesText(bulkTextValue);
      notesToImport.push(...notes);
    }

    if (notesToImport.length === 0) {
      alert('Please select files or enter text to import');
      return;
    }

    // Show preview and confirmation
    const confirmed = confirm(
      `Ready to import ${notesToImport.length} notes?\n\n` +
      `Preview of first few notes:\n` +
      notesToImport.slice(0, 3).map(n => `• ${n.title.substring(0, 50)}...`).join('\n') +
      (notesToImport.length > 3 ? `\n... and ${notesToImport.length - 3} more` : '')
    );
    
    if (!confirmed) return;

    // Import with progress tracking
    let successful = 0;
    let failed = 0;
    const batchSize = 5;
    
    // Show progress
    const progressDiv = document.createElement('div');
    progressDiv.className = 'import-progress';
    progressDiv.innerHTML = `
      <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                  background: rgba(0,0,0,0.9); color: white; padding: 20px; border-radius: 8px; z-index: 1000;">
        <div>Importing notes...</div>
        <div id="importProgress">0 / ${notesToImport.length}</div>
      </div>
    `;
    document.body.appendChild(progressDiv);

    // Import in batches to avoid overwhelming the server
    for (let i = 0; i < notesToImport.length; i += batchSize) {
      const batch = notesToImport.slice(i, i + batchSize);
      
      await Promise.all(
        batch.map(async (note) => {
          try {
            await apiFetch('/notes/', { 
              method: 'POST', 
              body: JSON.stringify(note) 
            });
            successful++;
          } catch (e) {
            console.error('Failed to import note:', note.title, e);
            failed++;
          }
          
          // Update progress
          document.getElementById('importProgress').textContent = 
            `${successful + failed} / ${notesToImport.length}`;
        })
      );
      
      // Small delay between batches
      if (i + batchSize < notesToImport.length) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }

    // Clean up
    progressDiv.remove();
    document.getElementById('bulkImport').value = '';
    document.getElementById('bulkText').value = '';
    
    // Refresh map
    await refreshMap();
    
    // Show results
    const message = `Import complete!\n✅ ${successful} notes imported successfully` + 
                   (failed > 0 ? `\n❌ ${failed} notes failed to import` : '');
    alert(message);

  } catch (e) {
    console.error('Import failed:', e);
    alert('Import failed: ' + e.message);
  }
}

function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = e => resolve(e.target.result);
    reader.onerror = e => reject(new Error('Failed to read file: ' + file.name));
    reader.readAsText(file, 'UTF-8');
  });
}

// Load & render map
// Add global layout state
let currentLayout = 'force'; // 'force', 'tree', 'radial'

function toggleLayout() {
  try {
    const layouts = ['force', 'tree', 'radial'];
    const currentIndex = layouts.indexOf(currentLayout);
    currentLayout = layouts[(currentIndex + 1) % layouts.length];
    
    const button = document.getElementById('btnToggleLayout');
    if (button) {
      button.textContent = `${currentLayout.charAt(0).toUpperCase() + currentLayout.slice(1)} Layout`;
    }
    
    if (notifications) {
      notifications.show(`Switched to ${currentLayout} layout`, 'info');
    }
    
    // Add small delay to prevent rapid switching
    setTimeout(() => {
      refreshMap();
    }, 100);
  } catch (error) {
    console.error('Error toggling layout:', error);
    if (notifications) {
      notifications.show('Layout change failed - please try again', 'error');
    }
  }
}

function createTreeLayout(nodes, edges) {
  // Calculate node degrees (connection counts)
  const nodeDegrees = {};
  nodes.forEach(node => nodeDegrees[node.id] = 0);
  edges.forEach(edge => {
    nodeDegrees[edge.source]++;
    nodeDegrees[edge.target]++;
  });
  
  // Sort nodes by degree (most connected first)
  const sortedNodes = [...nodes].sort((a, b) => nodeDegrees[b.id] - nodeDegrees[a.id]);
  
  // Find the most connected node as root
  const rootNode = sortedNodes[0];
  
  const positions = {};
  const visited = new Set();
  const levels = {};
  
  // Build adjacency list
  const adjacency = {};
  nodes.forEach(node => adjacency[node.id] = []);
  edges.forEach(edge => {
    adjacency[edge.source].push(edge.target);
    adjacency[edge.target].push(edge.source);
  });
  
  // BFS to assign levels starting from most connected node
  const queue = [{nodeId: rootNode.id, level: 0, parentId: null}];
  levels[0] = [];
  
  while (queue.length > 0) {
    const {nodeId, level, parentId} = queue.shift();
    if (visited.has(nodeId)) continue;
    
    visited.add(nodeId);
    if (!levels[level]) levels[level] = [];
    levels[level].push(nodeId);
    
    // Add children to next level, sorted by their degree
    const children = adjacency[nodeId]
      .filter(childId => !visited.has(childId))
      .sort((a, b) => nodeDegrees[b] - nodeDegrees[a]); // Most connected children first
    
    children.forEach(childId => {
      queue.push({nodeId: childId, level: level + 1, parentId: nodeId});
    });
  }
  
  // Add any remaining unconnected nodes to the last level
  const unvisited = nodes.filter(node => !visited.has(node.id));
  if (unvisited.length > 0) {
    const lastLevel = Math.max(...Object.keys(levels).map(Number)) + 1;
    levels[lastLevel] = unvisited.map(node => node.id);
  }
  
  // Position nodes in tree structure - CENTER EVERYTHING
  const verticalSpacing = 120;
  const baseWidth = Math.min(800, Math.max(300, nodes.length * 50)); // Dynamic width
  const totalLevels = Object.keys(levels).length;
  const centerY = 0; // Center vertically
  
  Object.keys(levels).forEach(levelStr => {
    const level = parseInt(levelStr);
    const nodeIds = levels[level];
    const nodesAtLevel = nodeIds.length;
    
    // Calculate Y position centered around 0
    const yPos = centerY + (level - totalLevels / 2) * verticalSpacing;
    
    if (nodesAtLevel === 1) {
      // Center single nodes (especially root)
      positions[nodeIds[0]] = {
        x: 0,
        y: yPos,
        z: 0
      };
    } else {
      // Distribute multiple nodes horizontally, centered around 0
      const totalWidth = (nodesAtLevel - 1) * (baseWidth / nodesAtLevel);
      const startX = -totalWidth / 2;
      
      nodeIds.forEach((nodeId, index) => {
        positions[nodeId] = {
          x: startX + (index * (totalWidth / (nodesAtLevel - 1))),
          y: yPos,
          z: (Math.random() - 0.5) * 30 // Small Z variation
        };
      });
    }
  });
  
  return positions;
}

function createRadialLayout(nodes, edges) {
  const positions = {};
  
  // Find most connected node as center
  const nodeDegrees = {};
  nodes.forEach(node => nodeDegrees[node.id] = 0);
  edges.forEach(edge => {
    nodeDegrees[edge.source]++;
    nodeDegrees[edge.target]++;
  });
  
  const centerNode = nodes.reduce((max, node) => 
    nodeDegrees[node.id] > nodeDegrees[max.id] ? node : max
  );
  
  // Place center node at origin (0,0,0)
  positions[centerNode.id] = {x: 0, y: 0, z: 0};
  
  // Place other nodes in concentric circles centered at origin
  const remaining = nodes.filter(n => n.id !== centerNode.id);
  
  // Sort remaining nodes by degree for better radial distribution
  remaining.sort((a, b) => nodeDegrees[b.id] - nodeDegrees[a.id]);
  
  const baseRadius = 150;
  const maxLayers = Math.ceil(remaining.length / 8); // 8 nodes per layer max
  
  let nodeIndex = 0;
  for (let layer = 1; layer <= maxLayers; layer++) {
    const nodesInThisLayer = Math.min(8, remaining.length - nodeIndex);
    const angleStep = (2 * Math.PI) / nodesInThisLayer;
    const layerRadius = baseRadius * layer;
    
    for (let i = 0; i < nodesInThisLayer; i++) {
      if (nodeIndex >= remaining.length) break;
      
      const angle = i * angleStep;
      const node = remaining[nodeIndex++];
      
      positions[node.id] = {
        x: Math.cos(angle) * layerRadius,
        y: Math.sin(angle) * layerRadius,
        z: (Math.random() - 0.5) * 60 // More Z variation for depth
      };
    }
  }
  
  return positions;
}

async function refreshMap() {
  try {
    if (!state.token) {
      console.warn('No authentication token');
      return;
    }

    const params = new URLSearchParams({
      min_similarity: document.getElementById('minSim').value,
      top_k: document.getElementById('topK').value,
      max_nodes: document.getElementById('maxNodes').value,
      include_isolates: String(document.getElementById('includeIsolates').checked)
    });

    const data = await apiFetch('/map/?' + params.toString());
    state.mapData = { nodes: data.nodes || [], edges: data.edges || [] };

    if (state.is3D) {
      // Render in 3D mode
      if (!state.three.scene) {
        init3D();
      }
      render3DMap(state.mapData.nodes, state.mapData.edges);
    } else {
      // Render in 2D mode
      initCytoscape();
      const elements = [];
      
      state.mapData.nodes.forEach(n => {
        elements.push({ 
          data: { 
            id: n.id, 
            label: n.label || n.title, 
            title: n.title, 
            preview: n.preview, 
            degree: n.degree 
          } 
        });
      });
      
      state.mapData.edges.forEach(e => {
        elements.push({ 
          data: { 
            id: e.source + '_' + e.target, 
            source: e.source, 
            target: e.target, 
            weight: e.weight 
          } 
        });
      });
      
      state.cy.add(elements);
      state.cy.layout({ name: 'cose', animate: 'end', fit: true, padding: 40 }).run();
    }
    
  } catch (e) {
    console.error('Failed to refresh map:', e);
    notifications.showError('Failed to load neural map: ' + e.message);
  }
}

// Search
document.getElementById('btnSearch').addEventListener('click', async () => {
  try {
    const q = document.getElementById('searchQuery').value.trim();
    if (!q) return;
    
    const res = await apiFetch('/search', { 
      method: 'POST', 
      body: JSON.stringify({ query: q }) 
    });
    
    renderSearch(res);
  } catch (e) { 
    alert('Search failed: ' + e.message); 
  }
});

function renderSearch(payload) {
  const searchResults = document.getElementById('searchResults');
  searchResults.innerHTML = '';

  const results = Array.isArray(payload)
    ? payload
    : Array.isArray(payload?.results)
      ? payload.results
      : [];

  if (payload && typeof payload === 'object' && payload.message) {
    notifications.showInfo(payload.message, 6000);
  }

  results.forEach((r) => {
    const div = document.createElement('div');
    div.className = 'item';
    div.innerHTML =
      '<div><strong>' + escapeHtml(r.title || '(untitled)') + '</strong></div>' +
      '<div class="muted">' + escapeHtml((r.content || '').slice(0, 140)) + '</div>' +
      '<div class="muted">score: ' + Number(r.score ?? 0).toFixed(3) + '</div>';
    searchResults.appendChild(div);
  });
}

// Create Note
document.getElementById('btnCreateNote').addEventListener('click', async () => {
  try {
    const title = document.getElementById('noteTitle').value.trim();
    const content = document.getElementById('noteContent').value.trim();
    
    if (!title || !content) { 
      alert('Title and content required'); 
      return; 
    }
    
    await apiFetch('/notes/', { 
      method: 'POST', 
      body: JSON.stringify({ title, content }) 
    });
    
    document.getElementById('noteTitle').value = ''; 
    document.getElementById('noteContent').value = '';
    await refreshMap();
    alert('Note created!');
  } catch (e) { 
    alert('Create failed: ' + e.message); 
  }
});

// Event Listeners
document.getElementById('btnRefresh').addEventListener('click', refreshMap);
document.getElementById('btnToggleLayout').addEventListener('click', toggleLayout);
document.getElementById('autoRotate3D').addEventListener('change', (e) => {
  if (state.three.controls && state.three.controls.autoRotate !== undefined) {
    state.three.controls.autoRotate = e.target.checked;
  }
});
document.getElementById('btnBulkImport').addEventListener('click', handleBulkImport);

// Initial load
window.addEventListener('load', () => {
  if (state.token) document.getElementById('authStatus').textContent = 'Authenticated';
  document.getElementById('simVal').textContent = (+document.getElementById('minSim').value).toFixed(2);
  document.getElementById('kVal').textContent = document.getElementById('topK').value;
  document.getElementById('maxNodesVal').textContent = document.getElementById('maxNodes').value;

  // Check authentication and redirect if needed
  if (!state.token) {
    window.location.href = './auth.html';
    return;
  }

  refreshMap();
});
