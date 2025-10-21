import { motion, useReducedMotion } from 'framer-motion'

/**
 * OctopusLoader - Branded loading spinner with octopus animation
 * 
 * Features:
 * - Animated octopus emoji with pulsing and rotation
 * - Respects prefers-reduced-motion for accessibility
 * - Configurable size
 * - Theme-aware (works in both light and dark modes)
 * 
 * @param {Object} props
 * @param {string} props.size - Size variant: 'sm', 'md', 'lg', or 'xl'
 * @param {string} props.className - Additional CSS classes
 */
export default function OctopusLoader({ size = 'md', className = '' }) {
  const shouldReduceMotion = useReducedMotion()
  
  const sizeClasses = {
    sm: 'text-2xl',
    md: 'text-4xl',
    lg: 'text-6xl',
    xl: 'text-8xl',
  }

  if (shouldReduceMotion) {
    return (
      <div className={`flex items-center justify-center ${className}`} role="status" aria-label="Loading">
        <div className={`${sizeClasses[size]} select-none`}>
          🐙
        </div>
      </div>
    )
  }

  return (
    <div className={`flex items-center justify-center ${className}`} role="status" aria-label="Loading">
      <motion.div
        className={`${sizeClasses[size]} select-none`}
        animate={{
          scale: [1, 1.1, 1],
          rotate: [0, 5, -5, 0],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      >
        🐙
      </motion.div>
    </div>
  )
}
