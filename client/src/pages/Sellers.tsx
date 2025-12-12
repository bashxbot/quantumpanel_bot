import { useEffect, useState } from 'react'

interface Seller {
  id: number
  username: string
  name: string | null
  country: string | null
  platforms: string | null
  is_active: boolean
}

export default function Sellers() {
  const [sellers, setSellers] = useState<Seller[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newSeller, setNewSeller] = useState({ username: '', name: '', country: '', platforms: '' })

  const fetchSellers = () => {
    fetch('/api/sellers', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    })
      .then(res => res.json())
      .then(data => {
        setSellers(data.sellers || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  useEffect(() => {
    fetchSellers()
  }, [])

  const handleAddSeller = async () => {
    if (!newSeller.username.trim()) return
    
    await fetch('/api/sellers', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify(newSeller)
    })
    
    setNewSeller({ username: '', name: '', country: '', platforms: '' })
    setShowAddModal(false)
    fetchSellers()
  }

  const handleToggleActive = async (id: number, currentState: boolean) => {
    await fetch(`/api/sellers/${id}/toggle`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({ is_active: !currentState })
    })
    
    fetchSellers()
  }

  const handleRemoveSeller = async (id: number) => {
    if (!confirm('Are you sure you want to remove this seller?')) return
    
    await fetch(`/api/sellers/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    })
    
    fetchSellers()
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Sellers</h1>
          <p className="text-gray-400 mt-1">Manage trusted sellers</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="px-4 py-2 rounded-lg btn-primary text-white">
          + Add Seller
        </button>
      </div>

      <div className="glass-card p-1">
        <p className="text-gray-400 text-sm p-4">Total: {sellers.length} sellers</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
          {sellers.map((seller) => (
            <div key={seller.id} className="glass-card p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-primary-500/20 flex items-center justify-center text-2xl">
                    🛒
                  </div>
                  <div>
                    <p className="text-white font-medium">{seller.name || seller.username}</p>
                    <p className="text-gray-400 text-sm">@{seller.username}</p>
                    {seller.country && <p className="text-gray-500 text-xs mt-1">{seller.country}</p>}
                  </div>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${seller.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                  {seller.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              
              {seller.platforms && (
                <div className="mt-3 text-sm text-gray-400">
                  <p className="text-xs text-gray-500 mb-1">Platforms:</p>
                  <p className="whitespace-pre-line">{seller.platforms}</p>
                </div>
              )}
              
              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => handleToggleActive(seller.id, seller.is_active)}
                  className={`px-3 py-1 rounded text-sm ${seller.is_active ? 'bg-orange-500/20 text-orange-400' : 'bg-green-500/20 text-green-400'}`}
                >
                  {seller.is_active ? 'Deactivate' : 'Activate'}
                </button>
                <button
                  onClick={() => handleRemoveSeller(seller.id)}
                  className="px-3 py-1 rounded text-sm bg-red-500/20 text-red-400"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="glass-card p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">Add Seller</h2>
            <div className="space-y-4">
              <input
                type="text"
                value={newSeller.username}
                onChange={(e) => setNewSeller({ ...newSeller, username: e.target.value })}
                className="w-full px-4 py-3 rounded-lg glass-input text-white placeholder-gray-500 focus:outline-none"
                placeholder="Telegram Username (without @)"
              />
              <input
                type="text"
                value={newSeller.name}
                onChange={(e) => setNewSeller({ ...newSeller, name: e.target.value })}
                className="w-full px-4 py-3 rounded-lg glass-input text-white placeholder-gray-500 focus:outline-none"
                placeholder="Display Name"
              />
              <input
                type="text"
                value={newSeller.country}
                onChange={(e) => setNewSeller({ ...newSeller, country: e.target.value })}
                className="w-full px-4 py-3 rounded-lg glass-input text-white placeholder-gray-500 focus:outline-none"
                placeholder="Country"
              />
              <textarea
                value={newSeller.platforms}
                onChange={(e) => setNewSeller({ ...newSeller, platforms: e.target.value })}
                className="w-full px-4 py-3 rounded-lg glass-input text-white placeholder-gray-500 focus:outline-none h-24"
                placeholder="Platforms (one per line)"
              />
            </div>
            <div className="flex justify-end gap-3 mt-4">
              <button onClick={() => setShowAddModal(false)} className="px-4 py-2 rounded-lg text-gray-400 hover:text-white">
                Cancel
              </button>
              <button onClick={handleAddSeller} className="px-4 py-2 rounded-lg btn-primary text-white">
                Add Seller
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
