import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Network, Settings, RefreshCw, Eye, EyeOff,
  Box, Grid3x3, Tag, X, Info
} from 'lucide-react'
import ForceGraph3D from 'react-force-graph-3d'
import ForceGraph2D from 'react-force-graph-2d'
import * as THREE from 'three'
import api from '../utils/api'
import toast from 'react-hot-toast'
import OctopusLoader from '../components/OctopusLoader'
import { useTheme } from '../hooks/useTheme'
import {
  useForceGraphConfig,
  checkPrefersReducedMotion
} from '../hooks/useForceGraphConfig'

export default function NeuralMapPage() {
  const { theme } = useTheme()
  const [graphData, setGraphData] = useState({ nodes: [], links: [] })
  const [loading, setLoading] = useState(true)
  const [showControls, setShowControls] = useState(false)
  const [viewMode, setViewMode] = useState('3d')
  const [layoutMode, setLayoutMode] = useState('force') // force, tree, radial, planetary
  const [selectedNode, setSelectedNode] = useState(null)
  const [hoverNode, setHoverNode] = useState(null)
  const [highlightNodes, setHighlightNodes] = useState(new Set())
  const [highlightLinks, setHighlightLinks] = useState(new Set())
  const [availableTags, setAvailableTags] = useState([])
  const [selectedTags, setSelectedTags] = useState([])
  const [stats, setStats] = useState(null)

  const [settings, setSettings] = useState({
    minSimilarity: 0.20,
    topK: 3,
    maxNodes: 200,
    includeIsolates: true
  })

  const fgRef = useRef()
  const abortControllerRef = useRef(null)
  const keyboardControlsRef = useRef({ forward: 0, right: 0, up: 0 })
  const animationFrameRef = useRef(null)
  const layoutAppliedRef = useRef(false)
  const prefersReducedMotion = checkPrefersReducedMotion()
  const forceConfig = useForceGraphConfig({ prefersReducedMotion })

  // Get node color based on connection count (degree)
  const getNodeColorByDegree = useCallback((degree, isHovered, isSelected) => {
    if (isHovered || isSelected) {
      return '#FFD700' // Golden for hover/selected
    }
    
    // Color scale based on connections
    if (degree === 0) return '#666666' // Gray for isolated
    if (degree <= 2) return '#8B5CF6' // Purple - few connections
    if (degree <= 5) return '#A855F7' // Light purple
    if (degree <= 10) return '#F24D80' // Pink - moderate connections
    if (degree <= 15) return '#FF8F3C' // Orange
    return '#FFD700' // Gold - hub nodes (many connections)
  }, [])

  // Apply custom layouts (tree, radial, planetary)
  const applyCustomLayout = useCallback((graph, mode, is3d) => {
    if (!graph || mode === 'force') return

    // Get current graph data - use the state directly instead of graph.graphData()
    const currentData = graph.graphData ? graph.graphData() : graphData
    const nodes = currentData.nodes
    const links = currentData.links

    if (!nodes || nodes.length === 0) {
      toast.error('No nodes available for layout')
      return
    }

    if (mode === 'tree') {
      // Hierarchical tree layout
      const levels = new Map()
      const visited = new Set()
      const nodesByLevel = []

      // Find root nodes (nodes with most connections or no parents)
      const roots = nodes
        .filter(n => n.degree > 0)
        .sort((a, b) => (b.degree || 0) - (a.degree || 0))
        .slice(0, Math.max(1, Math.ceil(nodes.length * 0.1))) // Top 10% as roots

      // BFS to assign levels
      const queue = roots.map(n => ({ node: n, level: 0 }))
      roots.forEach(n => visited.add(n.id))

      while (queue.length > 0) {
        const { node, level } = queue.shift()
        
        if (!nodesByLevel[level]) nodesByLevel[level] = []
        nodesByLevel[level].push(node)
        levels.set(node.id, level)

        // Find connected nodes
        links.forEach(link => {
          const sourceId = typeof link.source === 'object' ? link.source.id : link.source
          const targetId = typeof link.target === 'object' ? link.target.id : link.target
          
          if (sourceId === node.id && !visited.has(targetId)) {
            const target = nodes.find(n => n.id === targetId)
            if (target) {
              visited.add(targetId)
              queue.push({ node: target, level: level + 1 })
            }
          } else if (targetId === node.id && !visited.has(sourceId)) {
            const source = nodes.find(n => n.id === sourceId)
            if (source) {
              visited.add(sourceId)
              queue.push({ node: source, level: level + 1 })
            }
          }
        })
      }

      // Add unvisited nodes to the end
      nodes.forEach(node => {
        if (!visited.has(node.id)) {
          const lastLevel = nodesByLevel.length
          if (!nodesByLevel[lastLevel]) nodesByLevel[lastLevel] = []
          nodesByLevel[lastLevel].push(node)
          levels.set(node.id, lastLevel)
        }
      })

      // Position nodes in tree structure with MAXIMUM spacing to prevent overlap
      const levelSpacing = is3d ? 350 : 280  // Huge vertical spacing (40% increase)
      const nodeSpacing = is3d ? 220 : 180   // Huge horizontal spacing (47% increase)

      nodesByLevel.forEach((levelNodes, level) => {
        levelNodes.forEach((node, i) => {
          // Add significant randomness to prevent any alignment overlap
          const jitter = (Math.random() - 0.5) * 40
          const x = (i - (levelNodes.length - 1) / 2) * nodeSpacing + jitter
          const y = level * levelSpacing
          
          if (is3d) {
            node.fx = x
            node.fy = y
            node.fz = (Math.random() - 0.5) * 80  // More Z variation for depth
          } else {
            node.fx = x
            node.fy = y
          }
        })
      })

    } else if (mode === 'radial') {
      // Improved radial layout with collision detection
      const centerNode = nodes.reduce((max, node) => 
        (node.degree || 0) > (max.degree || 0) ? node : max
      , nodes[0])

      // Position center node
      centerNode.fx = 0
      centerNode.fy = 0
      if (is3d) centerNode.fz = 0

      // Group nodes by degree for rings
      const rings = []
      const maxDegree = Math.max(...nodes.map(n => n.degree || 0))
      const numRings = Math.min(5, Math.ceil(maxDegree / 3)) // Up to 5 rings

      nodes.forEach(node => {
        if (node.id === centerNode.id) return
        
        const degree = node.degree || 0
        const ringIndex = Math.min(numRings - 1, Math.floor(degree / (maxDegree / numRings + 1)))
        if (!rings[ringIndex]) rings[ringIndex] = []
        rings[ringIndex].push(node)
      })

      // Position nodes in rings with MAXIMUM spacing to prevent overlap
      rings.forEach((ringNodes, ringIndex) => {
        // Massive radius increments for maximum separation
        const radius = (ringIndex + 1) * (is3d ? 260 : 210)  // 44% increase
        const nodesInRing = ringNodes.length
        const angleStep = (2 * Math.PI) / nodesInRing
        
        // Ensure minimum distance between nodes on ring
        const minDistanceBetweenNodes = is3d ? 150 : 120  // 50% increase in minimum spacing
        const circumference = 2 * Math.PI * radius
        const actualDistance = circumference / nodesInRing
        
        // If nodes would be too close, increase radius for this ring
        const adjustedRadius = actualDistance < minDistanceBetweenNodes 
          ? (minDistanceBetweenNodes * nodesInRing) / (2 * Math.PI)
          : radius

        ringNodes.forEach((node, i) => {
          const angle = i * angleStep
          // Add more random offset to prevent perfect alignment
          const radiusJitter = (Math.random() - 0.5) * 40
          const angleJitter = (Math.random() - 0.5) * 0.15
          
          const x = (adjustedRadius + radiusJitter) * Math.cos(angle + angleJitter)
          const y = (adjustedRadius + radiusJitter) * Math.sin(angle + angleJitter)

          if (is3d) {
            // Spiral in 3D with much more dramatic Z variation
            const z = (ringIndex - rings.length / 2) * 120  // 50% increase
            node.fx = x
            node.fy = y
            node.fz = z
          } else {
            node.fx = x
            node.fy = y
          }
        })
      })

    } else if (mode === 'planetary') {
      // Planetary system layout (3D spiral)
      const sorted = [...nodes].sort((a, b) => (b.degree || 0) - (a.degree || 0))
      
      sorted.forEach((node, i) => {
        const radius = Math.sqrt(i + 1) * (is3d ? 50 : 40)
        const angle = i * 2.4 // Golden angle for even distribution
        const x = radius * Math.cos(angle)
        const y = radius * Math.sin(angle)

        if (is3d) {
          // Spiral upward in 3D
          const z = (i - sorted.length / 2) * 30
          node.fx = x
          node.fy = y
          node.fz = z
        } else {
          node.fx = x
          node.fy = y
        }
      })
    }

    // Trigger re-render
    if (graph.refresh) {
      graph.refresh()
    }

    // Release fixed positions after a delay to allow force simulation
    setTimeout(() => {
      nodes.forEach(node => {
        node.fx = undefined
        node.fy = undefined
        if (is3d) node.fz = undefined
      })
      layoutAppliedRef.current = false
      if (graph.refresh) {
        graph.refresh()
      }
    }, 3000)

  }, [graphData])

  // Apply layout when layout mode or view mode changes
  useEffect(() => {
    if (fgRef.current && graphData.nodes.length > 0 && layoutMode !== 'force') {
      layoutAppliedRef.current = true
      // Wait for graph to initialize
      const timer = setTimeout(() => {
        try {
          applyCustomLayout(fgRef.current, layoutMode, viewMode === '3d')
          toast.success(`Applied ${layoutMode} layout`)
          // Auto-fit after layout is applied
          setTimeout(() => {
            if (fgRef.current && fgRef.current.zoomToFit) {
              fgRef.current.zoomToFit(1500, 150)
            }
          }, 800)
        } catch (error) {
          toast.error(`Failed to apply ${layoutMode} layout`)
        }
      }, 500)
      
      return () => clearTimeout(timer)
    } else if (layoutMode === 'force') {
      // Reset any fixed positions when switching back to force mode
      if (fgRef.current && graphData.nodes.length > 0) {
        try {
          const nodes = fgRef.current.graphData().nodes
          nodes.forEach(node => {
            node.fx = undefined
            node.fy = undefined
            node.fz = undefined
          })
        } catch (e) {
          // Ignore errors when resetting
        }
      }
    }
  }, [layoutMode, graphData.nodes.length, viewMode, applyCustomLayout])

  // Define updateHighlight before fetchMapData so it's available for event handlers
  const updateHighlight = useCallback((node, isHover = false) => {
    const newHighlightNodes = new Set()
    const newHighlightLinks = new Set()

    if (node) {
      newHighlightNodes.add(node.id)

      graphData.links.forEach(link => {
        const sourceId = typeof link.source === 'object' ? link.source.id : link.source
        const targetId = typeof link.target === 'object' ? link.target.id : link.target
        
        if (sourceId === node.id || targetId === node.id) {
          newHighlightLinks.add(link.id || `${sourceId}-${targetId}`)
          newHighlightNodes.add(sourceId)
          newHighlightNodes.add(targetId)
        }
      })
    }

    setHighlightNodes(newHighlightNodes)
    setHighlightLinks(newHighlightLinks)
    
    if (isHover) {
      setHoverNode(node)
    }
  }, [graphData.links])

  const fetchMapData = useCallback(async (forceRefresh = false) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    abortControllerRef.current = new AbortController()
    setLoading(true)

    // Clear highlights on refresh
    if (forceRefresh) {
      setSelectedNode(null)
      setHoverNode(null)
      setHighlightNodes(new Set())
      setHighlightLinks(new Set())
    }

    try {
      const params = new URLSearchParams({
        min_similarity: settings.minSimilarity,
        top_k: settings.topK,
        max_nodes: settings.maxNodes,
        include_isolates: settings.includeIsolates
      })

      if (selectedTags.length > 0) {
        params.append('tags', selectedTags.join(','))
      }

      const response = await api.get(`/map/?${params}`, {
        signal: abortControllerRef.current.signal,
        timeout: 30000 // 30 second timeout
      })

      if (response.data.error) {
        toast.error(response.data.error)
        setGraphData({ nodes: [], links: [] })
        setStats(null)
        return
      }

      // Ensure we have valid data
      const nodes = response.data.nodes || []
      const edges = response.data.edges || []

      if (nodes.length === 0) {
        toast('No notes found. Create some notes to see the neural map!', {
          icon: '📝',
          duration: 5000
        })
      }

      const transformedData = {
        nodes: nodes.map(node => ({
          ...node,
          // Ensure IDs are strings for consistency
          id: String(node.id),
          // Add default values if missing
          degree: node.degree || 0,
          label: node.label || node.title || `Note ${node.id}`,
        })),
        links: edges.map((edge, index) => ({
          ...edge,
          id: edge.id || `link-${index}`,
          source: String(edge.source),
          target: String(edge.target),
          value: edge.weight || edge.similarity || 0.5,
          similarity: edge.similarity || edge.weight || 0.5
        }))
      }

      setGraphData(transformedData)
      setStats(response.data.stats)

      const tags = new Set()
      transformedData.nodes.forEach(node => {
        if (node.tags && Array.isArray(node.tags)) {
          node.tags.forEach(tag => tags.add(tag))
        }
      })
      setAvailableTags(Array.from(tags).sort())

      if (forceRefresh) {
        toast.success(`Refreshed: ${transformedData.nodes.length} notes, ${transformedData.links.length} connections`)
      }
    } catch (error) {
      if (error.name === 'AbortError' || error.name === 'CanceledError') {
        return
      }
      
      if (error.response) {
        toast.error(`Backend error: ${error.response.status} - ${error.response.statusText}`)
      } else if (error.request) {
        toast.error('Cannot connect to backend. Is it running on port 8001?')
      } else {
        toast.error(`Failed to load neural map: ${error.message}`)
      }
      
      setGraphData({ nodes: [], links: [] })
      setStats(null)
    } finally {
      setLoading(false)
    }
  }, [settings, selectedTags])

  // Auto-fit graph to view when data loads
  const autoFitGraph = useCallback(() => {
    if (!fgRef.current || !graphData.nodes.length) return
    
    setTimeout(() => {
      if (viewMode === '3d') {
        // For 3D: zoom to fit all nodes with more padding
        fgRef.current.zoomToFit(1500, 150)
      } else {
        // For 2D: center and zoom with more padding
        fgRef.current.zoomToFit(1500, 150)
      }
    }, 800) // Longer delay to let graph fully stabilize
  }, [graphData.nodes.length, viewMode])

  useEffect(() => {
    fetchMapData()

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [fetchMapData])

  // Auto-fit when data changes
  useEffect(() => {
    if (graphData.nodes.length > 0 && !loading) {
      autoFitGraph()
    }
  }, [graphData.nodes.length, loading, autoFitGraph])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      const controls = keyboardControlsRef.current
      const speed = 20
      
      switch(e.key.toLowerCase()) {
        case 'w':
        case 'arrowup':
          e.preventDefault()
          controls.forward = speed
          break
        case 's':
        case 'arrowdown':
          e.preventDefault()
          controls.forward = -speed
          break
        case 'a':
        case 'arrowleft':
          e.preventDefault()
          controls.right = -speed
          break
        case 'd':
        case 'arrowright':
          e.preventDefault()
          controls.right = speed
          break
        case 'q':
          e.preventDefault()
          controls.up = -speed
          break
        case 'e':
          e.preventDefault()
          controls.up = speed
          break
        case ' ':
          e.preventDefault()
          autoFitGraph()
          break
        default:
          return
      }
    }

    const handleKeyUp = (e) => {
      const controls = keyboardControlsRef.current
      
      switch(e.key.toLowerCase()) {
        case 'w':
        case 'arrowup':
        case 's':
        case 'arrowdown':
          controls.forward = 0
          break
        case 'a':
        case 'arrowleft':
        case 'd':
        case 'arrowright':
          controls.right = 0
          break
        case 'q':
        case 'e':
          controls.up = 0
          break
        default:
          return
      }
    }

    // Animation loop for smooth camera movement
    const animate = () => {
      if (!fgRef.current) {
        animationFrameRef.current = requestAnimationFrame(animate)
        return
      }

      const controls = keyboardControlsRef.current
      
      if (controls.forward !== 0 || controls.right !== 0 || controls.up !== 0) {
        if (viewMode === '3d') {
          const camera = fgRef.current.camera()
          if (camera) {
            const direction = new THREE.Vector3()
            camera.getWorldDirection(direction)
            
            const right = new THREE.Vector3()
            right.crossVectors(camera.up, direction).normalize()
            
            const movement = new THREE.Vector3()
            movement.add(direction.multiplyScalar(-controls.forward))
            movement.add(right.multiplyScalar(controls.right))
            movement.add(camera.up.clone().multiplyScalar(controls.up))
            
            camera.position.add(movement)
            fgRef.current.controls().target.add(movement)
          }
        } else {
          // 2D panning
          const zoom = fgRef.current.zoom() || 1
          const centerX = (fgRef.current.centerAt()?.x || 0) - controls.right / zoom
          const centerY = (fgRef.current.centerAt()?.y || 0) - controls.forward / zoom
          fgRef.current.centerAt(centerX, centerY, 0)
        }
      }
      
      animationFrameRef.current = requestAnimationFrame(animate)
    }

    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)
    animationFrameRef.current = requestAnimationFrame(animate)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [viewMode, autoFitGraph])

  useEffect(() => {
    const handleHighlightNode = (event) => {
      const { noteId } = event.detail
      const node = graphData.nodes.find(n => n.id === String(noteId))
      if (node && fgRef.current) {
        if (viewMode === '3d') {
          const distance = 200
          const distRatio = 1 + distance / Math.hypot(node.x || 0, node.y || 0, node.z || 0)
          fgRef.current.cameraPosition(
            { x: (node.x || 0) * distRatio, y: (node.y || 0) * distRatio, z: (node.z || 0) * distRatio },
            node,
            1000
          )
        } else {
          fgRef.current.centerAt(node.x, node.y, 1000)
          fgRef.current.zoom(3, 1000)
        }

        setSelectedNode(node)
        updateHighlight(node)
        toast.success(`Focused on: ${node.title}`)
      }
    }

    window.addEventListener('highlight-node', handleHighlightNode)
    return () => window.removeEventListener('highlight-node', handleHighlightNode)
  }, [graphData.nodes, viewMode, updateHighlight])

  const handleSettingsChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  const toggleTag = (tag) => {
    setSelectedTags(prev =>
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    )
  }

  const handleNodeClick = useCallback((node) => {
    setSelectedNode(node)
    updateHighlight(node, false)
    window.dispatchEvent(new CustomEvent('open-note', {
      detail: { noteId: parseInt(node.id) }
    }))
  }, [updateHighlight])

  const handleNodeHover = useCallback((node) => {
    if (node) {
      updateHighlight(node, true)
    } else {
      setHoverNode(null)
      if (!selectedNode) {
        setHighlightNodes(new Set())
        setHighlightLinks(new Set())
      } else {
        updateHighlight(selectedNode, false)
      }
    }
  }, [updateHighlight, selectedNode])

  const handleBackgroundClick = useCallback(() => {
    setSelectedNode(null)
    setHoverNode(null)
    setHighlightNodes(new Set())
    setHighlightLinks(new Set())
  }, [])

  const handleNodeDragEnd = useCallback((node) => {
    // Fix node position when user finishes dragging to prevent it from snapping back
    node.fx = node.x
    node.fy = node.y
    if (viewMode === '3d' && node.z !== undefined) {
      node.fz = node.z
    }
  }, [viewMode])

  const createTextTexture = useCallback((text, theme) => {
    const canvas = document.createElement('canvas')
    const context = canvas.getContext('2d')
    canvas.width = 768  // Wider canvas for better text quality
    canvas.height = 96  // Taller for better rendering

    context.clearRect(0, 0, canvas.width, canvas.height)

    // High quality text rendering
    context.font = 'bold 40px -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif'
    context.fillStyle = theme === 'dark' ? '#ffffff' : '#1a1a1a'
    context.textAlign = 'center'
    context.textBaseline = 'middle'
    
    // Improved letter spacing for readability
    context.letterSpacing = '2px'
    
    // Multi-layer shadow for maximum visibility
    context.shadowColor = theme === 'dark' ? 'rgba(0, 0, 0, 0.95)' : 'rgba(255, 255, 255, 0.95)'
    context.shadowBlur = 12
    context.shadowOffsetX = 0
    context.shadowOffsetY = 0
    
    // Add words with proper spacing
    const words = text.split(' ')
    let displayText = ''
    const maxWidth = canvas.width - 60
    
    // Build text with spaces between words
    for (let i = 0; i < words.length; i++) {
      const testText = displayText + (displayText ? '  ' : '') + words[i]  // Double space between words
      if (context.measureText(testText).width > maxWidth && displayText) {
        // Add ellipsis if too long
        displayText += '...'
        break
      }
      displayText = testText
    }
    
    // Draw text with outline for better visibility
    context.strokeStyle = theme === 'dark' ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.8)'
    context.lineWidth = 3
    context.strokeText(displayText || text, canvas.width / 2, canvas.height / 2)
    context.fillText(displayText || text, canvas.width / 2, canvas.height / 2)

    const texture = new THREE.Texture(canvas)
    texture.needsUpdate = true
    texture.minFilter = THREE.LinearFilter  // Better filtering for text
    texture.magFilter = THREE.LinearFilter
    return texture
  }, [])

  const node3DObject = useCallback((node) => {
    const isHighlighted = highlightNodes.has(node.id)
    const isHovered = hoverNode?.id === node.id
    const degree = node.degree || 0
    
    // More dramatic size scaling based on connections - bigger nodes for hub nodes
    const baseSize = 4 + Math.min(degree * 0.8, 15)  // Increased scaling
    const size = (isHovered || isHighlighted) ? baseSize * 1.4 : baseSize
    
    // Color based on degree
    const nodeColor = getNodeColorByDegree(degree, isHovered, isHighlighted)
    
    // Reduced polygon count for performance
    const geometry = new THREE.SphereGeometry(size, 16, 16)
    const material = new THREE.MeshBasicMaterial({
      color: nodeColor,
      transparent: true,
      opacity: degree === 0 ? 0.4 : 0.95
    })

    const mesh = new THREE.Mesh(geometry, material)

    // Enhanced glow for highlighted/hovered nodes
    if ((isHighlighted || isHovered) && !prefersReducedMotion) {
      const glowGeometry = new THREE.SphereGeometry(size * 1.6, 16, 16)
      const glowMaterial = new THREE.MeshBasicMaterial({
        color: isHovered ? '#FFD700' : nodeColor,
        transparent: true,
        opacity: 0.35,
        side: THREE.BackSide
      })
      const glowMesh = new THREE.Mesh(glowGeometry, glowMaterial)
      mesh.add(glowMesh)
      
      // Add second glow layer for extra effect
      const glow2Geometry = new THREE.SphereGeometry(size * 2, 16, 16)
      const glow2Material = new THREE.MeshBasicMaterial({
        color: isHovered ? '#FFD700' : nodeColor,
        transparent: true,
        opacity: 0.15,
        side: THREE.BackSide
      })
      const glow2Mesh = new THREE.Mesh(glow2Geometry, glow2Material)
      mesh.add(glow2Mesh)
    }

    // Text label - always visible with better scaling
    const sprite = new THREE.Sprite(
      new THREE.SpriteMaterial({
        map: createTextTexture(node.label || node.title, theme),
        transparent: true,
        depthTest: false,
        depthWrite: false
      })
    )
    // Larger sprite for better readability, scaled with node size
    const spriteWidth = 60 + (degree * 2)  // Wider for hub nodes
    const spriteHeight = 15
    sprite.scale.set(spriteWidth, spriteHeight, 1)
    sprite.position.y = size + 12  // More spacing above node
    sprite.renderOrder = 999 // Always render on top
    mesh.add(sprite)

    return mesh
  }, [highlightNodes, hoverNode, prefersReducedMotion, createTextTexture, theme, getNodeColorByDegree])

  const link3DObject = useCallback((link) => {
    const linkId = link.id || `${link.source?.id || link.source}-${link.target?.id || link.target}`
    const isHighlighted = highlightLinks.has(linkId)
    const similarity = link.similarity || link.weight || 0.5

    const start = typeof link.source === 'object'
      ? new THREE.Vector3(link.source.x || 0, link.source.y || 0, link.source.z || 0)
      : new THREE.Vector3(0, 0, 0)
    const end = typeof link.target === 'object'
      ? new THREE.Vector3(link.target.x || 0, link.target.y || 0, link.target.z || 0)
      : new THREE.Vector3(0, 0, 0)

    const distance = start.distanceTo(end)
    if (distance === 0) return null

    // Create a smooth tube geometry along the path - NO flat caps!
    const path = new THREE.LineCurve3(start, end)
    
    const baseWidth = isHighlighted ? 1.5 : 0.6
    const width = baseWidth * (0.6 + similarity * 0.4)
    
    // TubeGeometry creates a smooth tube with NO end caps - perfect!
    const geometry = new THREE.TubeGeometry(
      path,           // path
      1,              // tubular segments (minimal for performance)
      width,          // radius
      6,              // radial segments (6 is enough for smoothness)
      false           // closed = false (NO caps at all!)
    )
    
    const color = isHighlighted ? '#FFD700' : `#${Math.floor((0.5 + similarity * 0.5) * 255).toString(16).padStart(2, '0')}66FF`
    
    const material = new THREE.MeshBasicMaterial({
      color: color,
      transparent: true,
      opacity: isHighlighted ? 0.95 : Math.max(0.5, similarity * 0.75),
      depthWrite: false  // Prevent z-fighting
    })

    const tube = new THREE.Mesh(geometry, material)
    
    // No positioning needed - TubeGeometry creates the tube along the actual path
    return tube
  }, [highlightLinks])

  const node2DCanvasObject = useCallback((node, ctx, globalScale) => {
    const isHighlighted = highlightNodes.has(node.id)
    const isHovered = hoverNode?.id === node.id
    const degree = node.degree || 0
    
    // More dramatic size scaling to match 3D
    const baseSize = 6 + Math.min(degree * 0.5, 12)  // Bigger nodes for hubs
    const size = (isHovered || isHighlighted) ? baseSize * 1.3 : baseSize
    const nodeColor = getNodeColorByDegree(degree, isHovered, isHighlighted)

    // Enhanced glow for highlighted/hovered
    if ((isHighlighted || isHovered) && !prefersReducedMotion) {
      const gradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, size * 3)
      gradient.addColorStop(0, isHovered ? 'rgba(255, 215, 0, 0.6)' : `${nodeColor}99`)
      gradient.addColorStop(0.5, isHovered ? 'rgba(255, 215, 0, 0.3)' : `${nodeColor}44`)
      gradient.addColorStop(1, 'transparent')

      ctx.fillStyle = gradient
      ctx.beginPath()
      ctx.arc(node.x, node.y, size * 3, 0, 2 * Math.PI)
      ctx.fill()
    }

    // Node circle
    ctx.fillStyle = nodeColor
    ctx.globalAlpha = degree === 0 ? 0.4 : 0.95
    ctx.beginPath()
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI)
    ctx.fill()

    // Text label - always visible with improved readability
    const fontSize = Math.max(16 / globalScale, 12)  // Larger minimum font size
    ctx.font = `bold ${fontSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    
    // Stronger text shadow for better visibility
    ctx.shadowColor = theme === 'dark' ? 'rgba(0, 0, 0, 0.95)' : 'rgba(255, 255, 255, 0.95)'
    ctx.shadowBlur = 6
    ctx.lineWidth = 3
    
    // Add text outline for maximum readability
    ctx.strokeStyle = theme === 'dark' ? 'rgba(0, 0, 0, 0.9)' : 'rgba(255, 255, 255, 0.9)'
    ctx.globalAlpha = 1
    
    // Add extra spacing between words
    const words = (node.label || node.title).split(' ')
    const displayText = words.join('  ')  // Double space between words
    
    ctx.strokeText(displayText, node.x, node.y - size - 16)  // More spacing above node
    
    ctx.fillStyle = theme === 'dark' ? '#ffffff' : '#1a1a1a'
    ctx.fillText(displayText, node.x, node.y - size - 16)
    
    ctx.shadowBlur = 0
    ctx.globalAlpha = 1
  }, [highlightNodes, hoverNode, prefersReducedMotion, theme, getNodeColorByDegree])

  const renderGraph = useMemo(() => {
    if (graphData.nodes.length === 0) {
      return (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <Network className="w-24 h-24 text-[var(--sb-primary)] mx-auto mb-4 opacity-50" />
            <h2 className="text-2xl font-semibold text-[var(--sb-text-primary)] mb-2">
              No connections found
            </h2>
            <p className="text-[var(--sb-text-secondary)]">
              Create some notes to see your knowledge graph
            </p>
          </div>
        </div>
      )
    }

    const commonProps = {
      ref: fgRef,
      graphData: graphData,
      nodeLabel: node => node.title,
      onNodeClick: handleNodeClick,
      onNodeHover: handleNodeHover,
      onNodeDragEnd: handleNodeDragEnd,
      onBackgroundClick: handleBackgroundClick,
      onBackgroundRightClick: handleBackgroundClick,
      ...forceConfig,
      // EXTREMELY aggressive force simulation for maximum spacing
      cooldownTicks: 400,  // Even more time to stabilize
      d3VelocityDecay: 0.6,  // Very smooth, controlled movement
      d3AlphaDecay: 0.008,  // Super slow decay for thorough settling
      warmupTicks: 200,  // Extended initial simulation
      // MAXIMUM spacing to completely prevent overlap
      nodeRelSize: 18,  // Huge collision size (50% increase)
      linkDistance: 250,  // Massive space between connected nodes (67% increase)
      chargeStrength: -500,  // Extreme repulsion force (67% increase)
      enablePointerInteraction: true
    }

    if (viewMode === '3d') {
      return (
        <ForceGraph3D
          {...commonProps}
          nodeThreeObject={node3DObject}
          linkThreeObject={link3DObject}
          linkThreeObjectExtend={false}  // Don't extend default, use only custom
          backgroundColor={theme === 'dark' ? '#0a0a0f' : '#f5f5f5'}
          width={undefined}
          height={undefined}
          showNavInfo={false}
          enableNodeDrag={true}
          enableNavigationControls={true}
          controlType="orbit"
          // Disable particles for performance
          linkDirectionalParticles={0}
          // Explicitly disable any default link rendering
          linkWidth={0}
          linkOpacity={0}
        />
      )
    } else {
      return (
        <ForceGraph2D
          {...commonProps}
          nodeCanvasObject={node2DCanvasObject}
          linkCanvasObject={(link, ctx) => {
            const linkId = link.id || `${link.source?.id || link.source}-${link.target?.id || link.target}`
            const isHighlighted = highlightLinks.has(linkId)
            const similarity = link.similarity || link.weight || 0.5
            
            const start = link.source
            const end = link.target
            
            // Thicker, more visible lines
            const baseWidth = isHighlighted ? 6 : 2.5
            const width = baseWidth * (0.6 + similarity * 0.4)
            
            ctx.beginPath()
            ctx.moveTo(start.x, start.y)
            ctx.lineTo(end.x, end.y)
            
            // Draw glow for highlighted
            if (isHighlighted) {
              ctx.strokeStyle = 'rgba(255, 215, 0, 0.2)'
              ctx.lineWidth = width * 3
              ctx.stroke()
              
              ctx.beginPath()
              ctx.moveTo(start.x, start.y)
              ctx.lineTo(end.x, end.y)
              ctx.strokeStyle = 'rgba(255, 215, 0, 0.4)'
              ctx.lineWidth = width * 2
              ctx.stroke()
              
              ctx.beginPath()
              ctx.moveTo(start.x, start.y)
              ctx.lineTo(end.x, end.y)
            }
            
            // Main line
            ctx.strokeStyle = isHighlighted 
              ? 'rgba(255, 215, 0, 0.95)' 
              : `rgba(139, 92, 246, ${Math.max(0.5, similarity * 0.75)})`
            ctx.lineWidth = width
            ctx.stroke()
          }}
          linkDirectionalParticleSpeed={0}
          linkDirectionalParticles={0}
          backgroundColor={theme === 'dark' ? '#0a0a0f' : '#f5f5f5'}
          width={undefined}
          height={undefined}
          // Performance: use canvas instead of webGL
          dagMode={null}  // Use custom layout logic instead
        />
      )
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [graphData, viewMode, layoutMode, highlightLinks, node3DObject, link3DObject, node2DCanvasObject, handleNodeClick, handleNodeHover, handleBackgroundClick, forceConfig, theme])

  if (loading && graphData.nodes.length === 0) {
    return (
      <div className="p-8 h-full flex flex-col">
        <div className="mb-6">
          <h1 className="text-4xl font-bold text-[var(--sb-text-primary)] mb-2">Neural Map</h1>
          <p className="text-[var(--sb-text-secondary)]">Visualize connections between your notes</p>
        </div>
        <div className="flex-1 glass rounded-2xl flex items-center justify-center">
          <div className="text-center">
            <OctopusLoader size="lg" />
            <p className="text-[var(--sb-text-secondary)] mt-4">Loading your knowledge graph...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 h-full flex flex-col relative">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-[var(--sb-text-primary)] mb-2">Neural Map</h1>
            <p className="text-[var(--sb-text-secondary)]">
              Interactive visualization • {graphData.nodes.length} notes • {graphData.links.length} connections
              {stats && ` • ${(stats.embedding_coverage * 100).toFixed(0)}% semantic`}
            </p>
          </div>
          <div className="flex gap-2">
            <motion.div className="flex items-center gap-1 bg-[var(--sb-bg-secondary)] border border-[var(--sb-border)] rounded-lg p-1">
              <button
                onClick={() => setViewMode('3d')}
                className={`px-3 py-2 rounded flex items-center gap-2 transition-colors ${viewMode === '3d'
                  ? 'bg-[var(--sb-primary)] text-white'
                  : 'text-[var(--sb-text-secondary)] hover:text-[var(--sb-text-primary)]'
                  }`}
              >
                <Box size={16} />
                3D
              </button>
              <button
                onClick={() => setViewMode('2d')}
                className={`px-3 py-2 rounded flex items-center gap-2 transition-colors ${viewMode === '2d'
                  ? 'bg-[var(--sb-primary)] text-white'
                  : 'text-[var(--sb-text-secondary)] hover:text-[var(--sb-text-primary)]'
                  }`}
              >
                <Grid3x3 size={16} />
                2D
              </button>
            </motion.div>

            <motion.div className="flex items-center gap-1 bg-[var(--sb-bg-secondary)] border border-[var(--sb-border)] rounded-lg p-1">
              <button
                onClick={() => setLayoutMode('force')}
                className={`px-3 py-2 rounded flex items-center gap-2 transition-colors text-xs ${layoutMode === 'force'
                  ? 'bg-[var(--sb-primary)] text-white'
                  : 'text-[var(--sb-text-secondary)] hover:text-[var(--sb-text-primary)]'
                  }`}
                title="Force-Directed Layout"
              >
                <Network size={14} />
                Force
              </button>
              <button
                onClick={() => setLayoutMode('tree')}
                className={`px-3 py-2 rounded flex items-center gap-2 transition-colors text-xs ${layoutMode === 'tree'
                  ? 'bg-[var(--sb-primary)] text-white'
                  : 'text-[var(--sb-text-secondary)] hover:text-[var(--sb-text-primary)]'
                  }`}
                title="Tree Layout"
              >
                Tree
              </button>
              <button
                onClick={() => setLayoutMode('radial')}
                className={`px-3 py-2 rounded flex items-center gap-2 transition-colors text-xs ${layoutMode === 'radial'
                  ? 'bg-[var(--sb-primary)] text-white'
                  : 'text-[var(--sb-text-secondary)] hover:text-[var(--sb-text-primary)]'
                  }`}
                title="Radial Layout"
              >
                Radial
              </button>
            </motion.div>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => fetchMapData(true)}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-[var(--sb-secondary)]/20 border border-[var(--sb-secondary)]/30 rounded-lg text-[var(--sb-secondary)] hover:bg-[var(--sb-secondary)]/30 transition-colors disabled:opacity-50"
              title="Refresh and reset view"
            >
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
              Refresh
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowControls(!showControls)}
              className="flex items-center gap-2 px-4 py-2 bg-[var(--sb-bg-secondary)] border border-[var(--sb-border)] rounded-lg text-[var(--sb-text-primary)] hover:bg-[var(--sb-bg-tertiary)] transition-colors"
            >
              <Settings size={16} />
              Controls
            </motion.button>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {showControls && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass rounded-2xl p-6 mb-6"
          >
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--sb-text-primary)] mb-2">
                    Min Similarity: {settings.minSimilarity.toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="0.9"
                    step="0.05"
                    value={settings.minSimilarity}
                    onChange={(e) => handleSettingsChange('minSimilarity', parseFloat(e.target.value))}
                    className="w-full accent-[var(--sb-primary)]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--sb-text-primary)] mb-2">
                    Connections per Node: {settings.topK}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    step="1"
                    value={settings.topK}
                    onChange={(e) => handleSettingsChange('topK', parseInt(e.target.value))}
                    className="w-full accent-[var(--sb-primary)]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--sb-text-primary)] mb-2">
                    Max Nodes: {settings.maxNodes}
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="500"
                    step="50"
                    value={settings.maxNodes}
                    onChange={(e) => handleSettingsChange('maxNodes', parseInt(e.target.value))}
                    className="w-full accent-[var(--sb-primary)]"
                  />
                </div>

                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-[var(--sb-text-primary)]">
                    <input
                      type="checkbox"
                      checked={settings.includeIsolates}
                      onChange={(e) => handleSettingsChange('includeIsolates', e.target.checked)}
                      className="rounded accent-[var(--sb-primary)]"
                    />
                    {settings.includeIsolates ? <Eye size={16} /> : <EyeOff size={16} />}
                    Show Isolated Notes
                  </label>
                </div>
              </div>

              {availableTags.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-[var(--sb-text-primary)] mb-2 flex items-center gap-2">
                    <Tag size={16} />
                    Filter by Tags
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {availableTags.map(tag => (
                      <button
                        key={tag}
                        onClick={() => toggleTag(tag)}
                        className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${selectedTags.includes(tag)
                          ? 'bg-[var(--sb-primary)] text-white'
                          : 'bg-[var(--sb-bg-tertiary)] text-[var(--sb-text-secondary)] hover:bg-[var(--sb-border)]'
                          }`}
                      >
                        {tag}
                        {selectedTags.includes(tag) && <X size={12} className="inline ml-1" />}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {stats && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-[var(--sb-border)]">
                  <div>
                    <div className="text-xs text-[var(--sb-text-tertiary)]">Avg Degree</div>
                    <div className="text-lg font-semibold text-[var(--sb-text-primary)]">
                      {stats.avg_degree.toFixed(1)}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-[var(--sb-text-tertiary)]">Isolated Nodes</div>
                    <div className="text-lg font-semibold text-[var(--sb-text-primary)]">
                      {stats.isolated_nodes}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-[var(--sb-text-tertiary)]">Similarity Range</div>
                    <div className="text-lg font-semibold text-[var(--sb-text-primary)]">
                      {stats.min_similarity.toFixed(2)} - {stats.max_similarity.toFixed(2)}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-[var(--sb-text-tertiary)]">Embedding Coverage</div>
                    <div className="text-lg font-semibold text-[var(--sb-text-primary)]">
                      {(stats.embedding_coverage * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {selectedNode && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="absolute right-8 top-32 w-80 glass rounded-2xl p-4 z-10"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <Info size={16} className="text-[var(--sb-primary)]" />
                <h3 className="font-semibold text-[var(--sb-text-primary)]">Node Details</h3>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-[var(--sb-text-tertiary)] hover:text-[var(--sb-text-primary)]"
              >
                <X size={16} />
              </button>
            </div>

            <div className="space-y-2 text-sm">
              <div>
                <span className="text-[var(--sb-text-tertiary)]">Title:</span>
                <div className="font-medium text-[var(--sb-text-primary)]">{selectedNode.title}</div>
              </div>

              {selectedNode.tags && selectedNode.tags.length > 0 && (
                <div>
                  <span className="text-[var(--sb-text-tertiary)]">Tags:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedNode.tags.map(tag => (
                      <span
                        key={tag}
                        className="px-2 py-0.5 rounded-full bg-[var(--sb-primary)]/20 text-[var(--sb-primary)] text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <span className="text-[var(--sb-text-tertiary)]">Connections:</span>
                <div className="text-[var(--sb-text-primary)]">{selectedNode.degree}</div>
              </div>

              <div>
                <span className="text-[var(--sb-text-tertiary)]">Preview:</span>
                <div className="text-[var(--sb-text-secondary)] line-clamp-3 mt-1">
                  {selectedNode.preview}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex-1 glass rounded-2xl overflow-hidden relative" style={{ minHeight: '600px' }}>
        {renderGraph}
        
        {/* Keyboard Controls Indicator */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="absolute bottom-4 left-4 glass rounded-lg p-3 text-xs text-[var(--sb-text-tertiary)] max-w-xs"
        >
          <div className="font-semibold text-[var(--sb-text-secondary)] mb-1">⌨️ Keyboard Controls</div>
          <div className="space-y-0.5">
            <div><kbd className="px-1.5 py-0.5 bg-[var(--sb-bg-tertiary)] rounded">WASD</kbd> or <kbd className="px-1.5 py-0.5 bg-[var(--sb-bg-tertiary)] rounded">↑↓←→</kbd> Navigate</div>
            <div><kbd className="px-1.5 py-0.5 bg-[var(--sb-bg-tertiary)] rounded">Q</kbd> / <kbd className="px-1.5 py-0.5 bg-[var(--sb-bg-tertiary)] rounded">E</kbd> Up/Down (3D)</div>
            <div><kbd className="px-1.5 py-0.5 bg-[var(--sb-bg-tertiary)] rounded">Space</kbd> Reset View</div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
