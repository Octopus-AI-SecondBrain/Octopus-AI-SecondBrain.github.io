import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Plus, Edit, Trash2, Save, X } from 'lucide-react'
import api from '../utils/api'
import toast from 'react-hot-toast'

export default function NotesPage() {
  const [notes, setNotes] = useState([])
  const [loading, setLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [formData, setFormData] = useState({ title: '', content: '' })

  useEffect(() => {
    fetchNotes()
  }, [])

  const fetchNotes = async () => {
    try {
      const response = await api.get('/notes/')
      setNotes(response.data)
    } catch (error) {
      toast.error('Failed to load notes')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    try {
      const response = await api.post('/notes/', formData)
      setNotes([response.data, ...notes])
      setFormData({ title: '', content: '' })
      setIsCreating(false)
      toast.success('Note created!')
    } catch (error) {
      toast.error('Failed to create note')
    }
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="loading-dots text-2xl">
          <span>.</span>
          <span>.</span>
          <span>.</span>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold text-white">Your Notes</h1>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsCreating(true)}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl text-white font-semibold"
          >
            <Plus size={20} />
            New Note
          </motion.button>
        </div>

        {/* Create Form */}
        {isCreating && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass rounded-2xl p-6 mb-6"
          >
            <h2 className="text-xl font-semibold text-white mb-4">Create Note</h2>
            <input
              type="text"
              placeholder="Title"
              value={formData.title}
              onChange={e => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-xl text-white placeholder-gray-500 mb-4 focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <textarea
              placeholder="Content"
              value={formData.content}
              onChange={e => setFormData({ ...formData, content: e.target.value })}
              rows={6}
              className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-xl text-white placeholder-gray-500 mb-4 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
            />
            <div className="flex gap-2">
              <button
                onClick={handleCreate}
                className="flex items-center gap-2 px-6 py-2 bg-purple-600 rounded-lg text-white font-semibold hover:bg-purple-700"
              >
                <Save size={18} />
                Save
              </button>
              <button
                onClick={() => {
                  setIsCreating(false)
                  setFormData({ title: '', content: '' })
                }}
                className="flex items-center gap-2 px-6 py-2 bg-white/10 rounded-lg text-white font-semibold hover:bg-white/20"
              >
                <X size={18} />
                Cancel
              </button>
            </div>
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
              className="glass rounded-2xl p-6 group"
            >
              <h3 className="text-lg font-semibold text-white mb-2 line-clamp-1">
                {note.title}
              </h3>
              <p className="text-gray-400 text-sm mb-4 line-clamp-3">{note.content}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  {new Date(note.created_at).toLocaleDateString()}
                </span>
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => handleDelete(note.id)}
                    className="p-2 rounded-lg hover:bg-red-500/20 text-red-400 transition-colors"
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
            <p className="text-gray-400 text-lg mb-4">No notes yet</p>
            <button
              onClick={() => setIsCreating(true)}
              className="text-purple-400 hover:text-purple-300"
            >
              Create your first note →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
