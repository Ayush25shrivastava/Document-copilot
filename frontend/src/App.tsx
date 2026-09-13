import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/lib/auth-context'
import AuthPage from '@/pages/Auth'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { session, loading } = useAuth()

  if (loading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>
  }

  if (!session) {
    return <Navigate to="/auth" replace />
  }

  return <>{children}</>
}

function MainLayout() {
  const { user } = useAuth()
  
  const handleLogout = async () => {
    await supabase.auth.signOut()
  }

  return (
    <div className="flex h-screen flex-col items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold">Document Copilot</h1>
        <p className="text-gray-500">Welcome, {user?.email}</p>
        <p className="text-sm">Chat interface coming soon...</p>
        <Button onClick={handleLogout} variant="outline" className="mt-4">
          Logout
        </Button>
      </div>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/auth" element={<AuthPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
