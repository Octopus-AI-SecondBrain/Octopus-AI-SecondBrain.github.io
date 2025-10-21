import { LogOut, Moon, Sun, User } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { useTheme } from '../../hooks/useTheme'
import { motion } from 'framer-motion'

export default function Navbar() {
  const { user, logout } = useAuth()
  const { isDark, toggleTheme } = useTheme()

  return (
    <header 
      className="glass px-6 py-4"
      style={{ borderBottom: '1px solid var(--sb-border)' }}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 
            className="text-2xl font-bold"
            style={{ color: 'var(--sb-text-primary)' }}
          >
            Welcome back, {user?.username}!
          </h2>
        </div>

        <div className="flex items-center gap-4">
          {/* Theme Toggle */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={toggleTheme}
            className="p-2 rounded-lg transition-all"
            style={{ 
              color: 'var(--sb-text-secondary)',
              background: 'transparent'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(242, 77, 128, 0.1)'
              e.currentTarget.style.color = 'var(--sb-primary)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent'
              e.currentTarget.style.color = 'var(--sb-text-secondary)'
            }}
            title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? <Sun size={20} /> : <Moon size={20} />}
          </motion.button>

          {/* User Menu */}
          <div 
            className="flex items-center gap-3 px-4 py-2 rounded-lg"
            style={{ background: 'var(--sb-bg-tertiary)' }}
          >
            <div 
              className="w-8 h-8 rounded-full flex items-center justify-center"
              style={{ background: 'var(--sb-gradient-primary)' }}
            >
              <User size={16} style={{ color: 'white' }} />
            </div>
            <span className="text-sm" style={{ color: 'var(--sb-text-primary)' }}>
              {user?.username}
            </span>
          </div>

          {/* Logout */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={logout}
            className="p-2 rounded-lg transition-all"
            style={{ 
              color: 'var(--sb-text-secondary)',
              background: 'transparent'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(220, 38, 38, 0.1)'
              e.currentTarget.style.color = 'var(--sb-error)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent'
              e.currentTarget.style.color = 'var(--sb-text-secondary)'
            }}
            title="Logout"
          >
            <LogOut size={20} />
          </motion.button>
        </div>
      </div>
    </header>
  )
}
