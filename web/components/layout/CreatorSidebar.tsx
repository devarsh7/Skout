'use client'

import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { LayoutDashboard, Sparkles, UserCog, Eye, LogOut } from 'lucide-react'
import clsx from 'clsx'

const nav = [
  { href: '/creator/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/creator/profile', icon: Eye, label: 'View Profile' },
  { href: '/creator/career-manager', icon: Sparkles, label: 'Career Manager' },
  { href: '/creator/update-profile', icon: UserCog, label: 'Edit Profile' },
]

export default function CreatorSidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuth()

  return (
    <aside className="fixed left-0 top-0 h-full w-60 bg-white border-r border-[#E2E8F0] flex flex-col z-40"
      style={{ boxShadow: '1px 0 8px rgba(15,23,42,0.04)' }}>

      <div className="px-5 py-4 border-b border-[#E2E8F0]">
        <Link href="/">
          <Image src="/skout-logo.png" alt="Skout" width={100} height={32} style={{ height: 32, width: 'auto' }} />
        </Link>
      </div>

      {user && (
        <div className="px-4 py-4 border-b border-[#E2E8F0]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 text-white text-sm font-bold"
              style={{ background: 'linear-gradient(135deg,#4F46E5,#7C3AED)' }}>
              {user.username.charAt(0).toUpperCase()}
            </div>
            <div>
              <div className="text-[#1E1B4B] text-sm font-bold truncate max-w-[140px]">{user.username}</div>
              <div className="text-[#4F46E5] text-xs font-semibold">Creator</div>
            </div>
          </div>
        </div>
      )}

      <nav className="flex-1 p-3 space-y-0.5">
        {nav.map(item => (
          <Link key={item.href} href={item.href}
            className={clsx(
              'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors',
              pathname === item.href
                ? 'bg-[#EEF2FF] text-[#4F46E5] font-semibold'
                : 'text-[#6B7280] hover:text-[#1E1B4B] hover:bg-[#F3F4FF]',
            )}>
            <item.icon className="w-4 h-4 flex-shrink-0" />
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="p-3 border-t border-[#E2E8F0]">
        <button onClick={logout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-[#9CA3AF] hover:text-red-500 hover:bg-red-50 transition-colors w-full font-medium">
          <LogOut className="w-4 h-4" />
          Log out
        </button>
      </div>
    </aside>
  )
}
