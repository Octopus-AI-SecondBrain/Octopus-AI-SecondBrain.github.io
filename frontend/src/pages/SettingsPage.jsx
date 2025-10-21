import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { User, Key, Palette, Save, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../hooks/useTheme'
import api from '../utils/api'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  const { user } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const [activeTab, setActiveTab] = useState('profile')
  const [showApiKey, setShowApiKey] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    openaiApiKey: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        username: user.username || '',
        email: user.email || ''
      }))
    }
  }, [user])

  const handleSaveProfile = async () => {
    if (!formData.email && !formData.username) {
      toast.error('Please provide at least email to update')
      return
    }

    setSaving(true)
    try {
      const payload = {
        email: formData.email || null
      }

      await api.put('/auth/profile', payload)
      toast.success('Profile updated successfully!')
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to update profile'
      toast.error(message)
    } finally {
      setSaving(false)
    }
  }

  const handleSaveApiKeys = async () => {
    setSaving(true)
    try {
      // Store API keys in localStorage for now (in production, this should be server-side)
      if (formData.openaiApiKey) {
        localStorage.setItem('openai_api_key', formData.openaiApiKey)
        toast.success('API key saved locally')
      } else {
        localStorage.removeItem('openai_api_key')
        toast.success('API key removed')
      }
    } catch (error) {
      toast.error('Failed to save API key')
    } finally {
      setSaving(false)
    }
  }

  const handleResetPassword = async () => {
    if (!formData.currentPassword) {
      toast.error('Current password is required')
      return
    }
    
    if (!formData.newPassword || !formData.confirmPassword) {
      toast.error('New password and confirmation are required')
      return
    }

    if (formData.newPassword !== formData.confirmPassword) {
      toast.error('Passwords do not match')
      return
    }

    setSaving(true)
    try {
      await api.put('/auth/profile', {
        current_password: formData.currentPassword,
        new_password: formData.newPassword
      })
      
      toast.success('Password updated successfully!')
      
      // Clear password fields
      setFormData(prev => ({
        ...prev,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }))
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to update password'
      toast.error(message)
    } finally {
      setSaving(false)
    }
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'api-keys', label: 'API Keys', icon: Key },
    { id: 'appearance', label: 'Appearance', icon: Palette }
  ]

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 
            className="text-4xl font-bold mb-2"
            style={{ color: 'var(--sb-text-primary)' }}
          >
            Settings
          </h1>
          <p style={{ color: 'var(--sb-text-secondary)' }}>
            Manage your account and preferences
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-8">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className="flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all"
              style={{
                background: activeTab === tab.id 
                  ? 'var(--sb-gradient-primary)' 
                  : 'var(--sb-bg-tertiary)',
                color: activeTab === tab.id 
                  ? 'white' 
                  : 'var(--sb-text-secondary)',
              }}
              onMouseEnter={(e) => {
                if (activeTab !== tab.id) {
                  e.currentTarget.style.background = 'var(--sb-border)'
                  e.currentTarget.style.color = 'var(--sb-text-primary)'
                }
              }}
              onMouseLeave={(e) => {
                if (activeTab !== tab.id) {
                  e.currentTarget.style.background = 'var(--sb-bg-tertiary)'
                  e.currentTarget.style.color = 'var(--sb-text-secondary)'
                }
              }}
            >
              <tab.icon size={18} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass rounded-2xl p-8"
            style={{ 
              border: '1px solid var(--sb-border)',
              boxShadow: 'var(--sb-shadow-md)'
            }}
          >
            <h2 
              className="text-2xl font-semibold mb-6"
              style={{ color: 'var(--sb-text-primary)' }}
            >
              Profile Information
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label 
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--sb-text-primary)' }}
                >
                  Username
                </label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={e => setFormData(prev => ({ ...prev, username: e.target.value }))}
                  className="w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2"
                  style={{
                    background: 'var(--sb-surface)',
                    border: '1px solid var(--sb-border)',
                    color: 'var(--sb-text-primary)',
                    boxShadow: 'var(--sb-shadow-sm)'
                  }}
                  onFocus={(e) => e.currentTarget.style.borderColor = 'var(--sb-primary)'}
                  onBlur={(e) => e.currentTarget.style.borderColor = 'var(--sb-border)'}
                />
              </div>
              
              <div>
                <label 
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--sb-text-primary)' }}
                >
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={e => setFormData(prev => ({ ...prev, email: e.target.value }))}
                  className="w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2"
                  style={{
                    background: 'var(--sb-surface)',
                    border: '1px solid var(--sb-border)',
                    color: 'var(--sb-text-primary)',
                    boxShadow: 'var(--sb-shadow-sm)'
                  }}
                  onFocus={(e) => e.currentTarget.style.borderColor = 'var(--sb-primary)'}
                  onBlur={(e) => e.currentTarget.style.borderColor = 'var(--sb-border)'}
                />
              </div>
            </div>

            <div className="mt-8">
              <h3 
                className="text-lg font-semibold mb-4"
                style={{ color: 'var(--sb-text-primary)' }}
              >
                Change Password
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <input
                  type="password"
                  placeholder="Current password"
                  value={formData.currentPassword}
                  onChange={e => setFormData(prev => ({ ...prev, currentPassword: e.target.value }))}
                  className="w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2"
                  style={{
                    background: 'var(--sb-surface)',
                    border: '1px solid var(--sb-border)',
                    color: 'var(--sb-text-primary)',
                    boxShadow: 'var(--sb-shadow-sm)'
                  }}
                  onFocus={(e) => e.currentTarget.style.borderColor = 'var(--sb-primary)'}
                  onBlur={(e) => e.currentTarget.style.borderColor = 'var(--sb-border)'}
                />
                <input
                  type="password"
                  placeholder="New password"
                  value={formData.newPassword}
                  onChange={e => setFormData(prev => ({ ...prev, newPassword: e.target.value }))}
                  className="w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2"
                  style={{
                    background: 'var(--sb-surface)',
                    border: '1px solid var(--sb-border)',
                    color: 'var(--sb-text-primary)',
                    boxShadow: 'var(--sb-shadow-sm)'
                  }}
                  onFocus={(e) => e.currentTarget.style.borderColor = 'var(--sb-primary)'}
                  onBlur={(e) => e.currentTarget.style.borderColor = 'var(--sb-border)'}
                />
                <input
                  type="password"
                  placeholder="Confirm password"
                  value={formData.confirmPassword}
                  onChange={e => setFormData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                  className="w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2"
                  style={{
                    background: 'var(--sb-surface)',
                    border: '1px solid var(--sb-border)',
                    color: 'var(--sb-text-primary)',
                    boxShadow: 'var(--sb-shadow-sm)'
                  }}
                  onFocus={(e) => e.currentTarget.style.borderColor = 'var(--sb-primary)'}
                  onBlur={(e) => e.currentTarget.style.borderColor = 'var(--sb-border)'}
                />
              </div>
            </div>

            <div className="flex gap-4 mt-8">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSaveProfile}
                disabled={saving}
                className="neon-button-primary flex items-center gap-2 px-6 py-3 rounded-xl font-semibold disabled:opacity-50"
              >
                <Save size={18} />
                {saving ? 'Saving...' : 'Save Profile'}
              </motion.button>
              
              {(formData.currentPassword && formData.newPassword && formData.confirmPassword) && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleResetPassword}
                  disabled={saving}
                  className="neon-button-accent flex items-center gap-2 px-6 py-3 rounded-xl font-semibold disabled:opacity-50"
                >
                  Reset Password
                </motion.button>
              )}
            </div>
          </motion.div>
        )}

        {/* API Keys Tab */}
        {activeTab === 'api-keys' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass rounded-2xl p-8"
            style={{ 
              border: '1px solid var(--sb-border)',
              boxShadow: 'var(--sb-shadow-md)'
            }}
          >
            <h2 
              className="text-2xl font-semibold mb-6"
              style={{ color: 'var(--sb-text-primary)' }}
            >
              API Configuration
            </h2>
            
            <div className="space-y-6">
              <div>
                <label 
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--sb-text-primary)' }}
                >
                  OpenAI API Key
                  <span 
                    className="text-xs ml-2"
                    style={{ color: 'var(--sb-text-tertiary)' }}
                  >
                    (for AI-powered search explanations)
                  </span>
                </label>
                <div className="relative">
                  <input
                    type={showApiKey ? 'text' : 'password'}
                    placeholder="sk-..."
                    value={formData.openaiApiKey}
                    onChange={e => setFormData(prev => ({ ...prev, openaiApiKey: e.target.value }))}
                    className="w-full px-4 py-3 pr-12 rounded-xl focus:outline-none focus:ring-2"
                    style={{
                      background: 'var(--sb-surface)',
                      border: '1px solid var(--sb-border)',
                      color: 'var(--sb-text-primary)',
                      boxShadow: 'var(--sb-shadow-sm)'
                    }}
                    onFocus={(e) => e.currentTarget.style.borderColor = 'var(--sb-primary)'}
                    onBlur={(e) => e.currentTarget.style.borderColor = 'var(--sb-border)'}
                  />
                  <button
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 transition-colors"
                    style={{ color: 'var(--sb-text-tertiary)' }}
                    onMouseEnter={(e) => e.currentTarget.style.color = 'var(--sb-text-primary)'}
                    onMouseLeave={(e) => e.currentTarget.style.color = 'var(--sb-text-tertiary)'}
                  >
                    {showApiKey ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
                <p 
                  className="text-xs mt-2"
                  style={{ color: 'var(--sb-text-tertiary)' }}
                >
                  Your API key is stored locally and never sent to our servers. Get your key from{' '}
                  <a 
                    href="https://platform.openai.com/api-keys" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    style={{ color: 'var(--sb-secondary)' }}
                    onMouseEnter={(e) => e.currentTarget.style.color = 'var(--sb-primary)'}
                    onMouseLeave={(e) => e.currentTarget.style.color = 'var(--sb-secondary)'}
                  >
                    OpenAI Platform
                  </a>
                </p>
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleSaveApiKeys}
              disabled={saving}
              className="neon-button-primary flex items-center gap-2 px-6 py-3 rounded-xl font-semibold disabled:opacity-50 mt-6"
            >
              <Save size={18} />
              {saving ? 'Saving...' : 'Save API Keys'}
            </motion.button>
          </motion.div>
        )}

        {/* Appearance Tab */}
        {activeTab === 'appearance' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass rounded-2xl p-8"
            style={{ 
              border: '1px solid var(--sb-border)',
              boxShadow: 'var(--sb-shadow-md)'
            }}
          >
            <h2 
              className="text-2xl font-semibold mb-6"
              style={{ color: 'var(--sb-text-primary)' }}
            >
              Appearance & Theme
            </h2>
            
            <div className="space-y-6">
              <div>
                <label 
                  className="block text-sm font-medium mb-4"
                  style={{ color: 'var(--sb-text-primary)' }}
                >
                  Theme
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    onClick={() => theme !== 'dark' && toggleTheme()}
                    className="p-6 rounded-xl border-2 transition-all"
                    style={{
                      borderColor: theme === 'dark' ? 'var(--sb-primary)' : 'var(--sb-border)',
                      background: theme === 'dark' 
                        ? 'rgba(242, 77, 128, 0.1)' 
                        : 'var(--sb-bg-secondary)',
                      boxShadow: theme === 'dark' ? 'var(--sb-shadow-md)' : 'var(--sb-shadow-sm)'
                    }}
                  >
                    <div className="w-16 h-12 rounded-lg mx-auto mb-3"
                      style={{ background: 'linear-gradient(135deg, #0E0A1A 0%, #1A1328 100%)' }}
                    ></div>
                    <h3 
                      className="font-semibold"
                      style={{ color: 'var(--sb-text-primary)' }}
                    >
                      Dark
                    </h3>
                    <p 
                      className="text-sm"
                      style={{ color: 'var(--sb-text-secondary)' }}
                    >
                      {theme === 'dark' ? '✓ Active' : 'Classic dark theme'}
                    </p>
                  </button>
                  
                  <button
                    onClick={() => theme !== 'light' && toggleTheme()}
                    className="p-6 rounded-xl border-2 transition-all"
                    style={{
                      borderColor: theme === 'light' ? 'var(--sb-primary)' : 'var(--sb-border)',
                      background: theme === 'light' 
                        ? 'rgba(242, 77, 128, 0.1)' 
                        : 'var(--sb-bg-secondary)',
                      boxShadow: theme === 'light' ? 'var(--sb-shadow-md)' : 'var(--sb-shadow-sm)'
                    }}
                  >
                    <div className="w-16 h-12 rounded-lg mx-auto mb-3"
                      style={{ background: 'linear-gradient(135deg, #F7F4FA 0%, #FFFFFF 100%)' }}
                    ></div>
                    <h3 
                      className="font-semibold"
                      style={{ color: 'var(--sb-text-primary)' }}
                    >
                      Light
                    </h3>
                    <p 
                      className="text-sm"
                      style={{ color: 'var(--sb-text-secondary)' }}
                    >
                      {theme === 'light' ? '✓ Active' : 'Bright & airy'}
                    </p>
                  </button>
                </div>
              </div>

              <div>
                <label 
                  className="block text-sm font-medium mb-4"
                  style={{ color: 'var(--sb-text-primary)' }}
                >
                  Preferences
                </label>
                <div className="space-y-3">
                  <div 
                    className="flex items-center justify-between p-4 rounded-xl"
                    style={{ background: 'var(--sb-bg-secondary)', border: '1px solid var(--sb-border)' }}
                  >
                    <div>
                      <h4 
                        className="font-medium"
                        style={{ color: 'var(--sb-text-primary)' }}
                      >
                        Animated Background
                      </h4>
                      <p 
                        className="text-sm"
                        style={{ color: 'var(--sb-text-secondary)' }}
                      >
                        Show animated neural network background
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      defaultChecked
                      className="w-5 h-5 rounded focus:ring-2"
                      style={{ 
                        accentColor: 'var(--sb-primary)',
                        borderColor: 'var(--sb-border)'
                      }}
                    />
                  </div>
                  
                  <div 
                    className="flex items-center justify-between p-4 rounded-xl"
                    style={{ background: 'var(--sb-bg-secondary)', border: '1px solid var(--sb-border)' }}
                  >
                    <div>
                      <h4 
                        className="font-medium"
                        style={{ color: 'var(--sb-text-primary)' }}
                      >
                        Reduce Motion
                      </h4>
                      <p 
                        className="text-sm"
                        style={{ color: 'var(--sb-text-secondary)' }}
                      >
                        Minimize animations and transitions
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      className="w-5 h-5 rounded focus:ring-2"
                      style={{ 
                        accentColor: 'var(--sb-primary)',
                        borderColor: 'var(--sb-border)'
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}