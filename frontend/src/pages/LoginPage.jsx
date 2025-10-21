import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { LogIn, Eye, EyeOff, Moon, Sun } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../hooks/useTheme'
import OctopusLoader from '../components/OctopusLoader'
import OctopusIcon from '../components/OctopusIcon'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const { isDark, toggleTheme } = useTheme()
  const navigate = useNavigate()

  const handleSubmit = async e => {
    e.preventDefault()
    setLoading(true)

    const result = await login(username, password)
    
    setLoading(false)

    if (result.success) {
      navigate('/app')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: 'var(--sb-bg-primary)' }}>
      {/* Theme Toggle */}
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
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="glass p-8 rounded-3xl" style={{ border: '1px solid var(--sb-border)', boxShadow: 'var(--sb-shadow-lg)' }}>
          {/* Logo */}
          <div className="text-center mb-8">
            <OctopusIcon size="lg" className="mb-4 inline-block" style={{ color: 'var(--sb-primary)' }} />
            <h1 className="text-3xl font-bold mb-2" style={{ color: 'var(--sb-text-primary)' }}>Welcome Back</h1>
            <p style={{ color: 'var(--sb-text-secondary)' }}>Sign in to your Second Brain</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium mb-2" style={{ color: 'var(--sb-text-secondary)' }}>
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
                className="w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2 transition-all"
                style={{
                  background: 'var(--sb-surface)',
                  border: '1px solid var(--sb-border)',
                  color: 'var(--sb-text-primary)',
                  boxShadow: 'var(--sb-shadow-sm)'
                }}
                placeholder="Enter your username"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-2" style={{ color: 'var(--sb-text-secondary)' }}>
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  className="w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2 transition-all pr-12"
                  style={{
                    background: 'var(--sb-surface)',
                    border: '1px solid var(--sb-border)',
                    color: 'var(--sb-text-primary)',
                    boxShadow: 'var(--sb-shadow-sm)'
                  }}
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 transition-colors"
                  style={{ color: 'var(--sb-text-secondary)' }}
                  onMouseEnter={(e) => e.currentTarget.style.color = 'var(--sb-text-primary)'}
                  onMouseLeave={(e) => e.currentTarget.style.color = 'var(--sb-text-secondary)'}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="neon-button-primary w-full py-3 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="flex items-center justify-center gap-2">
                {loading ? (
                  <OctopusLoader size="sm" />
                ) : (
                  <>
                    <LogIn size={20} />
                    Sign In
                  </>
                )}
              </div>
            </motion.button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p style={{ color: 'var(--sb-text-secondary)' }}>
              Don&apos;t have an account?{' '}
              <Link 
                to="/signup" 
                className="font-semibold transition-colors"
                style={{ color: 'var(--sb-secondary)' }}
                onMouseEnter={(e) => e.currentTarget.style.color = 'var(--sb-primary)'}
                onMouseLeave={(e) => e.currentTarget.style.color = 'var(--sb-secondary)'}
              >
                Sign up
              </Link>
            </p>
          </div>

          <div className="mt-4 text-center">
            <Link 
              to="/" 
              className="text-sm transition-colors"
              style={{ color: 'var(--sb-text-tertiary)' }}
              onMouseEnter={(e) => e.currentTarget.style.color = 'var(--sb-text-secondary)'}
              onMouseLeave={(e) => e.currentTarget.style.color = 'var(--sb-text-tertiary)'}
            >
              ← Back to home
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
