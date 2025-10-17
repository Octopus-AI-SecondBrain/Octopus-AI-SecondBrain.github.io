import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import { useAuth } from './hooks/useAuth'

// Pages
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import DashboardPage from './pages/DashboardPage'
import NotesPage from './pages/NotesPage'
import NeuralMapPage from './pages/NeuralMapPage'
import SearchPage from './pages/SearchPage'

// Layout
import MainLayout from './components/layout/MainLayout'

// Protected Route Component - moved inside AuthProvider context
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, initialized } = useAuth()

  if (loading || !initialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="loading-dots text-2xl">
          <span>.</span>
          <span>.</span>
          <span>.</span>
        </div>
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
        <div className="loading-dots text-2xl">
          <span>.</span>
          <span>.</span>
          <span>.</span>
        </div>
      </div>
    )
  }

  return isAuthenticated ? <Navigate to="/app" replace /> : children
}

// App Routes Component - this ensures ProtectedRoute is within AuthProvider
const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
      <Route path="/signup" element={<GuestRoute><SignupPage /></GuestRoute>} />

      {/* Protected Routes */}
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="notes" element={<NotesPage />} />
        <Route path="map" element={<NeuralMapPage />} />
        <Route path="search" element={<SearchPage />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="neural-bg" />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'rgba(26, 26, 26, 0.95)',
              color: '#fff',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              backdropFilter: 'blur(10px)',
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
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
