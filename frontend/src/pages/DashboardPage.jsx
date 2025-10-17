import { motion } from 'framer-motion'
import { FileText, Network, Search, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function DashboardPage() {
  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-8"
      >
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            icon={FileText}
            title="Total Notes"
            value="0"
            change="+0"
            color="purple"
          />
          <StatCard
            icon={Network}
            title="Connections"
            value="0"
            change="+0"
            color="blue"
          />
          <StatCard
            icon={Search}
            title="Searches"
            value="0"
            change="+0"
            color="pink"
          />
        </div>

        {/* Quick Actions */}
        <div className="glass rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-white mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              to="/app/notes"
              className="p-6 bg-white/5 rounded-xl hover:bg-white/10 transition-all group"
            >
              <FileText className="w-8 h-8 text-purple-400 mb-3 group-hover:scale-110 transition-transform" />
              <h3 className="font-semibold text-white mb-1">Create Note</h3>
              <p className="text-sm text-gray-400">Start capturing your thoughts</p>
            </Link>

            <Link
              to="/app/map"
              className="p-6 bg-white/5 rounded-xl hover:bg-white/10 transition-all group"
            >
              <Network className="w-8 h-8 text-blue-400 mb-3 group-hover:scale-110 transition-transform" />
              <h3 className="font-semibold text-white mb-1">View Map</h3>
              <p className="text-sm text-gray-400">Explore your neural network</p>
            </Link>

            <Link
              to="/app/search"
              className="p-6 bg-white/5 rounded-xl hover:bg-white/10 transition-all group"
            >
              <Search className="w-8 h-8 text-pink-400 mb-3 group-hover:scale-110 transition-transform" />
              <h3 className="font-semibold text-white mb-1">Search</h3>
              <p className="text-sm text-gray-400">Find what you're looking for</p>
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

function StatCard({ icon: Icon, title, value, change, color }) {
  const colors = {
    purple: 'from-purple-600 to-purple-400',
    blue: 'from-blue-600 to-blue-400',
    pink: 'from-pink-600 to-pink-400',
  }

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="glass rounded-2xl p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg bg-gradient-to-r ${colors[color]}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        <span className="text-sm text-green-400 flex items-center gap-1">
          <TrendingUp size={16} />
          {change}
        </span>
      </div>
      <h3 className="text-gray-400 text-sm mb-1">{title}</h3>
      <p className="text-3xl font-bold text-white">{value}</p>
    </motion.div>
  )
}
