import { motion } from 'framer-motion'
import { Network } from 'lucide-react'

export default function NeuralMapPage() {
  return (
    <div className="p-8 h-full flex flex-col">
      <div className="mb-6">
        <h1 className="text-4xl font-bold text-white mb-2">Neural Map</h1>
        <p className="text-gray-400">Visualize connections between your notes</p>
      </div>

      {/* Neural Map Container */}
      <div className="flex-1 glass rounded-2xl flex items-center justify-center">
        <div className="text-center">
          <Network className="w-24 h-24 text-purple-400 mx-auto mb-4 opacity-50" />
          <h2 className="text-2xl font-semibold text-white mb-2">Neural Map Coming Soon</h2>
          <p className="text-gray-400">3D interactive visualization of your knowledge graph</p>
        </div>
      </div>
    </div>
  )
}
