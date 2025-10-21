import { motion, useReducedMotion } from 'framer-motion'

/**
 * OctopusIcon - Branded octopus mascot with subtle animation
 * 
 * Features:
 * - Floating animation with gentle vertical movement
 * - Optional rotation for variety
 * - Respects prefers-reduced-motion for accessibility
 * - Configurable size and animation style
 * - Theme-aware (works in both light and dark modes)
 * 
 * @param {Object} props
 * @param {string} props.size - Size variant: 'sm', 'md', 'lg', or 'xl'
 * @param {boolean} props.animate - Whether to animate (default: true)
 * @param {string} props.animationStyle - 'float' (default), 'pulse', or 'bounce'
 * @param {string} props.className - Additional CSS classes
 */
export default function OctopusIcon({ 
  size = 'md', 
  animate = true, 
  animationStyle = 'float',
  className = '' 
}) {
  const shouldReduceMotion = useReducedMotion()
  
  const sizeClasses = {
    xs: 'text-2xl',
    sm: 'text-3xl',
    md: 'text-4xl',
    lg: 'text-6xl',
    xl: 'text-8xl',
  }

  const animations = {
    float: {
      y: [0, -10, 0],
      transition: {
        duration: 3,
        repeat: Infinity,
        ease: 'easeInOut',
      },
    },
    pulse: {
      scale: [1, 1.1, 1],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: 'easeInOut',
      },
    },
    bounce: {
      y: [0, -15, 0],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: 'easeOut',
      },
    },
  }

  if (!animate || shouldReduceMotion) {
    return (
      <div className={`${sizeClasses[size]} select-none ${className}`}>
        🐙
      </div>
    )
  }

  return (
    <motion.div
      className={`${sizeClasses[size]} select-none inline-block ${className}`}
      animate={animations[animationStyle]}
    >
      🐙
    </motion.div>
  )
}
