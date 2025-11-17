import { useState, useCallback } from 'react'
import { Upload, Search, FileText, Trash2, Loader2, AlertCircle, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../utils/api'

const RAGPage = () => {
  const [uploadingFile, setUploadingFile] = useState(false)
  const [documents, setDocuments] = useState([])
  const [loadingDocuments, setLoadingDocuments] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [questionMode, setQuestionMode] = useState(false)
  const [answer, setAnswer] = useState(null)
  const [modalityFilter, setModalityFilter] = useState('all')

  // Load documents on mount
  const loadDocuments = useCallback(async () => {
    try {
      setLoadingDocuments(true)
      const params = modalityFilter !== 'all' ? `?modality=${modalityFilter}` : ''
      const response = await api.get(`/rag/documents${params}`)
      setDocuments(response.data.documents || [])
    } catch (error) {
      console.error('Failed to load documents:', error)
      toast.error('Failed to load documents')
    } finally {
      setLoadingDocuments(false)
    }
  }, [modalityFilter])

  // Handle file upload
  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)
    formData.append('encrypt', 'false')

    setUploadingFile(true)
    const uploadToast = toast.loading(`Uploading ${file.name}...`)

    try {
      const response = await api.post('/rag/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      toast.success('File uploaded and processed!', { id: uploadToast })
      
      // Add to documents list
      setDocuments(prev => [response.data, ...prev])
      
      // Reset input
      event.target.value = ''
    } catch (error) {
      console.error('Upload failed:', error)
      const errorMsg = error.response?.data?.detail || 'Failed to upload file'
      toast.error(errorMsg, { id: uploadToast })
    } finally {
      setUploadingFile(false)
    }
  }

  // Handle search
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query')
      return
    }

    setSearching(true)
    setAnswer(null)

    try {
      if (questionMode) {
        // Question answering mode
        const response = await api.post('/rag/answer', {
          question: searchQuery,
          top_k: 3,
          include_sources: true
        })
        
        setAnswer(response.data)
        setSearchResults([])
        toast.success('Answer generated!')
      } else {
        // Search mode
        const response = await api.post('/rag/search', {
          query: searchQuery,
          top_k: 10,
          modality_filter: modalityFilter !== 'all' ? modalityFilter : null,
          min_score: 0.5
        })
        
        setSearchResults(response.data.results || [])
        setAnswer(null)
        toast.success(`Found ${response.data.total_results} results`)
      }
    } catch (error) {
      console.error('Search failed:', error)
      const errorMsg = error.response?.data?.detail || 'Search failed'
      toast.error(errorMsg)
    } finally {
      setSearching(false)
    }
  }

  // Handle delete
  const handleDelete = async (documentId) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      await api.delete(`/rag/documents/${documentId}`)
      setDocuments(prev => prev.filter(doc => doc.id !== documentId))
      toast.success('Document deleted')
    } catch (error) {
      console.error('Delete failed:', error)
      toast.error('Failed to delete document')
    }
  }

  // Get status badge color
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-500/20 text-green-400'
      case 'processing': return 'bg-yellow-500/20 text-yellow-400'
      case 'failed': return 'bg-red-500/20 text-red-400'
      default: return 'bg-gray-500/20 text-gray-400'
    }
  }

  // Get modality icon
  const getModalityIcon = (modality) => {
    switch (modality) {
      case 'pdf': return '📄'
      case 'image': return '🖼️'
      case 'audio': return '🎵'
      case 'video': return '🎥'
      default: return '📝'
    }
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-sb-text-primary">
              Smart Knowledge Base
            </h1>
            <p className="text-sb-text-secondary mt-1">
              Upload documents, search semantically, and ask questions
            </p>
          </div>

          {/* Upload Button */}
          <label className="btn-primary cursor-pointer flex items-center gap-2">
            <input
              type="file"
              className="hidden"
              onChange={handleFileUpload}
              disabled={uploadingFile}
              accept=".txt,.md,.pdf,.png,.jpg,.jpeg,.mp3,.wav,.mp4,.mov,.json,.yaml"
            />
            {uploadingFile ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                Upload Document
              </>
            )}
          </label>
        </div>

        {/* Search Section */}
        <div className="card p-6 space-y-4">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder={questionMode ? "Ask a question..." : "Search your documents..."}
                className="input w-full pl-10"
                disabled={searching}
              />
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-sb-text-secondary" />
            </div>

            <button
              onClick={handleSearch}
              disabled={searching || !searchQuery.trim()}
              className="btn-primary px-6"
            >
              {searching ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  {questionMode ? 'Thinking...' : 'Searching...'}
                </>
              ) : (
                questionMode ? 'Ask' : 'Search'
              )}
            </button>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-4 text-sm">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={questionMode}
                onChange={(e) => setQuestionMode(e.target.checked)}
                className="form-checkbox"
              />
              <span>Question Mode (AI Answers)</span>
            </label>

            <select
              value={modalityFilter}
              onChange={(e) => setModalityFilter(e.target.value)}
              className="input py-1"
            >
              <option value="all">All Types</option>
              <option value="text">Text</option>
              <option value="pdf">PDF</option>
              <option value="image">Images</option>
              <option value="audio">Audio</option>
              <option value="video">Video</option>
            </select>
          </div>
        </div>

        {/* Answer Display */}
        {answer && (
          <div className="card p-6 space-y-4 border-l-4 border-sb-primary">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-6 h-6 text-sb-success flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-sb-text-primary mb-2">
                  Answer
                </h3>
                <p className="text-sb-text-secondary whitespace-pre-wrap leading-relaxed">
                  {answer.answer}
                </p>
                <div className="text-xs text-sb-text-tertiary mt-4">
                  Generated in {answer.execution_time_ms}ms
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-sb-text-primary">
              Search Results ({searchResults.length})
            </h3>
            {searchResults.map((result, idx) => (
              <div key={idx} className="card p-4 hover:border-sb-primary/50 transition-colors">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">{getModalityIcon(result.modality)}</span>
                      <h4 className="font-semibold text-sb-text-primary">{result.title}</h4>
                      <span className="text-xs px-2 py-1 rounded bg-sb-primary/20 text-sb-primary">
                        {Math.round(result.score * 100)}% match
                      </span>
                    </div>
                    <p className="text-sm text-sb-text-secondary line-clamp-3">
                      {result.content}
                    </p>
                    {result.metadata && Object.keys(result.metadata).length > 0 && (
                      <div className="text-xs text-sb-text-tertiary mt-2">
                        {result.metadata.page && `Page ${result.metadata.page}`}
                        {result.metadata.timestamp && ` • ${result.metadata.timestamp}`}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Documents List */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-sb-text-primary">
              Your Documents ({documents.length})
            </h3>
            <button
              onClick={loadDocuments}
              disabled={loadingDocuments}
              className="text-sm text-sb-text-secondary hover:text-sb-text-primary"
            >
              {loadingDocuments ? 'Loading...' : 'Refresh'}
            </button>
          </div>

          {loadingDocuments ? (
            <div className="card p-12 flex items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-sb-primary" />
            </div>
          ) : documents.length === 0 ? (
            <div className="card p-12 text-center">
              <FileText className="w-12 h-12 text-sb-text-tertiary mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-sb-text-primary mb-2">
                No documents yet
              </h3>
              <p className="text-sb-text-secondary">
                Upload your first document to get started with AI-powered search
              </p>
            </div>
          ) : (
            <div className="grid gap-3">
              {documents.map((doc) => (
                <div key={doc.id} className="card p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      <span className="text-2xl">{getModalityIcon(doc.modality)}</span>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-sb-text-primary truncate">
                          {doc.title}
                        </h4>
                        <div className="flex items-center gap-2 mt-1 text-xs text-sb-text-secondary">
                          <span className={`px-2 py-0.5 rounded ${getStatusColor(doc.processing_status)}`}>
                            {doc.processing_status}
                          </span>
                          <span>•</span>
                          <span>{doc.chunk_count} chunks</span>
                          {doc.file_size && (
                            <>
                              <span>•</span>
                              <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                            </>
                          )}
                          <span>•</span>
                          <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                        </div>
                        {doc.processing_error && (
                          <div className="flex items-center gap-2 mt-2 text-xs text-red-400">
                            <AlertCircle className="w-4 h-4" />
                            {doc.processing_error}
                          </div>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="btn-secondary p-2 hover:bg-red-500/20 hover:text-red-400"
                      title="Delete document"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default RAGPage
