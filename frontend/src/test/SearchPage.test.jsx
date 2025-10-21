import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import SearchPage from '../pages/SearchPage'
import { BrowserRouter } from 'react-router-dom'

vi.mock('../utils/api', () => ({
  default: {
    post: vi.fn(),
  },
}))

vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
    button: ({ children, ...props }) => <button {...props}>{children}</button>,
  },
}))

const Wrapper = ({ children }) => <BrowserRouter>{children}</BrowserRouter>

describe('SearchPage', () => {
  let mockApi

  beforeEach(async () => {
    const apiModule = await import('../utils/api')
    mockApi = vi.mocked(apiModule.default)
    vi.clearAllMocks()
  })

  it('should perform a search and display results', async () => {
    const mockResults = {
      results: [
        {
          id: 1,
          title: 'AI Research',
          content: 'Deep learning content',
          preview: 'Deep learning content...',
          highlighted_preview: 'Deep **learning** content...',
          score: 0.95,
          search_method: 'vector',
          created_at: '2025-01-01T00:00:00Z',
        },
        {
          id: 2,
          title: 'Machine Learning',
          content: 'ML basics',
          preview: 'ML basics...',
          highlighted_preview: 'ML **basics**...',
          score: 0.85,
          search_method: 'vector',
          created_at: '2025-01-02T00:00:00Z',
        },
      ],
      count: 2,
      search_method: 'vector similarity',
      message: 'Found 2 results',
    }

    mockApi.post.mockResolvedValueOnce({ data: mockResults })

    render(<SearchPage />, { wrapper: Wrapper })

    // Enter search query
    const searchInput = screen.getByPlaceholderText(/Search by meaning/i)
    fireEvent.change(searchInput, { target: { value: 'machine learning' } })

    // Submit search
    fireEvent.submit(searchInput.closest('form'))

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/search/', {
        query: 'machine learning',
      })
    })

    // Check results are displayed
    await waitFor(() => {
      expect(screen.getByText('AI Research')).toBeInTheDocument()
      expect(screen.getByText('Machine Learning')).toBeInTheDocument()
    })

    // Check search method is displayed
    expect(screen.getByText('vector similarity')).toBeInTheDocument()
  })

  it('should display highlighted previews', async () => {
    const mockResults = {
      results: [
        {
          id: 1,
          title: 'Test Note',
          preview: 'This is a test',
          highlighted_preview: 'This is a **test**',
          score: 0.9,
          search_method: 'vector',
        },
      ],
      count: 1,
      search_method: 'vector similarity',
    }

    mockApi.post.mockResolvedValueOnce({ data: mockResults })

    render(<SearchPage />, { wrapper: Wrapper })

    const searchInput = screen.getByPlaceholderText(/Search by meaning/i)
    fireEvent.change(searchInput, { target: { value: 'test' } })
    fireEvent.submit(searchInput.closest('form'))

    await waitFor(() => {
      const highlightedText = screen.getByText((content, element) => {
        return element.innerHTML.includes('<mark')
      })
      expect(highlightedText).toBeInTheDocument()
    })
  })

  it('should call explain endpoint and show explanation', async () => {
    const mockResults = {
      results: [
        {
          id: 1,
          title: 'Note 1',
          preview: 'Content 1',
          score: 0.9,
          search_method: 'vector',
        },
      ],
      count: 1,
      search_method: 'vector similarity',
    }

    const mockExplanation = {
      explanation:
        'These results show notes related to your query about machine learning, focusing on neural networks and deep learning concepts.',
      method: 'llm',
      llm_available: true,
    }

    mockApi.post.mockResolvedValueOnce({ data: mockResults })
    mockApi.post.mockResolvedValueOnce({ data: mockExplanation })

    render(<SearchPage />, { wrapper: Wrapper })

    // Perform search
    const searchInput = screen.getByPlaceholderText(/Search by meaning/i)
    fireEvent.change(searchInput, { target: { value: 'machine learning' } })
    fireEvent.submit(searchInput.closest('form'))

    await waitFor(() => {
      expect(screen.getByText('Note 1')).toBeInTheDocument()
    })

    // Click explain button
    const explainButton = screen.getByText('Explain Results')
    fireEvent.click(explainButton)

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/search/explain', {
        query: 'machine learning',
        results: mockResults.results.slice(0, 5),
      })
    })

    // Check explanation is displayed
    await waitFor(() => {
      expect(
        screen.getByText(/These results show notes related to your query/)
      ).toBeInTheDocument()
    })
  })

  it('should handle empty search results', async () => {
    const mockResults = {
      results: [],
      count: 0,
      search_method: 'vector similarity',
      message: 'No results found',
    }

    mockApi.post.mockResolvedValueOnce({ data: mockResults })

    render(<SearchPage />, { wrapper: Wrapper })

    const searchInput = screen.getByPlaceholderText(/Search by meaning/i)
    fireEvent.change(searchInput, { target: { value: 'nonexistent' } })
    fireEvent.submit(searchInput.closest('form'))

    await waitFor(() => {
      expect(screen.getByText('No results found')).toBeInTheDocument()
    })
  })

  it('should not search with empty query', async () => {
    render(<SearchPage />, { wrapper: Wrapper })

    const searchInput = screen.getByPlaceholderText(/Search by meaning/i)
    fireEvent.change(searchInput, { target: { value: '' } })
    fireEvent.submit(searchInput.closest('form'))

    // API should not be called
    expect(mockApi.post).not.toHaveBeenCalled()
  })

  it('should display search method badges', async () => {
    const mockResults = {
      results: [
        {
          id: 1,
          title: 'Vector Result',
          preview: 'Content',
          score: 0.9,
          search_method: 'vector',
        },
        {
          id: 2,
          title: 'Keyword Result',
          preview: 'Content',
          score: 0.7,
          search_method: 'keyword',
        },
      ],
      count: 2,
      search_method: 'hybrid',
    }

    mockApi.post.mockResolvedValueOnce({ data: mockResults })

    render(<SearchPage />, { wrapper: Wrapper })

    const searchInput = screen.getByPlaceholderText(/Search by meaning/i)
    fireEvent.change(searchInput, { target: { value: 'test' } })
    fireEvent.submit(searchInput.closest('form'))

    await waitFor(() => {
      expect(screen.getByText('Semantic')).toBeInTheDocument()
      expect(screen.getByText('Keyword')).toBeInTheDocument()
    })
  })
})
