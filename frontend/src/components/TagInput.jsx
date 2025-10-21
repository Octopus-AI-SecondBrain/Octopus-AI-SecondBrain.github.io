import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Plus } from 'lucide-react'

export default function TagInput({ tags = [], onChange, suggestions = [] }) {
  const [inputValue, setInputValue] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(false)
  const inputRef = useRef(null)

  const filteredSuggestions = suggestions.filter(
    (s) =>
      s.toLowerCase().includes(inputValue.toLowerCase()) &&
      !tags.includes(s)
  )

  const addTag = (tag) => {
    if (tag && !tags.includes(tag)) {
      onChange([...tags, tag])
      setInputValue('')
      setShowSuggestions(false)
    }
  }

  const removeTag = (tagToRemove) => {
    onChange(tags.filter((t) => t !== tagToRemove))
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      if (inputValue.trim()) {
        addTag(inputValue.trim())
      }
    } else if (e.key === 'Backspace' && !inputValue && tags.length > 0) {
      removeTag(tags[tags.length - 1])
    }
  }

  return (
    <div className="relative">
      {/* Tags Display */}
      <div className="flex flex-wrap gap-2 mb-2">
        <AnimatePresence>
          {tags.map((tag) => (
            <motion.span
              key={tag}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              className="neon-pill neon-pill-secondary"
            >
              {tag}
              <button
                type="button"
                onClick={() => removeTag(tag)}
                className="ml-1 transition-opacity hover:opacity-70"
              >
                <X size={14} />
              </button>
            </motion.span>
          ))}
        </AnimatePresence>
      </div>

      {/* Input Field */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value)
            setShowSuggestions(true)
          }}
          onKeyDown={handleKeyDown}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder="Add tags (press Enter)..."
          className="w-full px-4 py-2 rounded-xl focus:outline-none"
          style={{
            background: 'var(--sb-surface)',
            border: '1px solid var(--sb-border)',
            color: 'var(--sb-text-primary)',
            boxShadow: 'var(--sb-shadow-sm)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'var(--sb-primary)'
          }}
          onMouseLeave={(e) => {
            if (document.activeElement !== e.currentTarget) {
              e.currentTarget.style.borderColor = 'var(--sb-border)'
            }
          }}
        />

        {/* Add Button */}
        {inputValue && (
          <button
            type="button"
            onClick={() => addTag(inputValue.trim())}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-lg transition-all"
            style={{
              background: 'var(--sb-primary)',
              color: 'white'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = 'var(--sb-glow-primary)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <Plus size={16} />
          </button>
        )}

        {/* Suggestions Dropdown */}
        {showSuggestions && filteredSuggestions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute z-10 w-full mt-2 py-2 glass rounded-xl max-h-48 overflow-y-auto"
            style={{
              border: '1px solid var(--sb-border)',
              boxShadow: 'var(--sb-shadow-md)'
            }}
          >
            {filteredSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => addTag(suggestion)}
                className="w-full px-4 py-2 text-left transition-all"
                style={{ color: 'var(--sb-text-primary)' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(242, 77, 128, 0.1)'
                  e.currentTarget.style.color = 'var(--sb-primary)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.color = 'var(--sb-text-primary)'
                }}
              >
                {suggestion}
              </button>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  )
}
