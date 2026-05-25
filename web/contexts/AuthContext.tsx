'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { AuthUser } from '@/types'
import { login as apiLogin, getMe } from '@/lib/api'

interface AuthContextType {
  user: AuthUser | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setUserFromResponse: (user: AuthUser) => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const stored = localStorage.getItem('skout_token')
    if (stored) {
      setToken(stored)
      getMe(stored)
        .then(u => setUser(u))
        .catch(() => {
          localStorage.removeItem('skout_token')
          setToken(null)
        })
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    const res = await apiLogin(email, password)
    if (res.token) {
      localStorage.setItem('skout_token', res.token)
      setToken(res.token)
      setUser(res)
      if (res.role === 'creator') {
        router.push('/creator/dashboard')
      } else {
        router.push('/business/dashboard')
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('skout_token')
    setToken(null)
    setUser(null)
    router.push('/login')
  }

  const setUserFromResponse = (userData: AuthUser) => {
    if (userData.token) {
      localStorage.setItem('skout_token', userData.token)
      setToken(userData.token)
    }
    setUser(userData)
  }

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout, setUserFromResponse }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
