'use client'

import Link from 'next/link'
import { BarChart3, Plus } from 'lucide-react'

export default function CampaignsPage() {
  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Campaigns</h1>
          <p className="text-gray-500">Track your outreach campaigns and results.</p>
        </div>
        <Link href="/business/discover" className="btn-primary flex items-center gap-2 text-sm px-4 py-2.5">
          <Plus className="w-4 h-4" />
          New Campaign
        </Link>
      </div>

      <div className="text-center py-24">
        <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mx-auto mb-4">
          <BarChart3 className="w-7 h-7 text-gray-600" />
        </div>
        <p className="text-white font-medium mb-2">No campaigns yet</p>
        <p className="text-gray-500 text-sm mb-6 max-w-sm mx-auto">
          Start by discovering creators and sending outreach. Your campaigns will appear here.
        </p>
        <Link href="/business/discover" className="btn-primary text-sm">
          Discover Creators
        </Link>
      </div>
    </div>
  )
}
