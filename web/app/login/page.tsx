'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { useAuth } from '@/contexts/AuthContext'
import { APIError } from '@/lib/api'

export default function LoginPage() {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
    } catch (err) {
      setError(err instanceof APIError ? err.message : 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#FAFAFE] flex items-center justify-center px-4">
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div style={{ position: 'absolute', width: 650, height: 650, top: -200, right: -130, background: 'rgba(99,102,241,.12)', borderRadius: '50%', filter: 'blur(50px)' }} />
        <div style={{ position: 'absolute', width: 500, height: 500, bottom: -160, left: -100, background: 'rgba(139,92,246,.08)', borderRadius: '50%', filter: 'blur(50px)' }} />
      </div>

      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-block mb-6">
            <Image src="/skout-logo.png" alt="Skout" width={130} height={44} style={{ height: 44, width: 'auto', margin: '0 auto' }} />
          </Link>
          <h1 className="text-2xl font-bold text-[#1E1B4B] mb-1">Welcome back</h1>
          <p className="text-[#6B7280] text-sm">Sign in to your Skout account</p>
        </div>

        <div className="card p-8">
          {error && (
            <div className="mb-5 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Email</label>
              <input type="email" className="input" placeholder="you@example.com"
                value={email} onChange={e => setEmail(e.target.value)} required autoComplete="email" />
            </div>
            <div>
              <label className="label">Password</label>
              <input type="password" className="input" placeholder="••••••••"
                value={password} onChange={e => setPassword(e.target.value)} required autoComplete="current-password" />
            </div>
            <button type="submit" className="btn-primary w-full mt-2" disabled={loading}>
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>
        </div>

        <div className="text-center mt-6 space-y-2">
          <p className="text-[#6B7280] text-sm">
            Don&apos;t have an account?{' '}
            <Link href="/signup" className="text-[#4F46E5] font-semibold hover:text-[#4338CA] transition-colors">
              Sign up
            </Link>
          </p>
          <div className="flex gap-4 justify-center pt-1">
            <Link href="/creator/onboarding" className="text-[#6B7280] text-xs hover:text-[#4F46E5] transition-colors">
              Join as Creator →
            </Link>
            <Link href="/business/onboarding" className="text-[#6B7280] text-xs hover:text-[#4F46E5] transition-colors">
              Join as Business →
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
