import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import { useAuth } from './hooks/useAuth'
import { useState, lazy, Suspense } from 'react'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'
import OctopusLoader from './components/OctopusLoader'

// Layout and components
import MainLayout from './components/layout/MainLayout'

// Landing page - loaded immediately
import LandingPage from './pages/LandingPage'

// Lazy load pages for better performance
const LoginPage = lazy(() => import('./pages/LoginPage'))
const SignupPage = lazy(() => import('./pages/SignupPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const NotesPage = lazy(() => import('./pages/NotesPage'))
const NeuralMapPage = lazy(() => import('./pages/NeuralMapPage'))
const SearchPage = lazy(() => import('./pages/SearchPage'))
const SettingsPage = lazy(() => import('./pages/SettingsPage'))
const RAGPage = lazy(() => import('./pages/RAGPage'))
const KeyboardShortcutsModal = lazy(() => import('./components/KeyboardShortcutsModal'))

// Loading fallback component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen">
    <OctopusLoader size="lg" />
  </div>
)

// Protected Route Component - moved inside AuthProvider context
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, initialized } = useAuth()

  if (loading || !initialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <OctopusLoader size="lg" />
      </div>
    )
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />
}

// Redirect authenticated users away from auth pages
const GuestRoute = ({ children }) => {
  const { isAuthenticated, loading, initialized } = useAuth()

  if (loading || !initialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <OctopusLoader size="lg" />
      </div>
    )
  }

  return isAuthenticated ? <Navigate to="/app" replace /> : children
}

// App Routes Component - this ensures ProtectedRoute is within AuthProvider
const AppRoutes = () => {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const [showShortcuts, setShowShortcuts] = useState(false)

  // Global keyboard shortcuts
  useKeyboardShortcuts([
    {
      key: 'k',
      modifier: 'cmd',
      action: () => {
        if (isAuthenticated) {
          navigate('/app/search')
        }
      },
    },
    {
      key: 'n',
      modifier: 'cmd',
      action: () => {
        if (isAuthenticated) {
          navigate('/app/notes')
          // Trigger new note creation via custom event
          window.dispatchEvent(new CustomEvent('create-note'))
        }
      },
    },
    {
      key: '/',
      modifier: 'cmd',
      action: () => {
        setShowShortcuts(true)
      },
    },
  ])

  return (
    <>
      <Suspense fallback={<PageLoader />}>
        <KeyboardShortcutsModal isOpen={showShortcuts} onClose={() => setShowShortcuts(false)} />
      </Suspense>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route 
          path="/login" 
          element={
            <GuestRoute>
              <Suspense fallback={<PageLoader />}>
                <LoginPage />
              </Suspense>
            </GuestRoute>
          } 
        />
        <Route 
          path="/signup" 
          element={
            <GuestRoute>
              <Suspense fallback={<PageLoader />}>
                <SignupPage />
              </Suspense>
            </GuestRoute>
          } 
        />

        {/* Protected Routes */}
        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route 
            index 
            element={
              <Suspense fallback={<PageLoader />}>
                <DashboardPage />
              </Suspense>
            } 
          />
          <Route 
            path="notes" 
            element={
              <Suspense fallback={<PageLoader />}>
                <NotesPage />
              </Suspense>
            } 
          />
          <Route 
            path="map" 
            element={
              <Suspense fallback={<PageLoader />}>
                <NeuralMapPage />
              </Suspense>
            } 
          />
          <Route 
            path="search" 
            element={
              <Suspense fallback={<PageLoader />}>
                <SearchPage />
              </Suspense>
            } 
          />
          <Route 
            path="settings" 
            element={
              <Suspense fallback={<PageLoader />}>
                <SettingsPage />
              </Suspense>
            } 
          />
          <Route 
            path="knowledge" 
            element={
              <Suspense fallback={<PageLoader />}>
                <RAGPage />
              </Suspense>
            } 
          />
        </Route>

        {/* 404 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

function App() {
  // Get base path from Vite config (set via import.meta.env.BASE_URL)
  const basename = import.meta.env.BASE_URL || '/'
  
  return (
    <ThemeProvider>
      <Router basename={basename}>
        <div className="neural-bg" />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'var(--sb-surface)',
              color: 'var(--sb-text-primary)',
              border: '1px solid var(--sb-border)',
              backdropFilter: 'blur(10px)',
            },
            success: {
              iconTheme: {
                primary: 'var(--sb-success)',
                secondary: 'var(--sb-surface)',
              },
            },
            error: {
              iconTheme: {
                primary: 'var(--sb-error)',
                secondary: 'var(--sb-surface)',
              },
            },
          }}
        />
        
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </Router>
    </ThemeProvider>
  )
}

export default App
