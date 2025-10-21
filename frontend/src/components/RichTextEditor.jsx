import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { 
  Bold, 
  Italic, 
  List, 
  ListOrdered,
  Heading2,
  Quote,
  Code,
  Minus
} from 'lucide-react'

export default function RichTextEditor({ content, onChange, placeholder = 'Start writing...' }) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder,
      }),
    ],
    content: content || '',
    onUpdate: ({ editor }) => {
      const html = editor.getHTML()
      onChange(html)
    },
    editorProps: {
      attributes: {
        class: 'prose prose-invert max-w-none focus:outline-none min-h-[200px] px-4 py-3',
      },
    },
  })

  if (!editor) {
    return null
  }

  return (
    <div 
      className="rounded-xl overflow-hidden" 
      style={{ 
        background: 'var(--sb-surface)', 
        border: '1px solid var(--sb-border)',
        boxShadow: 'var(--sb-shadow-sm)'
      }}
    >
      {/* Toolbar */}
      <div 
        className="flex items-center gap-1 p-2 flex-wrap" 
        style={{ 
          borderBottom: '1px solid var(--sb-border)',
          background: 'var(--sb-bg-secondary)'
        }}
      >
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBold().run()}
          active={editor.isActive('bold')}
          title="Bold"
        >
          <Bold size={16} />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleItalic().run()}
          active={editor.isActive('italic')}
          title="Italic"
        >
          <Italic size={16} />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleCode().run()}
          active={editor.isActive('code')}
          title="Code"
        >
          <Code size={16} />
        </ToolbarButton>
        
        <div className="w-px h-6 mx-1" style={{ background: 'var(--sb-border)' }} />
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          active={editor.isActive('heading', { level: 2 })}
          title="Heading"
        >
          <Heading2 size={16} />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          active={editor.isActive('bulletList')}
          title="Bullet List"
        >
          <List size={16} />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          active={editor.isActive('orderedList')}
          title="Numbered List"
        >
          <ListOrdered size={16} />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
          active={editor.isActive('blockquote')}
          title="Quote"
        >
          <Quote size={16} />
        </ToolbarButton>
        
        <div className="w-px h-6 mx-1" style={{ background: 'var(--sb-border)' }} />
        
        <ToolbarButton
          onClick={() => editor.chain().focus().setHorizontalRule().run()}
          title="Horizontal Rule"
        >
          <Minus size={16} />
        </ToolbarButton>
      </div>

      {/* Editor Content */}
      <EditorContent editor={editor} style={{ color: 'var(--sb-text-primary)' }} />
    </div>
  )
}

function ToolbarButton({ onClick, active, title, children }) {
  return (
    <button
      onClick={onClick}
      type="button"
      title={title}
      className="p-2 rounded-lg transition-all"
      style={{
        background: active ? 'var(--sb-primary)' : 'transparent',
        color: active ? 'white' : 'var(--sb-text-secondary)',
        border: `1px solid ${active ? 'var(--sb-primary)' : 'var(--sb-border)'}`,
        boxShadow: active ? 'var(--sb-shadow-md)' : 'none'
      }}
      onMouseEnter={(e) => {
        if (!active) {
          e.currentTarget.style.background = 'rgba(242, 77, 128, 0.1)'
          e.currentTarget.style.color = 'var(--sb-primary)'
          e.currentTarget.style.borderColor = 'var(--sb-primary)'
        }
      }}
      onMouseLeave={(e) => {
        if (!active) {
          e.currentTarget.style.background = 'transparent'
          e.currentTarget.style.color = 'var(--sb-text-secondary)'
          e.currentTarget.style.borderColor = 'var(--sb-border)'
        }
      }}
    >
      {children}
    </button>
  )
}
