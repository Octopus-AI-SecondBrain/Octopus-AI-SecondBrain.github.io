import { useState } from 'react'
import { motion } from 'framer-motion'
import { Search as SearchIcon } from 'lucide-react'
import api from '../utils/api'
import toast from 'react-hot-toast'

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  const handleSearch = async e => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    try {
      const response = await api.post('/search/', { query })
      setResults(response.data.results || [])
      toast.success(`Found ${response.data.count || 0} results`)
    } catch (error) {
      toast.error('Search failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">Semantic Search</h1>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="mb-8">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search by meaning, topic, or concept..."
              className="w-full px-6 py-4 pl-14 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
            />
            <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={24} />
          </div>
        </form>

        {/* Results */}
        {loading && (
          <div className="text-center py-12">
            <div className="loading-dots text-2xl">
              <span>.</span>
              <span>.</span>
              <span>.</span>
            </div>
          </div>
        )}

        {!loading && results.length > 0 && (
          <div className="space-y-4">
            {results.map(result => (
              <motion.div
                key={result.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass rounded-2xl p-6 hover:bg-white/10 transition-all cursor-pointer"
              >
                <h3 className="text-lg font-semibold text-white mb-2">{result.title}</h3>
                <p className="text-gray-400 text-sm mb-3">{result.preview}</p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>Score: {(result.score * 100).toFixed(0)}%</span>
                  <span>•</span>
                  <span>{result.search_method}</span>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {!loading && query && results.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            No results found. Try a different search term.
          </div>
        )}
      </div>
    </div>
  )
}
