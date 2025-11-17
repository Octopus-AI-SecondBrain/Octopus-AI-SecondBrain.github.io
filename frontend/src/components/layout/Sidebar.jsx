import { NavLink } from 'react-router-dom'
import { Home, FileText, Network, Search, Settings, Brain } from 'lucide-react'
import { motion } from 'framer-motion'
import OctopusIcon from '../OctopusIcon'

const navItems = [
  { to: '/app', icon: Home, label: 'Dashboard', end: true },
  { to: '/app/notes', icon: FileText, label: 'Notes' },
  { to: '/app/map', icon: Network, label: 'Neural Map' },
  { to: '/app/search', icon: Search, label: 'Search' },
  { to: '/app/knowledge', icon: Brain, label: 'Knowledge Base' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 glass flex flex-col" style={{ borderRight: '1px solid var(--sb-border)' }}>
      {/* Logo */}
      <div className="p-6" style={{ borderBottom: '1px solid var(--sb-border)' }}>
        <div className="flex items-center gap-3">
          <OctopusIcon size="md" animationStyle="pulse" style={{ color: 'var(--sb-primary)' }} />
          <div>
            <h1 className="text-xl font-bold" style={{ color: 'var(--sb-text-primary)' }}>Octopus</h1>
            <p className="text-xs" style={{ color: 'var(--sb-text-tertiary)' }}>Your Second Brain</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map(item => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  isActive ? 'neon-nav-link neon-nav-link-active' : 'neon-nav-link'
                }
              >
                {({ isActive }) => (
                  <>
                    <item.icon size={20} />
                    <span className="font-medium ml-3">{item.label}</span>
                    {isActive && (
                      <motion.div
                        layoutId="activeTab"
                        className="ml-auto w-1 h-6 rounded-full"
                        style={{ background: 'white' }}
                      />
                    )}
                  </>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Settings */}
      <div className="p-4" style={{ borderTop: '1px solid var(--sb-border)' }}>
        <NavLink
          to="/app/settings"
          className="neon-nav-link"
        >
          <Settings size={20} />
          <span className="font-medium ml-3">Settings</span>
        </NavLink>
      </div>
    </aside>
  )
}
