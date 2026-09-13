import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { supabase } from '@/lib/supabase'
import { useAuth } from '@/lib/auth-context'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'

export default function AuthPage() {
  const { session, loading } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLogin, setIsLogin] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (loading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>
  }

  // Redirect if already authenticated
  if (session) {
    return <Navigate to="/" replace />
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setMessage(null)
    setIsSubmitting(true)

    try {
      if (isLogin) {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        })
        if (error) throw error
      } else {
        const { error, data } = await supabase.auth.signUp({
          email,
          password,
        })
        if (error) throw error
        
        if (data?.user && data?.session === null) {
          setMessage('Check your email for the confirmation link.')
        } else {
          setMessage('Account created successfully.')
        }
      }
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('An unexpected error occurred')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-white p-4 text-gray-900 font-sans">
      <div className="w-full max-w-[440px] rounded-2xl border border-gray-200/80 bg-white p-8 shadow-sm">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold tracking-tight text-[#111111] my-0">
            {isLogin ? 'Sign in' : 'Sign up'}
          </h1>
          <p className="mt-2 text-sm text-gray-500 font-normal">
            {isLogin
              ? 'Use your email and password to access Document Copilot.'
              : 'Create an account to access Document Copilot.'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {error && (
            <div className="rounded-xl bg-red-50 p-3 text-sm text-red-600 font-medium">
              {error}
            </div>
          )}
          {message && (
            <div className="rounded-xl bg-green-50 p-3 text-sm text-green-600 font-medium">
              {message}
            </div>
          )}

          <div className="space-y-1.5 text-left">
            <label htmlFor="email" className="text-sm font-semibold text-gray-800">
              Email
            </label>
            <input
              id="email"
              type="email"
              placeholder="dave@driftwood.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full h-11 rounded-xl border border-gray-200 px-3.5 text-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-400 transition"
            />
          </div>

          <div className="space-y-1.5 text-left">
            <label htmlFor="password" className="text-sm font-semibold text-gray-800">
              Password
            </label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full h-11 rounded-xl border border-gray-200 px-3.5 text-sm text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-400 transition"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full h-11 rounded-xl bg-[#373737] hover:bg-[#262626] text-white text-sm font-medium transition cursor-pointer disabled:opacity-50 mt-2"
          >
            {isSubmitting
              ? 'Please wait...'
              : isLogin
                ? 'Sign in'
                : 'Sign up'}
          </button>

          <div className="pt-1 text-center">
            <span className="text-sm text-gray-500 font-normal">
              {isLogin ? 'Need an account? ' : 'Already have an account? '}
            </span>
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin)
                setError(null)
                setMessage(null)
              }}
              className="text-sm font-semibold text-gray-900 hover:underline cursor-pointer"
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
