import { useEffect, useState } from 'react'

interface Stats {
  total_users: number
  premium_users: number
  total_keys: number
  available_keys: number
  used_keys: number
  total_products: number
  total_admins: number
  total_sellers: number
  total_orders: number
  total_revenue: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/stats', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    })
      .then(res => res.json())
      .then(data => {
        setStats(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  const statCards = [
    { label: 'Total Users', value: stats?.total_users || 0, icon: '👥', color: 'from-blue-500 to-cyan-500' },
    { label: 'Premium Users', value: stats?.premium_users || 0, icon: '⭐', color: 'from-yellow-500 to-orange-500' },
    { label: 'Total Keys', value: stats?.total_keys || 0, icon: '🔑', color: 'from-green-500 to-emerald-500' },
    { label: 'Available Keys', value: stats?.available_keys || 0, icon: '✅', color: 'from-teal-500 to-green-500' },
    { label: 'Used Keys', value: stats?.used_keys || 0, icon: '❌', color: 'from-red-500 to-pink-500' },
    { label: 'Products', value: stats?.total_products || 0, icon: '📦', color: 'from-purple-500 to-pink-500' },
    { label: 'Admins', value: stats?.total_admins || 0, icon: '👑', color: 'from-amber-500 to-yellow-500' },
    { label: 'Sellers', value: stats?.total_sellers || 0, icon: '🛒', color: 'from-indigo-500 to-purple-500' },
    { label: 'Total Orders', value: stats?.total_orders || 0, icon: '📋', color: 'from-cyan-500 to-blue-500' },
    { label: 'Revenue', value: `$${(stats?.total_revenue || 0).toFixed(2)}`, icon: '💰', color: 'from-green-400 to-emerald-600' },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-400 mt-1">Overview of your Quantum Panel</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
        {statCards.map((card, index) => (
          <div key={index} className="glass-card p-6 hover:scale-105 transition-transform">
            <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${card.color} flex items-center justify-center text-2xl mb-4`}>
              {card.icon}
            </div>
            <p className="text-gray-400 text-sm">{card.label}</p>
            <p className="text-2xl font-bold text-white mt-1">{card.value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
