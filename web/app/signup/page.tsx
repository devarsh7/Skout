'use client'

import Link from 'next/link'
import Image from 'next/image'
import { Building2, Mic2 } from 'lucide-react'

export default function SignupPage() {
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
          <h1 className="text-2xl font-bold text-[#1E1B4B] mb-1">Join Skout</h1>
          <p className="text-[#6B7280] text-sm">Choose how you want to use Skout</p>
        </div>

        <div className="space-y-4">
          <Link href="/business/onboarding"
            className="card p-7 hover:border-[#C7D2FE] hover:shadow-md transition-all group block"
            style={{ textDecoration: 'none' }}>
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors"
                style={{ background: 'linear-gradient(135deg,rgba(79,70,229,.1),rgba(124,58,237,.14))', border: '1.5px solid rgba(79,70,229,.2)' }}>
                <Building2 className="w-6 h-6 text-[#4F46E5]" />
              </div>
              <div>
                <div className="text-[#1E1B4B] font-bold text-lg mb-1">I&apos;m a Brand / Agency</div>
                <div className="text-[#6B7280] text-sm leading-relaxed">
                  Discover creators, run campaigns, and track ROI with AI-powered tools.
                </div>
                <div className="text-[#4F46E5] text-sm mt-3 font-bold group-hover:translate-x-1 transition-transform inline-block">
                  Get started →
                </div>
              </div>
            </div>
          </Link>

          <Link href="/creator/onboarding"
            className="card p-7 hover:border-[#DDD6FE] hover:shadow-md transition-all group block"
            style={{ textDecoration: 'none' }}>
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors"
                style={{ background: 'linear-gradient(135deg,rgba(124,58,237,.1),rgba(139,92,246,.14))', border: '1.5px solid rgba(124,58,237,.2)' }}>
                <Mic2 className="w-6 h-6 text-[#7C3AED]" />
              </div>
              <div>
                <div className="text-[#1E1B4B] font-bold text-lg mb-1">I&apos;m a Creator</div>
                <div className="text-[#6B7280] text-sm leading-relaxed">
                  Get discovered by brands, manage collabs, and grow your career with AI.
                </div>
                <div className="text-[#7C3AED] text-sm mt-3 font-bold group-hover:translate-x-1 transition-transform inline-block">
                  Join for free →
                </div>
              </div>
            </div>
          </Link>
        </div>

        <p className="text-center text-[#6B7280] text-sm mt-6">
          Already have an account?{' '}
          <Link href="/login" className="text-[#4F46E5] font-semibold hover:text-[#4338CA] transition-colors">
            Log in
          </Link>
        </p>
      </div>
    </div>
  )
}
