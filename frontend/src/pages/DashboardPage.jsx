import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FileText, Network, Search, Brain, AlertTriangle, TrendingUp, Tag } from 'lucide-react'
import { Link } from 'react-router-dom'
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import api from '../utils/api'
import toast from 'react-hot-toast'
import OctopusLoader from '../components/OctopusLoader'

const COLORS = ['#8b5cf6', '#ec4899', '#3b82f6', '#10b981', '#f59e0b', '#ef4444']

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState(null)
  const [trends, setTrends] = useState([])
  const [tagDistribution, setTagDistribution] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
    fetchTrends()
    fetchTagDistribution()
  }, [])

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/analytics/summary')
      setAnalytics(response.data)
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
      toast.error('Failed to load dashboard stats')
      setAnalytics({
        note_count: 0,
        total_words: 0,
        notes_this_week: 0,
        search_ready_percentage: 0,
        error: 'Unable to load stats'
      })
    } finally {
      setLoading(false)
    }
  }

  const fetchTrends = async () => {
    try {
      const response = await api.get('/analytics/trends?days=30')
      setTrends(response.data.trends || [])
    } catch (error) {
      console.error('Failed to fetch trends:', error)
    }
  }

  const fetchTagDistribution = async () => {
    try {
      const response = await api.get('/analytics/tags')
      setTagDistribution(response.data.tags?.slice(0, 6) || [])
    } catch (error) {
      console.error('Failed to fetch tag distribution:', error)
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <OctopusLoader size="lg" />
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-8"
      >
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2" style={{ color: 'var(--sb-text-primary)' }}>Welcome to SecondBrain</h1>
          <p style={{ color: 'var(--sb-text-secondary)' }}>Your AI-powered knowledge companion</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            icon={FileText}
            title="Total Notes"
            value={analytics?.note_count?.toString() || '0'}
            subtitle={`${analytics?.notes_this_week || 0} this week`}
            color="purple"
          />
          <StatCard
            icon={Brain}
            title="Total Words"
            value={analytics?.total_words?.toLocaleString() || '0'}
            subtitle={`${Math.round(analytics?.avg_note_length || 0)} avg per note`}
            color="blue"
          />
          <StatCard
            icon={Network}
            title="Search Ready"
            value={`${analytics?.search_ready_percentage || 0}%`}
            subtitle={`${analytics?.notes_with_embeddings || 0} of ${analytics?.note_count || 0} notes`}
            color="pink"
          />
          <StatCard
            icon={Search}
            title="Knowledge Graph"
            value={analytics?.note_count > 1 ? 'Active' : 'Pending'}
            subtitle={analytics?.note_count > 1 ? 'Ready to explore' : 'Add more notes'}
            color="green"
          />
        </div>

        {/* System Status */}
        {analytics?.error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass rounded-2xl p-4"
            style={{ border: '1px solid rgba(245, 158, 11, 0.3)' }}
          >
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-5 h-5" style={{ color: 'var(--sb-warning)' }} />
              <div>
                <h3 className="font-medium" style={{ color: 'var(--sb-warning)' }}>System Notice</h3>
                <p className="text-sm" style={{ color: 'var(--sb-text-secondary)' }}>Some features may be limited: {analytics.error}</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Creation Trends Chart */}
          <div className="glass rounded-2xl p-6" style={{ border: '1px solid var(--sb-border)', boxShadow: 'var(--sb-shadow-sm)' }}>
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5" style={{ color: 'var(--sb-secondary)' }} />
              <h2 className="text-xl font-bold" style={{ color: 'var(--sb-text-primary)' }}>30-Day Activity</h2>
            </div>
            {trends.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={trends}>
                  <XAxis 
                    dataKey="date" 
                    stroke="#6b7280"
                    fontSize={12}
                    tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis stroke="#6b7280" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(26, 26, 26, 0.95)',
                      border: '1px solid rgba(139, 92, 246, 0.3)',
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="count" 
                    stroke="#8b5cf6" 
                    strokeWidth={2}
                    dot={{ fill: '#8b5cf6', r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[250px] flex items-center justify-center" style={{ color: 'var(--sb-text-secondary)' }}>
                No activity data yet
              </div>
            )}
          </div>

          {/* Tag Distribution Chart */}
          <div className="glass rounded-2xl p-6" style={{ border: '1px solid var(--sb-border)', boxShadow: 'var(--sb-shadow-sm)' }}>
            <div className="flex items-center gap-2 mb-4">
              <Tag className="w-5 h-5" style={{ color: 'var(--sb-primary)' }} />
              <h2 className="text-xl font-bold" style={{ color: 'var(--sb-text-primary)' }}>Top Tags</h2>
            </div>
            {tagDistribution.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={tagDistribution}
                    dataKey="count"
                    nameKey="tag"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={({ tag, percent }) => `${tag} (${(percent * 100).toFixed(0)}%)`}
                    labelStyle={{ fill: '#fff', fontSize: 12 }}
                  >
                    {tagDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(26, 26, 26, 0.95)',
                      border: '1px solid rgba(139, 92, 246, 0.3)',
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[250px] flex items-center justify-center" style={{ color: 'var(--sb-text-secondary)' }}>
                No tags yet - add tags to your notes
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-2xl font-bold mb-6" style={{ color: 'var(--sb-text-primary)' }}>Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              to="/app/notes"
              className="neon-card p-6 rounded-xl group"
            >
              <FileText className="w-8 h-8 mb-2" style={{ color: 'var(--sb-primary)' }} />
              <h3 className="font-semibold mb-1" style={{ color: 'var(--sb-text-primary)' }}>Create Note</h3>
              <p className="text-sm" style={{ color: 'var(--sb-text-secondary)' }}>Start capturing your thoughts</p>
            </Link>
            <Link
              to="/app/map"
              className="neon-card-secondary p-6 rounded-xl group"
            >
              <Network className="w-8 h-8 mb-2" style={{ color: 'var(--sb-secondary)' }} />
              <h3 className="font-semibold mb-1" style={{ color: 'var(--sb-text-primary)' }}>View Map</h3>
              <p className="text-sm" style={{ color: 'var(--sb-text-secondary)' }}>Explore your neural network</p>
            </Link>
            <Link
              to="/app/search"
              className="neon-card-accent p-6 rounded-xl group"
            >
              <Search className="w-8 h-8 mb-2" style={{ color: 'var(--sb-accent)' }} />
              <h3 className="font-semibold mb-1" style={{ color: 'var(--sb-text-primary)' }}>Search</h3>
              <p className="text-sm" style={{ color: 'var(--sb-text-secondary)' }}>Find what you&apos;re looking for</p>
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

function StatCard({ icon: Icon, title, value, subtitle, color }) {
  const colors = {
    purple: 'var(--sb-secondary)',
    blue: 'var(--sb-info)',
    pink: 'var(--sb-primary)',
    green: 'var(--sb-success)',
  }

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="glass rounded-2xl p-6"
      style={{ border: '1px solid var(--sb-border)', boxShadow: 'var(--sb-shadow-sm)' }}
    >
      <div className="flex items-center justify-between mb-4">
        <div 
          className="p-3 rounded-lg"
          style={{ background: colors[color] }}
        >
          <Icon className="w-6 h-6" style={{ color: 'white' }} />
        </div>
      </div>
      <h3 className="text-sm mb-1" style={{ color: 'var(--sb-text-secondary)' }}>{title}</h3>
      <p className="text-3xl font-bold mb-1" style={{ color: 'var(--sb-text-primary)' }}>{value}</p>
      {subtitle && <p className="text-xs" style={{ color: 'var(--sb-text-tertiary)' }}>{subtitle}</p>}
    </motion.div>
  )
}
