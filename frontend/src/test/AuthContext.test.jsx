import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { AuthProvider, AuthContext } from '../context/AuthContext'
import { useContext } from 'react'

// Mock the API module
vi.mock('../utils/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
  onUnauthorized: vi.fn(() => () => {}),
}))

// Mock healthCheck module  
vi.mock('../utils/healthCheck', () => ({
  checkHealth: vi.fn(() => Promise.resolve({ healthy: true })),
  onHealthChange: vi.fn(() => () => {}),
}))

// Mock toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

// Test component to access auth context
function TestComponent() {
  const auth = useContext(AuthContext)
  if (!auth) return <div>No auth context</div>
  
  return (
    <div>
      <div data-testid="loading">{auth.loading.toString()}</div>
      <div data-testid="authenticated">{auth.isAuthenticated.toString()}</div>
      <div data-testid="initialized">{auth.initialized.toString()}</div>
      <div data-testid="user">{auth.user ? auth.user.username : 'null'}</div>
      <button onClick={() => auth.login('test', 'password')}>Login</button>
      <button onClick={() => auth.signup('test', 'password')}>Signup</button>
      <button onClick={() => auth.logout()}>Logout</button>
    </div>
  )
}

describe('AuthContext', () => {
  let mockApi

  beforeEach(async () => {
    const apiModule = await import('../utils/api')
    mockApi = vi.mocked(apiModule.default)
    vi.clearAllMocks()
  })

  it('should provide auth context', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
    expect(screen.getByTestId('loading')).toHaveTextContent('true')
    expect(screen.getByTestId('user')).toHaveTextContent('null')
  })

  it('should handle successful authentication', async () => {
    // Mock successful /auth/me response
    mockApi.get.mockResolvedValueOnce({
      data: { id: 1, username: 'testuser' }
    })

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false')
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
      expect(screen.getByTestId('user')).toHaveTextContent('testuser')
    })
  })

  it('should handle login flow with checkAuth returning success', async () => {
    // Mock initial auth check (401)
    mockApi.get.mockRejectedValueOnce({
      response: { status: 401 }
    })
    
    // Mock login token response
    mockApi.post.mockResolvedValueOnce({})
    
    // Mock successful checkAuth responses after login (retries)
    mockApi.get.mockResolvedValueOnce({
      data: { id: 1, username: 'testuser' }
    })

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    // Wait for initial auth check to complete
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false')
    })

    // Trigger login
    const loginButton = screen.getByText('Login')
    loginButton.click()

    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/auth/token', expect.any(URLSearchParams), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      // After successful login and checkAuth, user should be authenticated
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
      expect(screen.getByTestId('user')).toHaveTextContent('testuser')
    })
  })

  it('should handle failed authentication check', async () => {
    // Mock failed /auth/me response (401)
    mockApi.get.mockRejectedValueOnce({
      response: { status: 401 }
    })

    render(
      <AuthProvider>
        <TestComponent />  
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false')
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
      expect(screen.getByTestId('initialized')).toHaveTextContent('true')
    })
  })
})