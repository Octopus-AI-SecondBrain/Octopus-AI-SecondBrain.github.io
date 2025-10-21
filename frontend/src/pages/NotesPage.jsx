import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Plus, Edit, Trash2, Save, X, Download, Upload } from 'lucide-react'
import api from '../utils/api'
import toast from 'react-hot-toast'
import RichTextEditor from '../components/RichTextEditor'
import TagInput from '../components/TagInput'
import { NOTE_TEMPLATES } from '../utils/noteTemplates'
import OctopusLoader from '../components/OctopusLoader'
import BulkImportModal from '../components/BulkImportModal'

export default function NotesPage() {
  const [notes, setNotes] = useState([])
  const [loading, setLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [formData, setFormData] = useState({ title: '', content: '', tags: [] })
  const [selectedNote, setSelectedNote] = useState(null)
  const [validationErrors, setValidationErrors] = useState({})
  const [allTags, setAllTags] = useState([])
  const [selectedTagFilter, setSelectedTagFilter] = useState(null)
  const [showTemplates, setShowTemplates] = useState(false)
  const [showBulkImport, setShowBulkImport] = useState(false)

  const applyTemplate = (template) => {
    setFormData({
      title: template.title.replace('[Date]', new Date().toLocaleDateString()),
      content: template.content,
      tags: template.tags,
    })
    setShowTemplates(false)
  }

  useEffect(() => {
    fetchNotes()
    fetchAllTags()

    // Listen for keyboard shortcut to create note
    const handleCreateNote = () => setIsCreating(true)
    window.addEventListener('create-note', handleCreateNote)
    return () => window.removeEventListener('create-note', handleCreateNote)
  }, [])

  const fetchNotes = async (tag = null) => {
    try {
      const params = tag ? { tag } : {}
      const response = await api.get('/notes/', { params })
      setNotes(response.data)
    } catch (error) {
      toast.error('Failed to load notes')
    } finally {
      setLoading(false)
    }
  }

  const fetchAllTags = async () => {
    try {
      const response = await api.get('/notes/tags/all')
      setAllTags(response.data)
    } catch (error) {
      console.error('Failed to load tags:', error)
    }
  }

  const validateForm = () => {
    const errors = {}
    
    if (!formData.title?.trim()) {
      errors.title = 'Title is required'
    }
    
    // Check if content is empty (TipTap returns <p></p> for empty content)
    const contentText = formData.content?.replace(/<[^>]*>/g, '').trim()
    if (!contentText) {
      errors.content = 'Content is required'
    }
    
    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleCreate = async () => {
    if (!validateForm()) {
      toast.error('Please fill in all required fields')
      return
    }

    try {
      const response = await api.post('/notes/', formData)
      setNotes([response.data, ...notes])
      setFormData({ title: '', content: '', tags: [] })
      setIsCreating(false)
      setValidationErrors({})
      fetchAllTags() // Refresh tags list
      toast.success('Note created!')
    } catch (error) {
      const errorMsg = error?.response?.data?.detail || 'Failed to create note'
      toast.error(errorMsg)
    }
  }

  const handleEdit = async note => {
    // Fetch the latest note data to avoid stale content
    try {
      const response = await api.get(`/notes/${note.id}`)
      setEditingId(note.id)
      setFormData({ 
        title: response.data.title, 
        content: response.data.content,
        tags: response.data.tags || []
      })
      setIsCreating(false)
      setSelectedNote(null)
      setValidationErrors({})
    } catch (error) {
      toast.error('Failed to load note for editing')
    }
  }

  const handleUpdate = async () => {
    if (!validateForm()) {
      toast.error('Please fill in all required fields')
      return
    }

    try {
      const response = await api.put(`/notes/${editingId}`, formData)
      setNotes(notes.map(n => n.id === editingId ? response.data : n))
      setFormData({ title: '', content: '', tags: [] })
      setEditingId(null)
      setValidationErrors({})
      fetchAllTags() // Refresh tags list
      toast.success('Note updated!')
    } catch (error) {
      const errorMsg = error?.response?.data?.detail || 'Failed to update note'
      toast.error(errorMsg)
    }
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setFormData({ title: '', content: '', tags: [] })
    setValidationErrors({})
  }

  const handleViewNote = note => {
    setSelectedNote(note)
    setEditingId(null)
    setIsCreating(false)
  }

  const handleDelete = async id => {
    if (!confirm('Delete this note?')) return

    try {
      await api.delete(`/notes/${id}`)
      setNotes(notes.filter(n => n.id !== id))
      toast.success('Note deleted')
    } catch (error) {
      toast.error('Failed to delete note')
    }
  }

  const handleExport = async (format) => {
    try {
      const response = await api.get(`/notes/export/${format}`, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `notes.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      
      toast.success(`Notes exported as ${format.toUpperCase()}`)
    } catch (error) {
      toast.error('Failed to export notes')
    }
  }

  const handleImport = async (content, format) => {
    try {
      const response = await api.post('/notes/import', { 
        file_content: content, 
        format 
      })
      
      toast.success(response.data.message)
      fetchNotes()
      fetchAllTags()
    } catch (error) {
      const errorMsg = error?.response?.data?.detail || 'Failed to import notes'
      toast.error(errorMsg)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <OctopusLoader size="lg" />
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-4xl font-bold" style={{ color: 'var(--sb-text-primary)' }}>Your Notes</h1>
          <div className="flex gap-2">
            {/* Export Dropdown */}
            <div className="relative group">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="neon-button px-4 py-3 rounded-xl font-semibold"
              >
                <div className="flex items-center gap-2">
                  <Download size={20} />
                  Export
                </div>
              </motion.button>
              <div 
                className="absolute right-0 mt-2 w-48 glass rounded-xl overflow-hidden opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10"
                style={{ border: '1px solid var(--sb-border)', boxShadow: 'var(--sb-shadow-md)' }}
              >
                <button
                  onClick={() => handleExport('json')}
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
                  Export as JSON
                </button>
                <button
                  onClick={() => handleExport('markdown')}
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
                  Export as Markdown
                </button>
                <button
                  onClick={() => handleExport('csv')}
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
                  Export as CSV
                </button>
              </div>
            </div>

            {/* Bulk Import Button */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowBulkImport(true)}
              className="neon-button px-4 py-3 rounded-xl font-semibold"
            >
              <div className="flex items-center gap-2">
                <Upload size={20} />
                Bulk Import
              </div>
            </motion.button>

            {/* Import Button */}
            <motion.label
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="neon-button px-4 py-3 rounded-xl font-semibold cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <Download size={20} />
                Import File
              </div>
              <input
                type="file"
                accept=".json,.md,.txt"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) {
                    const reader = new FileReader()
                    reader.onload = (event) => {
                      const content = event.target?.result
                      const format = file.name.endsWith('.json') ? 'json' : 
                                   file.name.endsWith('.md') ? 'markdown' : 'text'
                      handleImport(content, format)
                    }
                    reader.readAsText(file)
                  }
                  e.target.value = '' // Reset input
                }}
              />
            </motion.label>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsCreating(true)}
              className="neon-button-primary px-6 py-3 rounded-xl font-semibold"
            >
              <div className="flex items-center gap-2">
                <Plus size={20} />
                New Note
              </div>
            </motion.button>
          </div>
        </div>

        {/* Tag Filter */}
        {allTags.length > 0 && (
          <div className="mb-6 glass rounded-xl p-4" style={{ border: '1px solid var(--sb-border)' }}>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm" style={{ color: 'var(--sb-text-secondary)' }}>Filter by tag:</span>
              <button
                onClick={() => {
                  setSelectedTagFilter(null)
                  fetchNotes()
                }}
                className={selectedTagFilter === null ? 'neon-pill-primary' : 'neon-pill'}
              >
                All
              </button>
              {allTags.map(tag => (
                <button
                  key={tag}
                  onClick={() => {
                    setSelectedTagFilter(tag)
                    fetchNotes(tag)
                  }}
                  className={selectedTagFilter === tag ? 'neon-pill-secondary' : 'neon-pill'}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Create/Edit Form */}
        {(isCreating || editingId) && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass rounded-2xl p-6 mb-6"
            style={{ border: '1px solid var(--sb-border)', boxShadow: 'var(--sb-shadow-md)' }}
          >
            <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--sb-text-primary)' }}>
              {editingId ? 'Edit Note' : 'Create Note'}
            </h2>
            
            {/* Template Selector - Only show when creating new note */}
            {!editingId && (
              <div className="mb-4">
                <button
                  type="button"
                  onClick={() => setShowTemplates(!showTemplates)}
                  className="text-sm mb-2 transition-colors"
                  style={{ color: 'var(--sb-secondary)' }}
                  onMouseEnter={(e) => e.currentTarget.style.color = 'var(--sb-primary)'}
                  onMouseLeave={(e) => e.currentTarget.style.color = 'var(--sb-secondary)'}
                >
                  {showTemplates ? '✕ Hide Templates' : '📝 Use a Template'}
                </button>
                
                {showTemplates && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mb-4">
                    {NOTE_TEMPLATES.map(template => (
                      <button
                        key={template.id}
                        type="button"
                        onClick={() => applyTemplate(template)}
                        className="neon-card p-3 rounded-lg text-left"
                      >
                        <div className="text-2xl mb-1">{template.icon}</div>
                        <div className="text-sm font-medium" style={{ color: 'var(--sb-text-primary)' }}>{template.name}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            <div className="mb-4">
              <input
                type="text"
                placeholder="Title"
                value={formData.title}
                onChange={e => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2 transition-all"
                style={{
                  background: 'var(--sb-surface)',
                  border: `1px solid ${validationErrors.title ? 'var(--sb-error)' : 'var(--sb-border)'}`,
                  color: 'var(--sb-text-primary)',
                  boxShadow: 'var(--sb-shadow-sm)'
                }}
              />
              {validationErrors.title && (
                <p className="text-sm mt-1" style={{ color: 'var(--sb-error)' }}>{validationErrors.title}</p>
              )}
            </div>
            
            <div className="mb-4">
              <RichTextEditor
                content={formData.content}
                onChange={(html) => setFormData({ ...formData, content: html })}
                placeholder="Start writing your note..."
              />
              {validationErrors.content && (
                <p className="text-sm mt-1" style={{ color: 'var(--sb-error)' }}>{validationErrors.content}</p>
              )}
            </div>
            
            <div className="mb-4">
              <label className="block text-sm mb-2" style={{ color: 'var(--sb-text-secondary)' }}>Tags</label>
              <TagInput
                tags={formData.tags}
                onChange={(tags) => setFormData({ ...formData, tags })}
                suggestions={allTags}
              />
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={editingId ? handleUpdate : handleCreate}
                className="neon-button-primary px-6 py-2 rounded-lg font-semibold"
              >
                <div className="flex items-center gap-2">
                  <Save size={18} />
                  {editingId ? 'Update' : 'Save'}
                </div>
              </button>
              <button
                onClick={editingId ? handleCancelEdit : () => {
                  setIsCreating(false)
                  setFormData({ title: '', content: '', tags: [] })
                  setValidationErrors({})
                }}
                className="neon-button px-6 py-2 rounded-lg font-semibold"
              >
                <div className="flex items-center gap-2">
                  <X size={18} />
                  Cancel
                </div>
              </button>
            </div>
          </motion.div>
        )}

        {/* Note Detail Modal */}
        {selectedNote && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed inset-0 flex items-center justify-center z-50 p-4"
            style={{ background: 'rgba(0, 0, 0, 0.5)' }}
            onClick={() => setSelectedNote(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="glass rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              style={{ border: '1px solid var(--sb-border)', boxShadow: 'var(--sb-shadow-lg)' }}
              onClick={e => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-semibold" style={{ color: 'var(--sb-text-primary)' }}>{selectedNote.title}</h2>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(selectedNote)}
                    className="p-2 rounded-lg transition-all"
                    style={{ color: 'var(--sb-secondary)' }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'rgba(168, 85, 247, 0.2)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'transparent'
                    }}
                  >
                    <Edit size={16} />
                  </button>
                  <button
                    onClick={() => setSelectedNote(null)}
                    className="p-2 rounded-lg transition-all"
                    style={{ color: 'var(--sb-text-secondary)' }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'rgba(97, 93, 115, 0.2)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'transparent'
                    }}
                  >
                    <X size={16} />
                  </button>
                </div>
              </div>
              <div 
                className="leading-relaxed prose prose-invert max-w-none"
                style={{ color: 'var(--sb-text-secondary)' }}
                dangerouslySetInnerHTML={{ __html: selectedNote.content }}
              />
              
              {/* Tags in modal */}
              {selectedNote.tags && selectedNote.tags.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {selectedNote.tags.map(tag => (
                    <span 
                      key={tag}
                      className="neon-pill-secondary"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
              
              <div 
                className="mt-4 pt-4 text-xs"
                style={{ borderTop: '1px solid var(--sb-border)', color: 'var(--sb-text-tertiary)' }}
              >
                Created: {new Date(selectedNote.created_at).toLocaleDateString()}
                {selectedNote.updated_at && selectedNote.updated_at !== selectedNote.created_at && (
                  <span> • Updated: {new Date(selectedNote.updated_at).toLocaleDateString()}</span>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}

        {/* Notes Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {notes.map(note => (
            <motion.div
              key={note.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              whileHover={{ scale: 1.02 }}
              className="neon-card rounded-2xl p-6 group cursor-pointer"
              onClick={() => handleViewNote(note)}
            >
              <h3 className="text-lg font-semibold mb-2 line-clamp-1" style={{ color: 'var(--sb-text-primary)' }}>
                {note.title}
              </h3>
              <p className="text-sm mb-3 line-clamp-3" style={{ color: 'var(--sb-text-secondary)' }}>
                {/* Strip HTML tags for preview */}
                {note.content?.replace(/<[^>]*>/g, '') || ''}
              </p>
              
              {/* Tags */}
              {note.tags && note.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {note.tags.slice(0, 3).map(tag => (
                    <span 
                      key={tag}
                      onClick={(e) => {
                        e.stopPropagation()
                        setSelectedTagFilter(tag)
                        fetchNotes(tag)
                      }}
                      className="neon-pill-secondary cursor-pointer"
                      style={{ fontSize: '0.75rem', padding: '0.125rem 0.5rem' }}
                    >
                      {tag}
                    </span>
                  ))}
                  {note.tags.length > 3 && (
                    <span className="text-xs" style={{ color: 'var(--sb-text-tertiary)', padding: '0.125rem 0.5rem' }}>
                      +{note.tags.length - 3}
                    </span>
                  )}
                </div>
              )}
              
              <div className="flex items-center justify-between">
                <span className="text-xs" style={{ color: 'var(--sb-text-tertiary)' }}>
                  {new Date(note.created_at).toLocaleDateString()}
                </span>
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={e => {
                      e.stopPropagation()
                      handleEdit(note)
                    }}
                    className="p-2 rounded-lg transition-all"
                    style={{ color: 'var(--sb-secondary)' }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'rgba(168, 85, 247, 0.2)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'transparent'
                    }}
                  >
                    <Edit size={16} />
                  </button>
                  <button
                    onClick={e => {
                      e.stopPropagation()
                      handleDelete(note.id)
                    }}
                    className="p-2 rounded-lg transition-all"
                    style={{ color: 'var(--sb-error)' }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'rgba(239, 68, 68, 0.2)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'transparent'
                    }}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {notes.length === 0 && !isCreating && (
          <div className="text-center py-20">
            <p className="text-lg mb-4" style={{ color: 'var(--sb-text-secondary)' }}>No notes yet</p>
            <button
              onClick={() => setIsCreating(true)}
              className="transition-colors"
              style={{ color: 'var(--sb-secondary)' }}
              onMouseEnter={(e) => e.currentTarget.style.color = 'var(--sb-primary)'}
              onMouseLeave={(e) => e.currentTarget.style.color = 'var(--sb-secondary)'}
            >
              Create your first note →
            </button>
          </div>
        )}
      </div>

      {/* Bulk Import Modal */}
      <BulkImportModal
        isOpen={showBulkImport}
        onClose={() => setShowBulkImport(false)}
        onSuccess={() => {
          fetchNotes()
          fetchAllTags()
        }}
      />
    </div>
  )
}
