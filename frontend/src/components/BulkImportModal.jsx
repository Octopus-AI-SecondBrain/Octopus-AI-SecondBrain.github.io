import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Upload, FileText, AlertCircle, CheckCircle, Loader } from 'lucide-react'
import api from '../utils/api'
import toast from 'react-hot-toast'

export default function BulkImportModal({ isOpen, onClose, onSuccess }) {
  const [importText, setImportText] = useState('')
  const [delimiter, setDelimiter] = useState('---')
  const [importing, setImporting] = useState(false)
  const [preview, setPreview] = useState([])
  const [showPreview, setShowPreview] = useState(false)

  const parseNotes = (text) => {
    if (!text.trim()) return []

    const notes = []
    
    // Split by delimiter
    const sections = text.split(new RegExp(`\\n${delimiter}\\n`, 'g'))
    
    sections.forEach((section, index) => {
      const trimmed = section.trim()
      if (!trimmed) return

      // Try to extract title from first line
      const lines = trimmed.split('\n')
      let title = lines[0].trim()
      let content = lines.slice(1).join('\n').trim()

      // If first line looks like a title (short and ends with certain chars)
      if (title.length > 100 || !content) {
        // Use whole section as content and generate title
        content = trimmed
        title = `Note ${index + 1} - ${new Date().toLocaleDateString()}`
      }

      // Remove markdown heading markers from title
      title = title.replace(/^#+\s*/, '')

      // Extract hashtags as tags
      const tagMatches = content.match(/#[\w]+/g) || []
      const tags = tagMatches.map(tag => tag.substring(1))

      notes.push({
        title: title || `Note ${index + 1}`,
        content: content || trimmed,
        tags: tags
      })
    })

    return notes
  }

  const handlePreview = () => {
    const parsed = parseNotes(importText)
    setPreview(parsed)
    setShowPreview(true)
  }

  const handleImport = async () => {
    if (!importText.trim()) {
      toast.error('Please paste some content to import')
      return
    }

    setImporting(true)

    try {
      const notesToImport = showPreview ? preview : parseNotes(importText)
      
      if (notesToImport.length === 0) {
        toast.error('No valid notes found to import')
        setImporting(false)
        return
      }

      // Import notes one by one
      let successCount = 0
      let failCount = 0

      for (const note of notesToImport) {
        try {
          await api.post('/notes/', note)
          successCount++
        } catch (error) {
          console.error('Failed to import note:', note.title, error)
          failCount++
        }
      }

      if (successCount > 0) {
        toast.success(`Successfully imported ${successCount} note${successCount > 1 ? 's' : ''}!`)
        if (onSuccess) onSuccess()
        handleClose()
      }

      if (failCount > 0) {
        toast.error(`Failed to import ${failCount} note${failCount > 1 ? 's' : ''}`)
      }
    } catch (error) {
      toast.error('Import failed: ' + (error.message || 'Unknown error'))
    } finally {
      setImporting(false)
    }
  }

  const handleClose = () => {
    setImportText('')
    setPreview([])
    setShowPreview(false)
    onClose()
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        onClick={handleClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="glass rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col"
        >
          {/* Header */}
          <div className="p-6 border-b border-[var(--sb-border)]">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Upload className="text-[var(--sb-primary)]" size={24} />
                <div>
                  <h2 className="text-2xl font-bold text-[var(--sb-text-primary)]">
                    Bulk Import Notes
                  </h2>
                  <p className="text-sm text-[var(--sb-text-secondary)] mt-1">
                    Import multiple notes from Apple Notes, text files, or any formatted content
                  </p>
                </div>
              </div>
              <button
                onClick={handleClose}
                className="text-[var(--sb-text-tertiary)] hover:text-[var(--sb-text-primary)] transition-colors"
              >
                <X size={24} />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {!showPreview ? (
              <div className="space-y-4">
                {/* Instructions */}
                <div className="bg-[var(--sb-bg-secondary)] rounded-lg p-4 space-y-2">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="text-[var(--sb-secondary)] mt-0.5" size={18} />
                    <div className="text-sm text-[var(--sb-text-secondary)]">
                      <p className="font-semibold mb-2">How to format your notes:</p>
                      <ul className="list-disc list-inside space-y-1">
                        <li>Separate each note with <code className="px-1.5 py-0.5 bg-[var(--sb-bg-tertiary)] rounded">---</code> on its own line</li>
                        <li>First line of each section becomes the title (or it auto-generates one)</li>
                        <li>Use hashtags like #tag to automatically create tags</li>
                        <li>Works great with copy-paste from Apple Notes, Notion, or plain text</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Delimiter Input */}
                <div>
                  <label className="block text-sm font-medium text-[var(--sb-text-primary)] mb-2">
                    Note Delimiter
                  </label>
                  <input
                    type="text"
                    value={delimiter}
                    onChange={(e) => setDelimiter(e.target.value)}
                    className="w-full px-4 py-2 bg-[var(--sb-bg-secondary)] border border-[var(--sb-border)] rounded-lg text-[var(--sb-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--sb-primary)]"
                    placeholder="e.g., ---, ===, ###"
                  />
                  <p className="text-xs text-[var(--sb-text-tertiary)] mt-1">
                    Text that separates your notes. Default is three dashes.
                  </p>
                </div>

                {/* Text Area */}
                <div>
                  <label className="block text-sm font-medium text-[var(--sb-text-primary)] mb-2">
                    Paste Your Notes Here
                  </label>
                  <textarea
                    value={importText}
                    onChange={(e) => setImportText(e.target.value)}
                    className="w-full h-[400px] px-4 py-3 bg-[var(--sb-bg-secondary)] border border-[var(--sb-border)] rounded-lg text-[var(--sb-text-primary)] font-mono text-sm focus:outline-none focus:ring-2 focus:ring-[var(--sb-primary)] resize-none"
                    placeholder={`My First Note
This is the content of my first note. #productivity

---

My Second Note
Another note with some content. #ideas #brainstorm

---

Quick Thought
Just a quick note about something important.`}
                  />
                </div>

                {/* Example */}
                <div className="text-xs text-[var(--sb-text-tertiary)] bg-[var(--sb-bg-tertiary)]/50 rounded-lg p-3">
                  <p className="font-semibold mb-1">💡 Tip for mobile users:</p>
                  <p>1. Open Apple Notes and select all your notes</p>
                  <p>2. Copy them</p>
                  <p>3. Paste here and click &ldquo;Preview&rdquo;</p>
                  <p>4. Review and import!</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Preview Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="text-green-500" size={20} />
                    <h3 className="text-lg font-semibold text-[var(--sb-text-primary)]">
                      Preview: {preview.length} note{preview.length !== 1 ? 's' : ''} found
                    </h3>
                  </div>
                  <button
                    onClick={() => setShowPreview(false)}
                    className="text-sm text-[var(--sb-secondary)] hover:text-[var(--sb-secondary)]/80"
                  >
                    ← Edit
                  </button>
                </div>

                {/* Preview List */}
                <div className="space-y-3 max-h-[500px] overflow-y-auto">
                  {preview.map((note, index) => (
                    <div
                      key={index}
                      className="bg-[var(--sb-bg-secondary)] rounded-lg p-4 border border-[var(--sb-border)]"
                    >
                      <div className="flex items-start gap-3">
                        <FileText className="text-[var(--sb-primary)] mt-1 flex-shrink-0" size={18} />
                        <div className="flex-1 min-w-0">
                          <h4 className="font-semibold text-[var(--sb-text-primary)] mb-1">
                            {note.title}
                          </h4>
                          <p className="text-sm text-[var(--sb-text-secondary)] line-clamp-3 mb-2">
                            {note.content}
                          </p>
                          {note.tags.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {note.tags.map((tag, tagIndex) => (
                                <span
                                  key={tagIndex}
                                  className="px-2 py-0.5 bg-[var(--sb-primary)]/20 text-[var(--sb-primary)] rounded-full text-xs"
                                >
                                  #{tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-[var(--sb-border)] flex justify-between">
            <button
              onClick={handleClose}
              disabled={importing}
              className="px-6 py-2 bg-[var(--sb-bg-secondary)] border border-[var(--sb-border)] rounded-lg text-[var(--sb-text-primary)] hover:bg-[var(--sb-bg-tertiary)] transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            
            <div className="flex gap-2">
              {!showPreview && (
                <button
                  onClick={handlePreview}
                  disabled={!importText.trim() || importing}
                  className="px-6 py-2 bg-[var(--sb-secondary)]/20 border border-[var(--sb-secondary)]/30 rounded-lg text-[var(--sb-secondary)] hover:bg-[var(--sb-secondary)]/30 transition-colors disabled:opacity-50"
                >
                  Preview
                </button>
              )}
              
              <button
                onClick={handleImport}
                disabled={!importText.trim() || importing}
                className="px-6 py-2 bg-[var(--sb-primary)] rounded-lg text-white hover:bg-[var(--sb-primary)]/90 transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {importing ? (
                  <>
                    <Loader className="animate-spin" size={18} />
                    Importing...
                  </>
                ) : (
                  <>
                    <Upload size={18} />
                    Import {showPreview ? `${preview.length} Note${preview.length !== 1 ? 's' : ''}` : 'Notes'}
                  </>
                )}
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
