import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import NotesPage from '../pages/NotesPage'
import { BrowserRouter } from 'react-router-dom'

// Mock the API module
vi.mock('../utils/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

// Import api for mocking
import api from '../utils/api'

// Mock toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

// Mock RichTextEditor component
vi.mock('../components/RichTextEditor', () => ({
  default: ({ content, onChange }) => (
    <textarea
      data-testid="rich-editor"
      value={content}
      onChange={(e) => onChange(e.target.value)}
    />
  ),
}))

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
    button: ({ children, ...props }) => <button {...props}>{children}</button>,
  },
}))

const Wrapper = ({ children }) => <BrowserRouter>{children}</BrowserRouter>

describe('NotesPage', () => {
  let mockApi

  beforeEach(async () => {
    mockApi = vi.mocked(api)
    vi.clearAllMocks()
  })

  it('should fetch and display notes', async () => {
    const mockNotes = [
      {
        id: 1,
        title: 'Test Note 1',
        content: '<p>Content 1</p>',
        created_at: '2025-01-01T00:00:00Z',
      },
      {
        id: 2,
        title: 'Test Note 2',
        content: '<p>Content 2</p>',
        created_at: '2025-01-02T00:00:00Z',
      },
    ]

    mockApi.get.mockResolvedValueOnce({ data: mockNotes })

    render(<NotesPage />, { wrapper: Wrapper })

    // Should show loading initially
    expect(screen.getByText(/\.\.\./)).toBeInTheDocument()

    // Wait for notes to load
    await waitFor(() => {
      expect(screen.getByText('Test Note 1')).toBeInTheDocument()
      expect(screen.getByText('Test Note 2')).toBeInTheDocument()
    })

    expect(mockApi.get).toHaveBeenCalledWith('/notes/')
  })

  it('should create a new note', async () => {
    mockApi.get.mockResolvedValueOnce({ data: [] })
    mockApi.post.mockResolvedValueOnce({
      data: {
        id: 1,
        title: 'New Note',
        content: '<p>New content</p>',
        created_at: '2025-01-01T00:00:00Z',
      },
    })

    render(<NotesPage />, { wrapper: Wrapper })

    await waitFor(() => {
      expect(screen.getByText('Your Notes')).toBeInTheDocument()
    })

    // Click New Note button
    const newNoteButton = screen.getByText('New Note')
    fireEvent.click(newNoteButton)

    // Fill in the form
    const titleInput = screen.getByPlaceholderText('Title')
    const contentInput = screen.getByTestId('rich-editor')

    fireEvent.change(titleInput, { target: { value: 'New Note' } })
    fireEvent.change(contentInput, { target: { value: '<p>New content</p>' } })

    // Submit the form
    const saveButton = screen.getByText('Save')
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/notes/', {
        title: 'New Note',
        content: '<p>New content</p>',
      })
    })
  })

  it('should validate empty title and content', async () => {
    mockApi.get.mockResolvedValueOnce({ data: [] })

    render(<NotesPage />, { wrapper: Wrapper })

    await waitFor(() => {
      expect(screen.getByText('Your Notes')).toBeInTheDocument()
    })

    // Click New Note button
    const newNoteButton = screen.getByText('New Note')
    fireEvent.click(newNoteButton)

    // Try to save without filling in fields
    const saveButton = screen.getByText('Save')
    fireEvent.click(saveButton)

    // Should show validation errors
    await waitFor(() => {
      expect(screen.getByText('Title is required')).toBeInTheDocument()
      expect(screen.getByText('Content is required')).toBeInTheDocument()
    })

    // Should not have called the API
    expect(mockApi.post).not.toHaveBeenCalled()
  })

  it('should update an existing note', async () => {
    const mockNote = {
      id: 1,
      title: 'Original Title',
      content: '<p>Original content</p>',
      created_at: '2025-01-01T00:00:00Z',
    }

    mockApi.get.mockResolvedValueOnce({ data: [mockNote] })
    mockApi.get.mockResolvedValueOnce({ data: mockNote }) // For edit fetch
    mockApi.put.mockResolvedValueOnce({
      data: {
        ...mockNote,
        title: 'Updated Title',
        content: '<p>Updated content</p>',
      },
    })

    render(<NotesPage />, { wrapper: Wrapper })

    await waitFor(() => {
      expect(screen.getByText('Original Title')).toBeInTheDocument()
    })

    // Click edit button (hover to reveal)
    const noteCard = screen.getByText('Original Title').closest('.glass')
    fireEvent.mouseEnter(noteCard)

    const editButton = screen.getAllByRole('button').find((btn) =>
      btn.querySelector('[data-lucide="edit"]')
    )
    fireEvent.click(editButton)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Original Title')).toBeInTheDocument()
    })

    // Update the title
    const titleInput = screen.getByDisplayValue('Original Title')
    fireEvent.change(titleInput, { target: { value: 'Updated Title' } })

    // Click update button
    const updateButton = screen.getByText('Update')
    fireEvent.click(updateButton)

    await waitFor(() => {
      expect(mockApi.put).toHaveBeenCalledWith('/notes/1', {
        title: 'Updated Title',
        content: '<p>Original content</p>',
      })
    })
  })

  it('should delete a note', async () => {
    const mockNote = {
      id: 1,
      title: 'To Delete',
      content: '<p>Content</p>',
      created_at: '2025-01-01T00:00:00Z',
    }

    mockApi.get.mockResolvedValueOnce({ data: [mockNote] })
    mockApi.delete.mockResolvedValueOnce({ data: { message: 'Note deleted' } })

    // Mock window.confirm
    window.confirm = vi.fn(() => true)

    render(<NotesPage />, { wrapper: Wrapper })

    await waitFor(() => {
      expect(screen.getByText('To Delete')).toBeInTheDocument()
    })

    // Click delete button
    const noteCard = screen.getByText('To Delete').closest('.glass')
    fireEvent.mouseEnter(noteCard)

    const deleteButton = screen.getAllByRole('button').find((btn) =>
      btn.querySelector('[data-lucide="trash-2"]')
    )
    fireEvent.click(deleteButton)

    await waitFor(() => {
      expect(mockApi.delete).toHaveBeenCalledWith('/notes/1')
    })

    // Note should be removed from the list
    await waitFor(() => {
      expect(screen.queryByText('To Delete')).not.toBeInTheDocument()
    })
  })

  it('should cancel note creation', async () => {
    mockApi.get.mockResolvedValueOnce({ data: [] })

    render(<NotesPage />, { wrapper: Wrapper })

    await waitFor(() => {
      expect(screen.getByText('Your Notes')).toBeInTheDocument()
    })

    // Click New Note button
    const newNoteButton = screen.getByText('New Note')
    fireEvent.click(newNoteButton)

    // Form should be visible
    expect(screen.getByPlaceholderText('Title')).toBeInTheDocument()

    // Click cancel
    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)

    // Form should be hidden
    await waitFor(() => {
      expect(screen.queryByPlaceholderText('Title')).not.toBeInTheDocument()
    })
  })
})
