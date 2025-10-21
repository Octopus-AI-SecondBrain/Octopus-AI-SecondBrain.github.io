import '@testing-library/jest-dom'
import { vi, beforeEach } from 'vitest'

// Mock environment variables for tests
vi.stubEnv('VITE_API_URL', 'http://localhost:8001')

// Mock fetch globally for API tests
globalThis.fetch = vi.fn()

beforeEach(() => {
  fetch.mockClear()
})