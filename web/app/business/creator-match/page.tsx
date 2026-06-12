'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { Target, MapPin, Loader2 } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { listCreators } from '@/lib/api'
import { Creator } from '@/types'

function fmt(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`
  return String(n)
}

function CreatorCard({ c }: { c: Creator }) {
  const total = (c.instagram_followers || 0) + (c.tiktok_followers || 0) + (c.youtube_subscribers || 0)
  return (
    <div className="rounded-2xl bg-white p-5" style={{ border: '1.5px solid #E0E7FF', boxShadow: '0 2px 10px rgba(79,70,229,.05)' }}>
      <div className="flex items-center gap-3 mb-3">
        <div
          className="w-11 h-11 rounded-full flex items-center justify-center text-white font-bold text-base flex-shrink-0"
          style={{ background: 'linear-gradient(135deg,#4F46E5,#7C3AED)' }}
        >
          {(c.display_name || c.full_name).charAt(0).toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-bold text-sm text-[#1E1B4B] truncate">{c.display_name || c.full_name}</div>
          {(c.city || c.country) && (
            <div className="flex items-center gap-1 text-xs text-[#6B7280]">
              <MapPin className="w-3 h-3" />{c.city ? `${c.city}, ${c.country}` : c.country}
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4 mb-3">
        <div>
          <div className="text-sm font-extrabold text-[#1E1B4B]">{fmt(total)}</div>
          <div className="text-[10.5px] text-[#9CA3AF]">Followers</div>
        </div>
        {c.avg_engagement_rate > 0 && (
          <div>
            <div className="text-sm font-extrabold text-[#1E1B4B]">{c.avg_engagement_rate.toFixed(1)}%</div>
            <div className="text-[10.5px] text-[#9CA3AF]">Engagement</div>
          </div>
        )}
        {c.open_to_collabs && (
          <span className="ml-auto text-[10.5px] font-semibold px-2 py-0.5 rounded-full" style={{ background: '#DCFCE7', color: '#166534' }}>
            Open to collabs
          </span>
        )}
      </div>

      {c.niches.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {c.niches.slice(0, 4).map(n => (
            <span key={n} className="text-[10.5px] px-2 py-0.5 rounded-full font-semibold" style={{ background: '#EEF2FF', color: '#4F46E5' }}>{n}</span>
          ))}
        </div>
      )}

      {c.instagram_handle && (
        <div className="text-xs text-[#6B7280]">📸 @{c.instagram_handle}</div>
      )}
      {c.tiktok_handle && (
        <div className="text-xs text-[#6B7280]">🎵 @{c.tiktok_handle}</div>
      )}
    </div>
  )
}

export default function CreatorMatchPage() {
  const { user } = useAuth()
  const meta = user?.profile_meta as Record<string, string> | undefined
  const hasProfile = Boolean(meta?.company_name)

  const [creators, setCreators] = useState<Creator[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (hasProfile) {
      setLoading(true)
      listCreators(50).then(setCreators).catch(() => {}).finally(() => setLoading(false))
    }
  }, [hasProfile])

  if (!hasProfile) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-[#1E1B4B] mb-1">Creator Match</h1>
          <p className="text-[#6B7280] text-sm">AI-powered matching based on your brand profile and goals.</p>
        </div>
        <div className="text-center py-20 rounded-3xl" style={{ background: '#F8F9FF', border: '1.5px solid #E0E7FF' }}>
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4" style={{ background: 'linear-gradient(135deg,#EEF2FF,#E0E7FF)' }}>
            <Target className="w-7 h-7 text-[#4F46E5]" />
          </div>
          <p className="font-bold text-[#1E1B4B] mb-2">Set up your brand profile first</p>
          <p className="text-[#6B7280] text-sm mb-6 max-w-sm mx-auto">
            Creator Match uses your industry, target audience, and budget to surface the most relevant creators for your campaigns.
          </p>
          <Link
            href="/business/onboarding"
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold text-white no-underline"
            style={{ background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', boxShadow: '0 4px 14px rgba(79,70,229,.3)' }}
          >
            Complete Brand Profile →
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-[#1E1B4B] mb-1">Creator Match</h1>
        <p className="text-[#6B7280] text-sm">
          Creators matched for <span className="font-semibold text-[#4F46E5]">{meta?.company_name}</span>
          {meta?.industry && <span> · {meta.industry}</span>}
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="w-7 h-7 animate-spin text-[#4F46E5]" />
        </div>
      ) : creators.length === 0 ? (
        <div className="text-center py-20 text-[#6B7280] text-sm">No creators found. Check back soon.</div>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          {creators.map(c => <CreatorCard key={c.id} c={c} />)}
        </div>
      )}
    </div>
  )
}
