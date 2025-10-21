import { motion, AnimatePresence } from 'framer-motion'
import { X, Command } from 'lucide-react'

export default function KeyboardShortcutsModal({ isOpen, onClose }) {
  const shortcuts = [
    { keys: ['⌘', 'K'], description: 'Quick search' },
    { keys: ['⌘', 'N'], description: 'New note' },
    { keys: ['⌘', '/'], description: 'Show shortcuts' },
    { keys: ['Esc'], description: 'Close modal/cancel' },
  ]

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 flex items-center justify-center z-50 p-4"
          style={{ background: 'rgba(0, 0, 0, 0.5)' }}
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="glass rounded-2xl p-6 max-w-md w-full"
            style={{ 
              border: '1px solid var(--sb-border)',
              boxShadow: 'var(--sb-shadow-lg)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <Command style={{ color: 'var(--sb-secondary)' }} size={24} />
                <h2 
                  className="text-2xl font-semibold"
                  style={{ color: 'var(--sb-text-primary)' }}
                >
                  Keyboard Shortcuts
                </h2>
              </div>
              <button
                onClick={onClose}
                className="p-2 rounded-lg transition-colors"
                style={{ color: 'var(--sb-text-tertiary)' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(242, 77, 128, 0.1)'
                  e.currentTarget.style.color = 'var(--sb-primary)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.color = 'var(--sb-text-tertiary)'
                }}
              >
                <X size={20} />
              </button>
            </div>

            <div className="space-y-3">
              {shortcuts.map((shortcut, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between py-2 last:border-0"
                  style={{ borderBottom: index < shortcuts.length - 1 ? '1px solid var(--sb-divider)' : 'none' }}
                >
                  <span style={{ color: 'var(--sb-text-secondary)' }}>
                    {shortcut.description}
                  </span>
                  <div className="flex gap-1">
                    {shortcut.keys.map((key, i) => (
                      <kbd
                        key={i}
                        className="px-2 py-1 rounded text-sm font-mono"
                        style={{ 
                          background: 'var(--sb-bg-tertiary)',
                          border: '1px solid var(--sb-border)',
                          color: 'var(--sb-text-primary)'
                        }}
                      >
                        {key}
                      </kbd>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div 
              className="mt-6 text-sm text-center"
              style={{ color: 'var(--sb-text-tertiary)' }}
            >
              Press{' '}
              <kbd 
                className="px-2 py-1 rounded text-xs"
                style={{ 
                  background: 'var(--sb-bg-tertiary)',
                  border: '1px solid var(--sb-border)',
                  color: 'var(--sb-text-primary)'
                }}
              >
                Esc
              </kbd>{' '}
              to close
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
