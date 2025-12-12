import { useEffect, useState } from 'react'

interface Product {
  id: number
  name: string
  description: string | null
  is_active: boolean
  keys_count: number
  available_keys: number
}

export default function Products() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newProduct, setNewProduct] = useState({ name: '', description: '' })

  const fetchProducts = () => {
    fetch('/api/products', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    })
      .then(res => res.json())
      .then(data => {
        setProducts(data.products || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  useEffect(() => {
    fetchProducts()
  }, [])

  const handleAddProduct = async () => {
    if (!newProduct.name.trim()) return
    
    await fetch('/api/products', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify(newProduct)
    })
    
    setNewProduct({ name: '', description: '' })
    setShowAddModal(false)
    fetchProducts()
  }

  const handleToggleActive = async (id: number, currentState: boolean) => {
    await fetch(`/api/products/${id}/toggle`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({ is_active: !currentState })
    })
    
    fetchProducts()
  }

  const handleDeleteProduct = async (id: number) => {
    if (!confirm('Are you sure? This will also delete all keys for this product!')) return
    
    await fetch(`/api/products/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    })
    
    fetchProducts()
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Products</h1>
          <p className="text-gray-400 mt-1">Manage your products</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="px-4 py-2 rounded-lg btn-primary text-white">
          + Add Product
        </button>
      </div>

      <div className="glass-card p-1">
        <p className="text-gray-400 text-sm p-4">Total: {products.length} products</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
          {products.map((product) => (
            <div key={product.id} className="glass-card p-6">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">📦</span>
                    <h3 className="text-lg font-bold text-white">{product.name}</h3>
                  </div>
                  {product.description && (
                    <p className="text-gray-400 text-sm mt-2 line-clamp-2">{product.description}</p>
                  )}
                </div>
                <span className={`px-2 py-1 rounded text-xs ${product.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                  {product.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              
              <div className="mt-4 flex gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Total Keys:</span>
                  <span className="text-white ml-1">{product.keys_count}</span>
                </div>
                <div>
                  <span className="text-gray-400">Available:</span>
                  <span className="text-green-400 ml-1">{product.available_keys}</span>
                </div>
              </div>
              
              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => handleToggleActive(product.id, product.is_active)}
                  className={`px-3 py-1 rounded text-sm ${product.is_active ? 'bg-orange-500/20 text-orange-400' : 'bg-green-500/20 text-green-400'}`}
                >
                  {product.is_active ? 'Deactivate' : 'Activate'}
                </button>
                <button
                  onClick={() => handleDeleteProduct(product.id)}
                  className="px-3 py-1 rounded text-sm bg-red-500/20 text-red-400"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="glass-card p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">Add Product</h2>
            <div className="space-y-4">
              <input
                type="text"
                value={newProduct.name}
                onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
                className="w-full px-4 py-3 rounded-lg glass-input text-white placeholder-gray-500 focus:outline-none"
                placeholder="Product Name"
              />
              <textarea
                value={newProduct.description}
                onChange={(e) => setNewProduct({ ...newProduct, description: e.target.value })}
                className="w-full px-4 py-3 rounded-lg glass-input text-white placeholder-gray-500 focus:outline-none h-24"
                placeholder="Description (optional)"
              />
            </div>
            <div className="flex justify-end gap-3 mt-4">
              <button onClick={() => setShowAddModal(false)} className="px-4 py-2 rounded-lg text-gray-400 hover:text-white">
                Cancel
              </button>
              <button onClick={handleAddProduct} className="px-4 py-2 rounded-lg btn-primary text-white">
                Add Product
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
