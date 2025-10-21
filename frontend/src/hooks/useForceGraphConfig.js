import { useMemo } from 'react'

/**
 * Shared configuration hook for both 2D and 3D force graphs
 * @param {Object} options - Configuration options
 * @returns {Object} Force graph configuration
 */
export function useForceGraphConfig({ 
  prefersReducedMotion = false,
  cooldownTime = 1000,
  particleSpeed = 0.001 
} = {}) {
  
  const config = useMemo(() => ({
    // Force simulation parameters - optimized for collision avoidance
    d3AlphaDecay: 0.015,
    d3VelocityDecay: 0.35,
    warmupTicks: 150,
    cooldownTime: cooldownTime,
    cooldownTicks: Infinity,
    
    // Link forces - balanced for spacing
    linkDistance: (link) => {
      const baseDistance = 180
      const similarity = link.similarity || link.weight || 0.5
      return baseDistance * (1 - similarity * 0.4)
    },
    linkStrength: (link) => {
      const similarity = link.similarity || link.weight || 0.5
      return similarity * 0.5
    },
    
    // Strong charge forces to prevent overlap
    chargeStrength: -800,
    chargeDistance: 600,
    
    // Enhanced collision detection for all modes
    d3Force: (simulation) => {
      // Collision force - prevents node overlap
      const collisionForce = window.d3?.forceCollide?.()
        .radius((node) => {
          const degree = node.degree || 0
          const baseSize = 5 + Math.min(degree * 0.3, 8)
          // Larger radius to account for labels
          return baseSize + 35
        })
        .strength(1.5)
        .iterations(3) // Multiple iterations for better collision resolution
      
      // Charge force - strong repulsion
      const chargeForce = window.d3?.forceManyBody?.()
        .strength(-800)
        .distanceMax(600)
        .distanceMin(30)
      
      // Center force - keeps graph centered
      const centerForce = window.d3?.forceCenter?.()
        .strength(0.05)
      
      if (collisionForce) simulation.force('collision', collisionForce)
      if (chargeForce) simulation.force('charge', chargeForce)
      if (centerForce) simulation.force('center', centerForce)
    },
    
    // Interaction settings
    enableNodeDrag: true,
    enableNavigationControls: true,
    enablePointerInteraction: true,
    
    // Animation settings
    animationSpeed: prefersReducedMotion ? 0 : particleSpeed,
    showNavInfo: false,
    
    // Camera settings
    cameraPosition: { x: 0, y: 0, z: 400 },
    
  }), [prefersReducedMotion, cooldownTime, particleSpeed])
  
  return config
}

/**
 * Get node appearance based on type and similarity
 * @param {Object} node - Node data
 * @param {boolean} isSelected - Whether node is selected
 * @param {string} theme - Current theme ('light' or 'dark')
 * @returns {Object} Appearance properties
 */
export function getNodeAppearance(node, isSelected = false, theme = 'dark') {
  const baseSize = node.size || 10
  const scaleFactor = isSelected ? 1.5 : 1
  
  return {
    size: baseSize * scaleFactor,
    color: node.color || getNodeColor(node.type),
    glowIntensity: isSelected ? 0.8 : (theme === 'light' ? 0.4 : 0.3),
    opacity: node.degree === 0 ? 0.5 : 1.0
  }
}

/**
 * Get default color for node type
 * @param {string} type - Node type
 * @returns {string} Hex color
 */
export function getNodeColor(type) {
  const colorMap = {
    idea: '#F24D80',      // Primary brand color
    technology: '#A855F7', // Secondary brand color
    detailed: '#FF8F3C',   // Accent color
    note: '#8B5CF6',       // Purple variant
  }
  return colorMap[type] || '#8B5CF6'
}

/**
 * Get edge appearance based on similarity
 * @param {Object} link - Link data
 * @param {boolean} isHighlighted - Whether edge is highlighted
 * @returns {Object} Appearance properties
 */
export function getEdgeAppearance(link, isHighlighted = false) {
  const similarity = link.similarity || link.weight || 0.5
  const baseWidth = isHighlighted ? 4 : 2
  const width = baseWidth * (0.5 + similarity * 0.5)
  
  return {
    width: width,
    opacity: isHighlighted ? 0.9 : similarity * 0.7,
    color: isHighlighted 
      ? `rgba(242, 77, 128, ${similarity})` 
      : `rgba(139, 92, 246, ${similarity * 0.6})`,
    particleWidth: width * 0.8,
    particles: isHighlighted ? 2 : 0
  }
}

/**
 * Check if user prefers reduced motion
 * @returns {boolean}
 */
export function checkPrefersReducedMotion() {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}
