import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

interface LayoutProps {
  children: ReactNode
}

const menuItems = [
  { path: '/', label: 'Dashboard', icon: '📊' },
  { path: '/keys', label: 'Keys', icon: '🔑' },
  { path: '/products', label: 'Products', icon: '📦' },
  { path: '/admins', label: 'Admins', icon: '👑' },
  { path: '/premium-users', label: 'Premium Users', icon: '⭐' },
  { path: '/sellers', label: 'Sellers', icon: '🛒' },
  { path: '/web-users', label: 'Web Users', icon: '👤' },
]

export default function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth()
  const location = useLocation()

  return (
    <div className="min-h-screen flex">
      <aside className="w-64 glass-sidebar fixed h-full">
        <div className="p-6">
          <h1 className="text-2xl font-bold gradient-text">Quantum Panel</h1>
          <p className="text-gray-400 text-sm mt-1">Admin Dashboard</p>
        </div>
        
        <nav className="mt-6">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center px-6 py-3 text-sm transition-all ${
                location.pathname === item.path
                  ? 'bg-primary-500/20 border-r-2 border-primary-500 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <span className="mr-3 text-lg">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
        
        <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-white/10">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-white">{user?.username}</p>
              <p className="text-xs text-gray-400">Administrator</p>
            </div>
            <button
              onClick={logout}
              className="px-3 py-1 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition-all"
            >
              Logout
            </button>
          </div>
        </div>
      </aside>
      
      <main className="flex-1 ml-64 p-8">
        {children}
      </main>
    </div>
  )
}
