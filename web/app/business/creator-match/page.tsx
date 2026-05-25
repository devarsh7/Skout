'use client'

import Link from 'next/link'
import { Target } from 'lucide-react'

export default function CreatorMatchPage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Creator Match</h1>
        <p className="text-gray-500">AI-powered matching based on your brand profile and goals.</p>
      </div>
      <div className="text-center py-24">
        <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mx-auto mb-4">
          <Target className="w-7 h-7 text-gray-600" />
        </div>
        <p className="text-white font-medium mb-2">Complete your brand profile first</p>
        <p className="text-gray-500 text-sm mb-6 max-w-sm mx-auto">
          Creator Match uses your industry, target audience, and budget to surface the most relevant creators.
        </p>
        <Link href="/business/onboarding" className="btn-primary text-sm">
          Complete Profile
        </Link>
      </div>
    </div>
  )
}
