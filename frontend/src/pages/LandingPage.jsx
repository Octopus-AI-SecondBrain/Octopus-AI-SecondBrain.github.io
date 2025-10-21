import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Brain, Zap, Network, Shield, Search, Globe, Moon, Sun } from 'lucide-react'
import OctopusIcon from '../components/OctopusIcon'
import { useTheme } from '../hooks/useTheme'

const features = [
  {
    icon: Brain,
    title: 'Neural Knowledge Mapping',
    description: 'Visualize connections between your notes in an interactive 3D neural network.',
  },
  {
    icon: Search,
    title: 'Semantic Search',
    description: 'Find notes by meaning, not just keywords. Powered by AI embeddings.',
  },
  {
    icon: Network,
    title: 'Auto-Linking',
    description: 'Automatically discover and visualize relationships between your ideas.',
  },
  {
    icon: Zap,
    title: 'Lightning Fast',
    description: 'Optimized performance with local-first architecture and smart caching.',
  },
  {
    icon: Shield,
    title: 'Privacy First',
    description: 'Your data stays on your device. No cloud storage, no tracking.',
  },
  {
    icon: Globe,
    title: 'Local Hosting',
    description: 'Run entirely on your machine. Full control over your second brain.',
  },
]

export default function LandingPage() {
  const { isDark, toggleTheme } = useTheme()

  return (
    <div className="min-h-screen" style={{ 
      background: 'linear-gradient(135deg, var(--sb-bg-primary) 0%, var(--sb-bg-secondary) 50%, var(--sb-bg-primary) 100%)'
    }}>
      {/* Theme Toggle - Fixed Position */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={toggleTheme}
        className="fixed top-6 right-6 z-50 p-3 rounded-full glass"
        style={{ 
          color: 'var(--sb-text-primary)',
          boxShadow: 'var(--sb-shadow-md)'
        }}
        title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      >
        {isDark ? <Sun size={20} /> : <Moon size={20} />}
      </motion.button>

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Animated background particles */}
        <div className="absolute inset-0 overflow-hidden opacity-20">
          {[...Array(50)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 rounded-full"
              style={{ background: 'var(--sb-primary)' }}
              initial={{
                x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1000),
                y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 1000),
              }}
              animate={{
                y: [null, Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 1000)],
                opacity: [0, 1, 0],
              }}
              transition={{
                duration: Math.random() * 10 + 10,
                repeat: Infinity,
                ease: 'linear',
              }}
            />
          ))}
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
              className="inline-block mb-6"
            >
              <OctopusIcon size="xl" />
            </motion.div>

            <h1 className="text-6xl md:text-8xl font-bold mb-6 bg-clip-text text-transparent" style={{
              backgroundImage: 'var(--sb-gradient-primary)'
            }}>
              Octopus
            </h1>

            <p className="text-2xl md:text-4xl mb-4 font-light" style={{ color: 'var(--sb-text-primary)' }}>
              Your AI Second Brain
            </p>

            <p className="text-xl md:text-2xl mb-12 max-w-3xl mx-auto" style={{ color: 'var(--sb-text-secondary)' }}>
              Store. Connect. Retrieve. Remember.
            </p>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            >
              <Link
                to="/signup"
                className="neon-button-primary px-8 py-4 rounded-full font-semibold text-lg"
              >
                Get Started Free
              </Link>

              <Link
                to="/login"
                className="neon-button-secondary px-8 py-4 rounded-full font-semibold text-lg"
              >
                Sign In
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4" style={{ color: 'var(--sb-text-primary)' }}>
            Everything You Need
          </h2>
          <p className="text-xl" style={{ color: 'var(--sb-text-secondary)' }}>
            Built for researchers, writers, and knowledge workers
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.05 }}
              className="neon-card p-6 rounded-2xl transition-all cursor-pointer"
            >
              <feature.icon className="w-12 h-12 mb-4" style={{ color: 'var(--sb-secondary)' }} />
              <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--sb-text-primary)' }}>{feature.title}</h3>
              <p style={{ color: 'var(--sb-text-secondary)' }}>{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="neon-card p-12 rounded-3xl text-center"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4" style={{ color: 'var(--sb-text-primary)' }}>
            Ready to Build Your Second Brain?
          </h2>
          <p className="text-xl mb-8" style={{ color: 'var(--sb-text-secondary)' }}>
            Join thousands of users organizing their knowledge with Octopus
          </p>
          <Link
            to="/signup"
            className="neon-button-primary inline-block px-12 py-5 rounded-full font-bold text-xl"
          >
            Start Free Today
          </Link>
        </motion.div>
      </div>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--sb-border)', paddingTop: '2rem', paddingBottom: '2rem' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center" style={{ color: 'var(--sb-text-tertiary)' }}>
            &copy; 2025 Octopus. Built with ❤️ for knowledge workers.
          </p>
        </div>
      </footer>
    </div>
  )
}
