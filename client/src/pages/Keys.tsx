import { useEffect, useState } from 'react'

interface Key {
  id: number
  product_name: string
  key_value: string
  duration: string
  is_used: boolean
  created_at: string
}

interface Product {
  id: number
  name: string
}

export default function Keys() {
  const [keys, setKeys] = useState<Key[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedProduct, setSelectedProduct] = useState<number | null>(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newKeys, setNewKeys] = useState('')
  const [selectedKeys, setSelectedKeys] = useState<number[]>([])

  const fetchKeys = () => {
    const url = selectedProduct ? `/api/keys?product_id=${selectedProduct}` : '/api/keys'
    fetch(url, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    })
      .then(res => res.json())
      .then(data => {
        setKeys(data.keys || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  useEffect(() => {
    fetch('/api/products', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    })
      .then(res => res.json())
      .then(data => setProducts(data.products || []))
  }, [])

  useEffect(() => {
    fetchKeys()
  }, [selectedProduct])

  const handleAddKeys = async () => {
    if (!selectedProduct || !newKeys.trim()) return
    
    await fetch('/api/keys/bulk', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({ product_id: selectedProduct, keys: newKeys })
    })
    
    setNewKeys('')
    setShowAddModal(false)
    fetchKeys()
  }

  const handleDeleteSelected = async () => {
    if (selectedKeys.length === 0) return
    
    await fetch('/api/keys/bulk-delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({ key_ids: selectedKeys })
    })
    
    setSelectedKeys([])
    fetchKeys()
  }

  const handleDeleteAll = async () => {
    if (!selectedProduct) return
    if (!confirm('Are you sure you want to delete ALL keys for this product?')) return
    
    await fetch(`/api/keys/delete-all/${selectedProduct}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    })
    
    fetchKeys()
  }

  const handleDeleteClaimed = async () => {
    if (!selectedProduct) return
    if (!confirm('Are you sure you want to delete all CLAIMED keys?')) return
    
    await fetch(`/api/keys/delete-claimed/${selectedProduct}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    })
    
    fetchKeys()
  }

  const toggleSelectKey = (id: number) => {
    setSelectedKeys(prev =>
      prev.includes(id) ? prev.filter(k => k !== id) : [...prev, id]
    )
  }

  const toggleSelectAll = () => {
    if (selectedKeys.length === keys.length) {
      setSelectedKeys([])
    } else {
      setSelectedKeys(keys.map(k => k.id))
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Keys Management</h1>
          <p className="text-gray-400 mt-1">Manage product keys</p>
        </div>
        <div className="flex gap-3">
          <select
            value={selectedProduct || ''}
            onChange={(e) => setSelectedProduct(e.target.value ? Number(e.target.value) : null)}
            className="px-4 py-2 rounded-lg glass-input text-white"
          >
            <option value="">All Products</option>
            {products.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          {selectedProduct && (
            <>
              <button onClick={() => setShowAddModal(true)} className="px-4 py-2 rounded-lg btn-primary text-white">
                + Add Keys
              </button>
              <button onClick={handleDeleteClaimed} className="px-4 py-2 rounded-lg bg-orange-500/20 text-orange-400 hover:bg-orange-500/30">
                Delete Claimed
              </button>
              <button onClick={handleDeleteAll} className="px-4 py-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30">
                Delete All
              </button>
            </>
          )}
        </div>
      </div>

      {selectedKeys.length > 0 && (
        <div className="mb-4 p-4 glass-card flex items-center justify-between">
          <span className="text-white">{selectedKeys.length} keys selected</span>
          <button onClick={handleDeleteSelected} className="px-4 py-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30">
            Delete Selected
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      ) : (
        <div className="glass-card overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedKeys.length === keys.length && keys.length > 0}
                    onChange={toggleSelectAll}
                    className="rounded"
                  />
                </th>
                <th className="px-4 py-3 text-left text-gray-400 font-medium">Product</th>
                <th className="px-4 py-3 text-left text-gray-400 font-medium">Key</th>
                <th className="px-4 py-3 text-left text-gray-400 font-medium">Duration</th>
                <th className="px-4 py-3 text-left text-gray-400 font-medium">Status</th>
                <th className="px-4 py-3 text-left text-gray-400 font-medium">Created</th>
              </tr>
            </thead>
            <tbody>
              {keys.map((key) => (
                <tr key={key.id} className="border-b border-white/5 hover:bg-white/5">
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedKeys.includes(key.id)}
                      onChange={() => toggleSelectKey(key.id)}
                      className="rounded"
                    />
                  </td>
                  <td className="px-4 py-3 text-white">{key.product_name}</td>
                  <td className="px-4 py-3">
                    <code className="text-primary-400 bg-primary-500/10 px-2 py-1 rounded text-sm">
                      {key.key_value.slice(0, 30)}...
                    </code>
                  </td>
                  <td className="px-4 py-3 text-gray-300">{key.duration}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs ${key.is_used ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                      {key.is_used ? 'Used' : 'Available'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-sm">{new Date(key.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {keys.length === 0 && (
            <div className="text-center py-12 text-gray-400">No keys found</div>
          )}
        </div>
      )}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="glass-card p-6 w-full max-w-lg">
            <h2 className="text-xl font-bold text-white mb-4">Add Keys</h2>
            <p className="text-gray-400 text-sm mb-4">
              Format: duration key (e.g., "1d ABC123" or "7d XYZ789")
            </p>
            <textarea
              value={newKeys}
              onChange={(e) => setNewKeys(e.target.value)}
              className="w-full h-48 px-4 py-3 rounded-lg glass-input text-white placeholder-gray-500 focus:outline-none"
              placeholder="1d KEY123&#10;7d KEY456&#10;1m KEY789"
            />
            <div className="flex justify-end gap-3 mt-4">
              <button onClick={() => setShowAddModal(false)} className="px-4 py-2 rounded-lg text-gray-400 hover:text-white">
                Cancel
              </button>
              <button onClick={handleAddKeys} className="px-4 py-2 rounded-lg btn-primary text-white">
                Add Keys
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
