import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Search as SearchIcon, Sparkles, Brain, SlidersHorizontal, X } from 'lucide-react'
import api from '../utils/api'
import toast from 'react-hot-toast'
import OctopusLoader from '../components/OctopusLoader'

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchMethod, setSearchMethod] = useState('')
  const [explanation, setExplanation] = useState(null)
  const [loadingExplanation, setLoadingExplanation] = useState(false)
  
  // Filter states
  const [showFilters, setShowFilters] = useState(false)
  const [allTags, setAllTags] = useState([])
  const [selectedTags, setSelectedTags] = useState([])
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [sortBy, setSortBy] = useState('relevance')

  useEffect(() => {
    fetchTags()
  }, [])

  const fetchTags = async () => {
    try {
      const response = await api.get('/notes/tags/all')
      setAllTags(response.data)
    } catch (error) {
      console.error('Failed to load tags:', error)
    }
  }

  const toggleTag = (tag) => {
    setSelectedTags(prev => 
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    )
  }

  const clearFilters = () => {
    setSelectedTags([])
    setDateFrom('')
    setDateTo('')
    setSortBy('relevance')
  }

  const handleSearch = async e => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setExplanation(null)
    try {
      const response = await api.post('/search/', { 
        query,
        filters: {
          tags: selectedTags.length > 0 ? selectedTags : undefined,
          date_from: dateFrom || undefined,
          date_to: dateTo || undefined,
          sort_by: sortBy
        }
      })
      setResults(response.data.results || [])
      setSearchMethod(response.data.search_method || '')
      
      if (response.data.results && response.data.results.length > 0) {
        toast.success(response.data.message || `Found ${response.data.count || 0} results`)
      } else {
        toast.error('No results found. Try different keywords.')
      }
    } catch (error) {
      toast.error('Search failed')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const handleExplainResults = async () => {
    if (!results.length) return
    
    setLoadingExplanation(true)
    try {
      const response = await api.post('/search/explain', { 
        query, 
        results: results.slice(0, 5) // Send top 5 results
      })
      setExplanation(response.data)
    } catch (error) {
      toast.error('Failed to generate explanation')
    } finally {
      setLoadingExplanation(false)
    }
  }

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8" style={{ color: 'var(--sb-text-primary)' }}>Semantic Search</h1>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="mb-8">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search by meaning, topic, or concept..."
              className="w-full px-6 py-4 pl-14 rounded-2xl focus:outline-none focus:ring-2 transition-all"
              style={{
                background: 'var(--sb-surface)',
                border: '1px solid var(--sb-border)',
                color: 'var(--sb-text-primary)',
                boxShadow: 'var(--sb-shadow-sm)'
              }}
            />
            <SearchIcon 
              className="absolute left-4 top-1/2 -translate-y-1/2" 
              size={24}
              style={{ color: 'var(--sb-text-tertiary)' }}
            />
            
            {/* Filter Toggle Button */}
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={showFilters ? 'neon-button-secondary absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all' : 'absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all'}
              style={!showFilters ? { color: 'var(--sb-text-secondary)' } : {}}
            >
              <SlidersHorizontal size={20} />
            </button>
          </div>

          {/* Filter Panel */}
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="glass rounded-xl p-6 space-y-4"
              style={{ border: '1px solid var(--sb-border)', marginTop: '1rem' }}
            >
              {/* Tag Filters */}
              <div>
                <label className="text-sm font-medium mb-2 block" style={{ color: 'var(--sb-text-secondary)' }}>
                  Filter by Tags
                </label>
                <div className="flex flex-wrap gap-2">
                  {allTags.map(tag => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => toggleTag(tag)}
                      className={selectedTags.includes(tag) ? 'neon-pill-primary' : 'neon-pill'}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>

              {/* Date Range */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block" style={{ color: 'var(--sb-text-secondary)' }}>
                    From Date
                  </label>
                  <input
                    type="date"
                    value={dateFrom}
                    onChange={(e) => setDateFrom(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg focus:outline-none focus:ring-2 transition-all"
                    style={{
                      background: 'var(--sb-surface)',
                      border: '1px solid var(--sb-border)',
                      color: 'var(--sb-text-primary)'
                    }}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block" style={{ color: 'var(--sb-text-secondary)' }}>
                    To Date
                  </label>
                  <input
                    type="date"
                    value={dateTo}
                    onChange={(e) => setDateTo(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg focus:outline-none focus:ring-2 transition-all"
                    style={{
                      background: 'var(--sb-surface)',
                      border: '1px solid var(--sb-border)',
                      color: 'var(--sb-text-primary)'
                    }}
                  />
                </div>
              </div>

              {/* Sort By */}
              <div>
                <label className="text-sm font-medium mb-2 block" style={{ color: 'var(--sb-text-secondary)' }}>
                  Sort By
                </label>
                <select
                  value={sortBy}
                  onChange={e => setSortBy(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg focus:outline-none focus:ring-2 transition-all"
                  style={{
                    background: 'var(--sb-surface)',
                    border: '1px solid var(--sb-border)',
                    color: 'var(--sb-text-primary)'
                  }}
                >
                  <option value="relevance">Relevance</option>
                  <option value="date_desc">Newest First</option>
                  <option value="date_asc">Oldest First</option>
                  <option value="title">Title (A-Z)</option>
                </select>
              </div>

              {/* Clear Filters Button */}
              <div className="flex justify-end pt-2">
                <button
                  type="button"
                  onClick={clearFilters}
                  className="flex items-center gap-2 px-4 py-2 text-sm transition-colors"
                  style={{ color: 'var(--sb-text-secondary)' }}
                  onMouseEnter={(e) => e.currentTarget.style.color = 'var(--sb-text-primary)'}
                  onMouseLeave={(e) => e.currentTarget.style.color = 'var(--sb-text-secondary)'}
                >
                  <X size={16} />
                  Clear Filters
                </button>
              </div>
            </motion.div>
          )}
        </form>

        {/* Results Header with Explain Button */}
        {!loading && results.length > 0 && (
          <div className="flex items-center justify-between mb-6">
            <div className="text-sm" style={{ color: 'var(--sb-text-secondary)' }}>
              Found {results.length} results using <span style={{ color: 'var(--sb-secondary)' }}>{searchMethod}</span>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleExplainResults}
              disabled={loadingExplanation}
              className="neon-button-primary px-4 py-2 rounded-lg text-sm font-semibold disabled:opacity-50"
            >
              <div className="flex items-center gap-2">
                {loadingExplanation ? (
                  <>
                    <OctopusLoader size="sm" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Brain size={16} />
                    Explain Results
                  </>
                )}
              </div>
            </motion.button>
          </div>
        )}

        {/* AI Explanation */}
        {explanation && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass rounded-2xl p-6 mb-6"
            style={{ border: '1px solid var(--sb-secondary)', boxShadow: 'var(--sb-shadow-md), var(--sb-glow-secondary)' }}
          >
            <div className="flex items-center gap-2 mb-3">
              <Sparkles style={{ color: 'var(--sb-secondary)' }} size={20} />
              <h3 className="text-lg font-semibold" style={{ color: 'var(--sb-text-primary)' }}>AI Analysis</h3>
              <span className="neon-pill-secondary text-xs">
                {explanation.method === 'llm' ? 'AI-Powered' : explanation.method === 'rule-based' ? 'Rule-Based' : 'Fallback'}
              </span>
            </div>
            <p className="leading-relaxed" style={{ color: 'var(--sb-text-secondary)' }}>{explanation.explanation}</p>
            {explanation.error && (
              <p className="text-sm mt-2" style={{ color: 'var(--sb-warning)' }}>⚠️ {explanation.error}</p>
            )}
          </motion.div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <OctopusLoader size="lg" />
            <p className="mt-4" style={{ color: 'var(--sb-text-secondary)' }}>Searching your knowledge base...</p>
          </div>
        )}

        {/* Search Results */}
        {!loading && results.length > 0 && (
          <div className="space-y-4">
            {results.map(result => (
              <motion.div
                key={result.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="neon-card rounded-2xl p-6 cursor-pointer"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-semibold" style={{ color: 'var(--sb-text-primary)' }}>{result.title}</h3>
                  <div className="flex items-center gap-2">
                    <span 
                      className="px-2 py-1 rounded-full text-xs font-medium"
                      style={{
                        background: result.score >= 0.8 ? 'rgba(16, 185, 129, 0.2)' : result.score >= 0.6 ? 'rgba(245, 158, 11, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                        color: result.score >= 0.8 ? 'var(--sb-success)' : result.score >= 0.6 ? 'var(--sb-warning)' : 'var(--sb-error)'
                      }}
                    >
                      {(result.score * 100).toFixed(0)}%
                    </span>
                    <span 
                      className="px-2 py-1 rounded-full text-xs"
                      style={{
                        background: result.search_method === 'vector' ? 'rgba(168, 85, 247, 0.2)' : 'rgba(37, 99, 235, 0.2)',
                        color: result.search_method === 'vector' ? 'var(--sb-secondary)' : 'var(--sb-info)'
                      }}
                    >
                      {result.search_method === 'vector' ? 'Semantic' : 'Keyword'}
                    </span>
                  </div>
                </div>
                
                {/* Show highlighted preview if available, otherwise regular preview */}
                <div className="text-sm mb-3" style={{ color: 'var(--sb-text-secondary)' }}>
                  {result.highlighted_preview ? (
                    <span 
                      dangerouslySetInnerHTML={{ 
                        __html: result.highlighted_preview
                          .replace(/\*\*(.*?)\*\*/g, '<mark style="background: rgba(245, 158, 11, 0.3); color: var(--sb-warning); padding: 0.125rem 0.25rem; border-radius: 0.25rem; font-weight: 500;">$1</mark>')
                      }} 
                    />
                  ) : (
                    result.preview
                  )}
                </div>
                
                {/* Tags */}
                {result.tags && result.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {result.tags.map((tag, idx) => (
                      <span 
                        key={idx}
                        className="neon-pill-secondary text-xs"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
                
                {result.created_at && (
                  <div className="text-xs" style={{ color: 'var(--sb-text-tertiary)' }}>
                    Created: {new Date(result.created_at).toLocaleDateString()}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}

        {/* No Results */}
        {!loading && query && results.length === 0 && (
          <div className="text-center py-12">
            <SearchIcon className="w-16 h-16 mx-auto mb-4" style={{ color: 'var(--sb-text-tertiary)' }} />
            <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--sb-text-primary)' }}>No results found</h3>
            <p style={{ color: 'var(--sb-text-secondary)' }}>
              Try different keywords, check spelling, or create a new note with this content.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
