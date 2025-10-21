import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { UserPlus, Eye, EyeOff, CheckCircle, Mail, Moon, Sun } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../hooks/useTheme'
import OctopusLoader from '../components/OctopusLoader'
import OctopusIcon from '../components/OctopusIcon'

const passwordRequirements = [
  { text: 'At least 8 characters', regex: /.{8,}/ },
  { text: 'One uppercase letter', regex: /[A-Z]/ },
  { text: 'One lowercase letter', regex: /[a-z]/ },
  { text: 'One number', regex: /\d/ },
]

export default function SignupPage() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const { signup } = useAuth()
  const { isDark, toggleTheme } = useTheme()
  const navigate = useNavigate()

  const usernameValid = username.trim().length >= 3
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  const emailValid = email.trim().length >= 3 && emailRegex.test(email)
  const passwordValid = passwordRequirements.every(req => req.regex.test(password))
  const canSubmit = usernameValid && emailValid && passwordValid && !loading

  const handleSubmit = async e => {
    e.preventDefault()
    if (!usernameValid || !emailValid || !passwordValid) return
    setLoading(true)

    const result = await signup(username, password, email)
    
    setLoading(false)

    if (result.success) {
      navigate('/app')
    }
  }

  const checkRequirement = regex => regex.test(password)

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12" style={{ background: 'var(--sb-bg-primary)' }}>
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
            <h1 className="text-3xl font-bold mb-2" style={{ color: 'var(--sb-text-primary)' }}>Create Account</h1>
            <p style={{ color: 'var(--sb-text-secondary)' }}>Start your Second Brain journey</p>
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
                minLength={3}
                className="w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2 transition-all"
                style={{
                  background: 'var(--sb-surface)',
                  border: '1px solid var(--sb-border)',
                  color: 'var(--sb-text-primary)',
                  boxShadow: 'var(--sb-shadow-sm)'
                }}
                placeholder="Choose a username"
              />
              <p className="mt-1 text-xs" style={{ color: 'var(--sb-text-tertiary)' }}>At least 3 characters</p>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2" style={{ color: 'var(--sb-text-secondary)' }}>
                Email
              </label>
              <div className="relative">
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  className="w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2 transition-all pl-12"
                  style={{
                    background: 'var(--sb-surface)',
                    border: '1px solid var(--sb-border)',
                    color: 'var(--sb-text-primary)',
                    boxShadow: 'var(--sb-shadow-sm)'
                  }}
                  placeholder="your@email.com"
                />
                <Mail size={20} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--sb-text-tertiary)' }} />
              </div>
              <p className="mt-1 text-xs" style={{ color: email && !emailValid ? 'var(--sb-error)' : 'var(--sb-text-tertiary)' }}>
                {email && !emailValid ? 'Please enter a valid email address' : 'Valid email required for account recovery'}
              </p>
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
                  placeholder="Create a strong password"
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

              {/* Password requirements */}
              <div className="mt-3 space-y-2">
                {passwordRequirements.map(req => (
                  <div key={req.text} className="flex items-center gap-2 text-sm">
                    <CheckCircle
                      size={16}
                      style={{ color: checkRequirement(req.regex) ? 'var(--sb-success)' : 'var(--sb-text-tertiary)' }}
                    />
                    <span style={{ color: checkRequirement(req.regex) ? 'var(--sb-success)' : 'var(--sb-text-tertiary)' }}>
                      {req.text}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={!canSubmit}
              className="neon-button-primary w-full py-3 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="flex items-center justify-center gap-2">
                {loading ? (
                  <OctopusLoader size="sm" />
                ) : (
                  <>
                    <UserPlus size={20} />
                    Create Account
                  </>
                )}
              </div>
            </motion.button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p style={{ color: 'var(--sb-text-secondary)' }}>
              Already have an account?{' '}
              <Link 
                to="/login" 
                className="font-semibold transition-colors"
                style={{ color: 'var(--sb-secondary)' }}
                onMouseEnter={(e) => e.currentTarget.style.color = 'var(--sb-primary)'}
                onMouseLeave={(e) => e.currentTarget.style.color = 'var(--sb-secondary)'}
              >
                Sign in
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
