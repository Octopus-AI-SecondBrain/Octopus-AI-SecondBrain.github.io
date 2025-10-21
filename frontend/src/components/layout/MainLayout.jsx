import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import Sidebar from './Sidebar'
import HealthIndicator from '../HealthIndicator'

export default function MainLayout() {
  return (
    <div 
      className="flex h-screen"
      style={{ background: 'var(--sb-bg-primary)' }}
    >
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
      <HealthIndicator />
    </div>
  )
}
