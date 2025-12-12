import { useEffect, useState } from 'react'

interface WebUser {
  id: number
  username: string
  is_admin: boolean
  created_at: string
}

export default function WebUsers() {
  const [users, setUsers] = useState<WebUser[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newUser, setNewUser] = useState({ username: '', password: '' })

  const fetchUsers = () => {
    fetch('/api/web-users', {
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
    if (!newUser.username.trim() || !newUser.password.trim()) return
    
    await fetch('/api/web-users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify(newUser)
    })
    
    setNewUser({ username: '', password: '' })
    setShowAddModal(false)
    fetchUsers()
  }

  const handleRemoveUser = async (id: number, username: string) => {
    if (username === 'admin') {
      alert('Cannot remove the default admin user')
      return
    }
    if (!confirm('Are you sure you want to remove this user?')) return
    
    await fetch(`/api/web-users/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    })
    
    fetchUsers()
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Web Users</h1>
          <p className="text-gray-400 mt-1">Manage web admin panel users</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="px-4 py-2 rounded-lg btn-primary text-white">
          + Add User
        </button>
      </div>

      <div className="glass-card p-1">
        <p className="text-gray-400 text-sm p-4">Total: {users.length} users</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      ) : (
        <div className="glass-card overflow-hidden mt-6">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="px-4 py-3 text-left text-gray-400 font-medium">User</th>
                <th className="px-4 py-3 text-left text-gray-400 font-medium">Role</th>
                <th className="px-4 py-3 text-left text-gray-400 font-medium">Created</th>
                <th className="px-4 py-3 text-left text-gray-400 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-b border-white/5 hover:bg-white/5">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-primary-500/20 flex items-center justify-center text-xl">👤</div>
                      <span className="text-white">{user.username}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs ${user.is_admin ? 'bg-yellow-500/20 text-yellow-400' : 'bg-blue-500/20 text-blue-400'}`}>
                      {user.is_admin ? 'Admin' : 'User'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-sm">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    {user.username !== 'admin' && (
                      <button
                        onClick={() => handleRemoveUser(user.id, user.username)}
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        Remove
                      </button>
                    )}
                    {user.username === 'admin' && (
                      <span className="text-gray-500 text-sm">Protected</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {users.length === 0 && (
            <div className="text-center py-12 text-gray-400">No users found</div>
          )}
        </div>
      )}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="glass-card p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">Add Web User</h2>
            <div className="space-y-4">
              <input
                type="text"
                value={newUser.username}
                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                className="w-full px-4 py-3 rounded-lg glass-input text-white placeholder-gray-500 focus:outline-none"
                placeholder="Username"
              />
              <input
                type="password"
                value={newUser.password}
                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                className="w-full px-4 py-3 rounded-lg glass-input text-white placeholder-gray-500 focus:outline-none"
                placeholder="Password"
              />
            </div>
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
