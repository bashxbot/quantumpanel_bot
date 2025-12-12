import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)
    
    const success = await login(username, password)
    setIsLoading(false)
    
    if (success) {
      navigate('/')
    } else {
      setError('Invalid username or password')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-500/20 rounded-full blur-3xl animate-float"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
      </div>
      
      <div className="glass-card p-8 w-full max-w-md relative z-10">
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center text-4xl">
            🤖
          </div>
          <h1 className="text-3xl font-bold gradient-text">Quantum Panel</h1>
          <p className="text-gray-400 mt-2">Web Admin Dashboard</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3 text-red-300 text-sm text-center">
              {error}
            </div>
          )}
          
          <div>
            <label className="block text-sm text-gray-400 mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 rounded-lg glass-input text-white placeholder-gray-500 focus:outline-none transition-all"
              placeholder="Enter username"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-400 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-lg glass-input text-white placeholder-gray-500 focus:outline-none transition-all"
              placeholder="Enter password"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 rounded-lg btn-primary text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        
        <p className="text-center text-gray-500 text-sm mt-6">
          Secure Admin Access Only
        </p>
      </div>
    </div>
  )
}
