import { NavLink } from 'react-router-dom'
import { Home, FileText, Network, Search, Settings } from 'lucide-react'
import { motion } from 'framer-motion'

const navItems = [
  { to: '/app', icon: Home, label: 'Dashboard', end: true },
  { to: '/app/notes', icon: FileText, label: 'Notes' },
  { to: '/app/map', icon: Network, label: 'Neural Map' },
  { to: '/app/search', icon: Search, label: 'Search' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 glass border-r border-white/10 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <span className="text-4xl">🐙</span>
          <div>
            <h1 className="text-xl font-bold text-white">Octopus</h1>
            <p className="text-xs text-gray-400">Your Second Brain</p>
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
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    isActive
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-400 hover:bg-white/5 hover:text-white'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <item.icon size={20} />
                    <span className="font-medium">{item.label}</span>
                    {isActive && (
                      <motion.div
                        layoutId="activeTab"
                        className="ml-auto w-1 h-6 bg-white rounded-full"
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
      <div className="p-4 border-t border-white/10">
        <NavLink
          to="/app/settings"
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-400 hover:bg-white/5 hover:text-white transition-all"
        >
          <Settings size={20} />
          <span className="font-medium">Settings</span>
        </NavLink>
      </div>
    </aside>
  )
}
