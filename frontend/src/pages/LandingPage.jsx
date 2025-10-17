import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Brain, Zap, Network, Shield, Search, Globe } from 'lucide-react'

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
  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-purple-900/10 to-black">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Animated background particles */}
        <div className="absolute inset-0 overflow-hidden opacity-20">
          {[...Array(50)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-purple-500 rounded-full"
              initial={{
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
              }}
              animate={{
                y: [null, Math.random() * window.innerHeight],
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
              <div className="text-8xl animate-float">🐙</div>
            </motion.div>

            <h1 className="text-6xl md:text-8xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-500 to-blue-500">
              Octopus
            </h1>

            <p className="text-2xl md:text-4xl text-gray-300 mb-4 font-light">
              Your AI Second Brain
            </p>

            <p className="text-xl md:text-2xl text-gray-400 mb-12 max-w-3xl mx-auto">
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
                className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full text-white font-semibold text-lg hover:from-purple-700 hover:to-pink-700 transition-all transform hover:scale-105 shadow-lg shadow-purple-500/50"
              >
                Get Started Free
              </Link>

              <Link
                to="/login"
                className="px-8 py-4 glass rounded-full text-white font-semibold text-lg hover:bg-white/10 transition-all"
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
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-white">
            Everything You Need
          </h2>
          <p className="text-xl text-gray-400">
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
              className="glass p-6 rounded-2xl hover:bg-white/10 transition-all cursor-pointer"
            >
              <feature.icon className="w-12 h-12 text-purple-400 mb-4" />
              <h3 className="text-xl font-semibold mb-2 text-white">{feature.title}</h3>
              <p className="text-gray-400">{feature.description}</p>
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
          className="glass p-12 rounded-3xl text-center"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-white">
            Ready to Build Your Second Brain?
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Join thousands of users organizing their knowledge with Octopus
          </p>
          <Link
            to="/signup"
            className="inline-block px-12 py-5 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full text-white font-bold text-xl hover:from-purple-700 hover:to-pink-700 transition-all transform hover:scale-105 shadow-lg shadow-purple-500/50"
          >
            Start Free Today
          </Link>
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500">
            © 2025 Octopus. Built with ❤️ for knowledge workers.
          </p>
        </div>
      </footer>
    </div>
  )
}
