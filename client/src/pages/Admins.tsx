import { useEffect, useState } from 'react'

interface Admin {
  id: number
  telegram_id: number
  username: string | null
  name: string | null
  is_root: boolean
}

export default function Admins() {
  const [admins, setAdmins] = useState<Admin[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newAdminId, setNewAdminId] = useState('')

  const fetchAdmins = () => {
    fetch('/api/admins', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    })
      .then(res => res.json())
      .then(data => {
        setAdmins(data.admins || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  useEffect(() => {
    fetchAdmins()
  }, [])

  const handleAddAdmin = async () => {
    if (!newAdminId.trim()) return
    
    await fetch('/api/admins', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({ telegram_id: parseInt(newAdminId) })
    })
    
    setNewAdminId('')
    setShowAddModal(false)
    fetchAdmins()
  }

  const handleRemoveAdmin = async (id: number) => {
    if (!confirm('Are you sure you want to remove this admin?')) return
    
    await fetch(`/api/admins/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    })
    
    fetchAdmins()
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Admins</h1>
          <p className="text-gray-400 mt-1">Manage bot administrators</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="px-4 py-2 rounded-lg btn-primary text-white">
          + Add Admin
        </button>
      </div>

      <div className="glass-card p-1">
        <p className="text-gray-400 text-sm p-4">Total: {admins.length} admins</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
          {admins.map((admin) => (
            <div key={admin.id} className="glass-card p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl ${admin.is_root ? 'bg-yellow-500/20' : 'bg-primary-500/20'}`}>
                    {admin.is_root ? '👑' : '🔑'}
                  </div>
                  <div>
                    <p className="text-white font-medium">{admin.name || admin.username || `ID: ${admin.telegram_id}`}</p>
                    {admin.username && <p className="text-gray-400 text-sm">@{admin.username}</p>}
                    <p className="text-gray-500 text-xs mt-1">ID: {admin.telegram_id}</p>
                  </div>
                </div>
                {!admin.is_root && (
                  <button
                    onClick={() => handleRemoveAdmin(admin.id)}
                    className="text-red-400 hover:text-red-300 text-sm"
                  >
                    Remove
                  </button>
                )}
              </div>
              {admin.is_root && (
                <div className="mt-3 text-xs text-yellow-400 bg-yellow-500/10 px-2 py-1 rounded inline-block">
                  Root Admin
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="glass-card p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">Add Admin</h2>
            <input
              type="text"
              value={newAdminId}
              onChange={(e) => setNewAdminId(e.target.value)}
              className="w-full px-4 py-3 rounded-lg glass-input text-white placeholder-gray-500 focus:outline-none"
              placeholder="Telegram User ID"
            />
            <div className="flex justify-end gap-3 mt-4">
              <button onClick={() => setShowAddModal(false)} className="px-4 py-2 rounded-lg text-gray-400 hover:text-white">
                Cancel
              </button>
              <button onClick={handleAddAdmin} className="px-4 py-2 rounded-lg btn-primary text-white">
                Add Admin
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
