import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Keys from './pages/Keys'
import Admins from './pages/Admins'
import PremiumUsers from './pages/PremiumUsers'
import Products from './pages/Products'
import Sellers from './pages/Sellers'
import WebUsers from './pages/WebUsers'
import Layout from './components/Layout'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth()
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }
  
  if (!user) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={
        <ProtectedRoute>
          <Layout>
            <Dashboard />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/keys" element={
        <ProtectedRoute>
          <Layout>
            <Keys />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/admins" element={
        <ProtectedRoute>
          <Layout>
            <Admins />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/premium-users" element={
        <ProtectedRoute>
          <Layout>
            <PremiumUsers />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/products" element={
        <ProtectedRoute>
          <Layout>
            <Products />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/sellers" element={
        <ProtectedRoute>
          <Layout>
            <Sellers />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/web-users" element={
        <ProtectedRoute>
          <Layout>
            <WebUsers />
          </Layout>
        </ProtectedRoute>
      } />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  )
}
