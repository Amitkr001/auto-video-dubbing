import { Link } from 'react-router-dom'
import { Languages } from 'lucide-react'

function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl gradient-bg flex items-center justify-center">
              <Languages className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text">DubSync</span>
          </Link>

          <div className="flex items-center gap-6">
            <Link
              to="/"
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              Home
            </Link>
            <Link
              to="/upload"
              className="text-sm px-4 py-2 rounded-lg gradient-bg hover:opacity-90 transition-opacity font-medium"
            >
              Start Dubbing
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
