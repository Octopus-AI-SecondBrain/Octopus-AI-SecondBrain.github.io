/**
 * Core Type Definitions for Octopus Second Brain
 * Production-grade TypeScript types with comprehensive documentation
 */

// ============================================================================
// User & Authentication Types
// ============================================================================

export interface User {
  id: number
  username: string
  email: string
  created_at: string
  updated_at?: string
}

export interface AuthTokens {
  access_token: string
  token_type: 'bearer'
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface SignupData {
  username: string
  email: string
  password: string
}

export interface AuthResponse {
  user: User
  access_token?: string
}

export interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<{ success: boolean; user?: User; error?: string }>
  signup: (data: SignupData) => Promise<{ success: boolean; user?: User; error?: string }>
  logout: () => Promise<void>
  updateProfile: (data: { email?: string; password?: string }) => Promise<{ success: boolean; error?: string }>
}

// ============================================================================
// Note Types
// ============================================================================

export interface Note {
  id: number
  title: string
  content: string
  user_id: number
  created_at: string
  updated_at: string
  tags?: string[]
  has_embedding?: boolean
}

export interface CreateNoteData {
  title: string
  content: string
  tags?: string[]
}

export interface UpdateNoteData {
  title?: string
  content?: string
  tags?: string[]
}

export interface NoteWithSimilarity extends Note {
  similarity?: number
}

// ============================================================================
// Search Types
// ============================================================================

export interface SearchResult {
  note: Note
  similarity: number
  method: 'semantic' | 'keyword'
}

export interface SearchResponse {
  results: SearchResult[]
  query: string
  total: number
  method: 'semantic' | 'keyword'
}

export interface SearchExplanation {
  explanation: string
  method: string
  query: string
}

// ============================================================================
// Neural Map Types
// ============================================================================

export interface GraphNode {
  id: number
  label: string
  content: string
  tags: string[]
  created_at: string
  updated_at: string
  x?: number
  y?: number
  z?: number
  vx?: number
  vy?: number
  vz?: number
  fx?: number
  fy?: number
  fz?: number
}

export interface GraphLink {
  source: number | GraphNode
  target: number | GraphNode
  similarity: number
  value?: number
}

export interface GraphData {
  nodes: GraphNode[]
  links: GraphLink[]
  stats: GraphStats
}

export interface GraphStats {
  total_nodes: number
  total_edges: number
  avg_degree: number
  min_similarity: number
  max_similarity: number
  isolated_nodes: number
  embedding_coverage: number
}

export type GraphLayout = 'force' | 'tree' | 'radial' | 'planetary'

export interface NeuralMapFilters {
  minSimilarity: number
  maxNodes: number
  connectionsPerNode: number
  selectedTags: string[]
  showIsolated: boolean
  layout: GraphLayout
}

// ============================================================================
// Analytics Types
// ============================================================================

export interface AnalyticsData {
  total_notes: number
  total_words: number
  weekly_notes: number
  embedding_coverage: number
  top_tags: Array<{ tag: string; count: number }>
  knowledge_graph: {
    total_nodes: number
    total_connections: number
    avg_connections: number
  }
}

// ============================================================================
// Settings Types
// ============================================================================

export interface UserSettings {
  theme: 'light' | 'dark' | 'system'
  apiKey?: string
  notifications: boolean
  analytics: boolean
}

export interface UpdatePasswordData {
  current_password: string
  new_password: string
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiError {
  error: string
  message?: string
  detail?: string
  status_code?: number
}

export interface ApiResponse<T = unknown> {
  data?: T
  error?: ApiError
  success: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  version: string
  environment: string
  database: 'connected' | 'disconnected' | 'schema_missing'
  vector_store: 'connected' | 'disconnected' | 'error' | 'unknown'
  openai: 'configured' | 'not_configured'
  message: string
  database_message?: string
  vector_error?: string
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface BaseComponentProps {
  className?: string
  'data-testid'?: string
}

export interface ModalProps extends BaseComponentProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
}

export interface ButtonProps extends BaseComponentProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
  children: React.ReactNode
}

// ============================================================================
// Theme Types
// ============================================================================

export type Theme = 'light' | 'dark'

export interface ThemeContextValue {
  theme: Theme
  toggleTheme: () => void
  setTheme: (theme: Theme) => void
}

// ============================================================================
// Keyboard Shortcut Types
// ============================================================================

export interface KeyboardShortcut {
  key: string
  description: string
  action: () => void
  meta?: boolean
  ctrl?: boolean
  shift?: boolean
  alt?: boolean
}

// ============================================================================
// Utility Types
// ============================================================================

export type Nullable<T> = T | null
export type Optional<T> = T | undefined
export type AsyncFunction<T = void> = () => Promise<T>
export type VoidFunction = () => void

// Type guards
export const isNote = (obj: unknown): obj is Note => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'title' in obj &&
    'content' in obj &&
    'user_id' in obj
  )
}

export const isApiError = (obj: unknown): obj is ApiError => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'error' in obj &&
    typeof (obj as ApiError).error === 'string'
  )
}
