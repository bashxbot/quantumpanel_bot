import { useEffect, useState } from 'react'

interface PremiumUser {
  id: number
  telegram_id: number
  username: string | null
  first_name: string | null
}

export default function PremiumUsers() {
  const [users, setUsers] = useState<PremiumUser[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newUserId, setNewUserId] = useState('')
  const [selectedUsers, setSelectedUsers] = useState<number[]>([])

  const fetchUsers = () => {
    fetch('/api/premium-users', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    })
      .then(res => res.json())
      .then(data => {
        setUsers(data.users || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  const handleAddUser = async () => {
    if (!newUserId.trim()) return
    
    await fetch('/api/premium-users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({ telegram_id: parseInt(newUserId) })
    })
    
    setNewUserId('')
    setShowAddModal(false)
    fetchUsers()
  }

  const handleRemoveUser = async (id: number) => {
    if (!confirm('Are you sure you want to remove premium from this user?')) return
    
    await fetch(`/api/premium-users/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    })
    
    fetchUsers()
  }

  const handleBulkRemove = async () => {
    if (selectedUsers.length === 0) return
    if (!confirm(`Remove premium from ${selectedUsers.length} users?`)) return
    
    await fetch('/api/premium-users/bulk-delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({ user_ids: selectedUsers })
    })
    
    setSelectedUsers([])
    fetchUsers()
  }

  const toggleSelectUser = (id: number) => {
    setSelectedUsers(prev =>
      prev.includes(id) ? prev.filter(u => u !== id) : [...prev, id]
    )
  }

  const toggleSelectAll = () => {
    if (selectedUsers.length === users.length) {
      setSelectedUsers([])
    } else {
      setSelectedUsers(users.map(u => u.id))
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Premium Users</h1>
          <p className="text-gray-400 mt-1">Manage premium subscriptions</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="px-4 py-2 rounded-lg btn-primary text-white">
          + Add Premium User
        </button>
      </div>

      <div className="glass-card p-1">
        <p className="text-gray-400 text-sm p-4">Total: {users.length} premium users</p>
      </div>

      {selectedUsers.length > 0 && (
        <div className="mt-4 p-4 glass-card flex items-center justify-between">
          <span className="text-white">{selectedUsers.length} users selected</span>
          <button onClick={handleBulkRemove} className="px-4 py-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30">
            Remove Selected
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      ) : (
        <div className="glass-card overflow-hidden mt-6">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedUsers.length === users.length && users.length > 0}
                    onChange={toggleSelectAll}
                    className="rounded"
                  />
                </th>
                <th className="px-4 py-3 text-left text-gray-400 font-medium">User</th>
                <th className="px-4 py-3 text-left text-gray-400 font-medium">Telegram ID</th>
                <th className="px-4 py-3 text-left text-gray-400 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-b border-white/5 hover:bg-white/5">
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedUsers.includes(user.id)}
                      onChange={() => toggleSelectUser(user.id)}
                      className="rounded"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center text-xl">⭐</div>
                      <div>
                        <p className="text-white">{user.first_name || 'Unknown'}</p>
                        {user.username && <p className="text-gray-400 text-sm">@{user.username}</p>}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <code className="text-primary-400">{user.telegram_id}</code>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleRemoveUser(user.id)}
                      className="text-red-400 hover:text-red-300 text-sm"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {users.length === 0 && (
            <div className="text-center py-12 text-gray-400">No premium users found</div>
          )}
        </div>
      )}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="glass-card p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">Add Premium User</h2>
            <input
              type="text"
              value={newUserId}
              onChange={(e) => setNewUserId(e.target.value)}
              className="w-full px-4 py-3 rounded-lg glass-input text-white placeholder-gray-500 focus:outline-none"
              placeholder="Telegram User ID"
            />
            <div className="flex justify-end gap-3 mt-4">
              <button onClick={() => setShowAddModal(false)} className="px-4 py-2 rounded-lg text-gray-400 hover:text-white">
                Cancel
              </button>
              <button onClick={handleAddUser} className="px-4 py-2 rounded-lg btn-primary text-white">
                Add User
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
