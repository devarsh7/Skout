'use client'

import Link from 'next/link'
import Image from 'next/image'
import { useAuth } from '@/contexts/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="fixed top-0 inset-x-0 z-50 border-b border-[#E2E8F0] bg-white/97 backdrop-blur-md"
      style={{ boxShadow: '0 1px 8px rgba(15,23,42,0.06)' }}>
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">

        <Link href="/" className="flex items-center">
          <Image src="/skout-logo.png" alt="Skout" width={120} height={40} style={{ height: 40, width: 'auto' }} priority />
        </Link>

        <div className="flex items-center gap-2">
          {user ? (
            <>
              <span className="badge hidden sm:inline-flex">
                {user.role === 'creator' ? '🎤' : '💼'} @{user.username}
              </span>
              <Link
                href={user.role === 'creator' ? '/creator/dashboard' : '/business/dashboard'}
                className="btn-ghost text-sm px-4 py-2"
              >
                Dashboard
              </Link>
              <button onClick={logout} className="text-[#9CA3AF] text-sm font-semibold hover:text-[#1E1B4B] transition-colors px-3 py-2">
                Log out
              </button>
            </>
          ) : (
            <>
              <Link href="/creator/onboarding"
                className="inline-flex items-center px-5 py-2 rounded-full text-sm font-bold text-[#4F46E5] border border-[#E0E7FF] hover:border-[#C7D2FE] transition-all"
                style={{ background: 'linear-gradient(135deg,rgba(99,102,241,.08),rgba(139,92,246,.11))' }}>
                Join as Creator
              </Link>
              <Link href="/business/onboarding"
                className="inline-flex items-center px-5 py-2 rounded-full text-sm font-bold text-white transition-all"
                style={{ background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', boxShadow: '0 4px 14px rgba(79,70,229,0.3)' }}>
                Join as Business
              </Link>
              <Link href="/login" className="text-[#9CA3AF] text-sm font-semibold hover:text-[#4F46E5] transition-colors px-3 py-2">
                Login
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
