'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import CreatorSidebar from '@/components/layout/CreatorSidebar'

export default function CreatorLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()
  const isOnboarding = pathname === '/creator/onboarding'

  useEffect(() => {
    if (!isLoading && !isOnboarding && (!user || user.role !== 'creator')) {
      router.push('/login')
    }
  }, [user, isLoading, router, isOnboarding])

  // Onboarding is public — no auth required, no sidebar
  if (isOnboarding) return <>{children}</>

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#FAFAFE] flex items-center justify-center">
        <div className="w-8 h-8 rounded-full border-2 border-[#E0E7FF] border-t-[#4F46E5] animate-spin" />
      </div>
    )
  }

  if (!user || user.role !== 'creator') return null

  return (
    <div className="min-h-screen bg-[#FAFAFE]">
      <CreatorSidebar />
      <main className="ml-60 min-h-screen">
        <div className="max-w-5xl mx-auto px-8 py-8">{children}</div>
      </main>
    </div>
  )
}
