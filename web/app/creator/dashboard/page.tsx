'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { getCreator } from '@/lib/api'
import { Creator } from '@/types'
import {
  Users, TrendingUp, Eye, DollarSign, Sparkles,
  UserCog, Instagram, Youtube, Music2, Twitter, Globe, MapPin, Edit3, Share2,
} from 'lucide-react'

function fmt(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`
  return n > 0 ? String(n) : '—'
}

export default function CreatorDashboard() {
  const { user } = useAuth()
  const [creator, setCreator] = useState<Creator | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (user?.creator_id) {
      getCreator(user.creator_id).then(setCreator).catch(() => {})
    }
  }, [user])

  const totalFollowers =
    (creator?.instagram_followers ?? 0) +
    (creator?.tiktok_followers ?? 0) +
    (creator?.youtube_subscribers ?? 0)

  const completionFields = [
    creator?.bio,
    creator?.instagram_handle || creator?.tiktok_handle || creator?.youtube_channel,
    creator?.niches && creator.niches.length > 0,
    creator?.city,
    creator?.avg_engagement_rate,
  ]
  const completeness = Math.round(
    (completionFields.filter(Boolean).length / completionFields.length) * 100
  )

  const copyProfile = async () => {
    try {
      await navigator.clipboard.writeText(`${window.location.origin}/creator/profile`)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {}
  }

  const stats = [
    { label: 'Total Followers', value: fmt(totalFollowers), icon: Users, gradient: 'linear-gradient(135deg,#4F46E5,#7C3AED)' },
    { label: 'Avg Engagement', value: creator?.avg_engagement_rate ? `${creator.avg_engagement_rate.toFixed(1)}%` : '—', icon: TrendingUp, gradient: 'linear-gradient(135deg,#059669,#10B981)' },
    { label: 'Avg Views', value: fmt(creator?.avg_views ?? 0), icon: Eye, gradient: 'linear-gradient(135deg,#0EA5E9,#38BDF8)' },
    { label: 'Min Rate', value: creator?.min_rate_usd ? `$${creator.min_rate_usd.toLocaleString()}` : 'Not set', icon: DollarSign, gradient: 'linear-gradient(135deg,#D97706,#F59E0B)' },
  ]

  const platforms = [
    creator?.instagram_handle && { icon: Instagram, handle: creator.instagram_handle, followers: creator.instagram_followers, color: 'linear-gradient(135deg,#E1306C,#C13584)' },
    creator?.tiktok_handle && { icon: Music2, handle: creator.tiktok_handle, followers: creator.tiktok_followers, color: 'linear-gradient(135deg,#010101,#69C9D0)' },
    creator?.youtube_channel && { icon: Youtube, handle: creator.youtube_channel, followers: creator.youtube_subscribers, color: 'linear-gradient(135deg,#FF0000,#CC0000)' },
    creator?.twitter_handle && { icon: Twitter, handle: creator.twitter_handle, followers: 0, color: 'linear-gradient(135deg,#1DA1F2,#0D8BD9)' },
  ].filter(Boolean) as { icon: React.ElementType; handle: string; followers: number; color: string }[]

  const actions = [
    { href: '/creator/career-manager', icon: Sparkles, label: 'AI Career Manager', desc: 'Personalised growth advice, pitch templates and collab strategies.', gradient: 'linear-gradient(135deg,#4F46E5,#7C3AED)', color: '#4F46E5' },
    { href: '/creator/update-profile', icon: UserCog, label: 'Edit Profile', desc: 'Update stats, handles, niches and rates to attract better brand matches.', gradient: 'linear-gradient(135deg,#0EA5E9,#6366F1)', color: '#0EA5E9' },
    { href: '/creator/profile', icon: Eye, label: 'View Public Profile', desc: 'See exactly how brands discover and view your profile on Skout.', gradient: 'linear-gradient(135deg,#059669,#10B981)', color: '#059669' },
  ]

  return (
    <div className="space-y-5">

      {/* Hero */}
      <div className="relative overflow-hidden rounded-3xl p-7" style={{ background: 'linear-gradient(135deg,#4F46E5 0%,#7C3AED 60%,#8B5CF6 100%)', boxShadow: '0 8px 32px rgba(79,70,229,.28)' }}>
        <div className="pointer-events-none absolute -right-12 -top-20 h-72 w-72 rounded-full opacity-10 bg-white" />
        <div className="pointer-events-none absolute -bottom-16 -left-8 h-44 w-44 rounded-full opacity-[0.06] bg-white" />

        <div className="relative flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-2xl" style={{ background: 'rgba(255,255,255,.2)', border: '2px solid rgba(255,255,255,.35)' }}>
              <span className="text-2xl font-black text-white">
                {(creator?.display_name || user?.username || 'C').charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <div className="text-xl font-black text-white" style={{ letterSpacing: '-0.02em' }}>
                {creator?.display_name || user?.username}
              </div>
              {creator?.city && (
                <div className="mt-1 flex items-center gap-1 text-xs" style={{ color: 'rgba(255,255,255,.72)' }}>
                  <MapPin className="h-3 w-3" />
                  {creator.city}{creator.country ? `, ${creator.country}` : ''}
                </div>
              )}
              {creator?.niches && creator.niches.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {creator.niches.slice(0, 3).map(n => (
                    <span key={n} className="rounded-full px-2 py-0.5 text-[10.5px] font-bold text-white" style={{ background: 'rgba(255,255,255,.18)', border: '1px solid rgba(255,255,255,.28)' }}>
                      {n}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <Link href="/creator/profile" className="inline-flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-[12.5px] font-bold text-white no-underline" style={{ background: 'rgba(255,255,255,.16)', border: '1.5px solid rgba(255,255,255,.32)' }}>
              <Eye className="h-3 w-3" />View Profile
            </Link>
            <Link href="/creator/update-profile" className="inline-flex items-center gap-1.5 rounded-xl bg-white px-3.5 py-2 text-[12.5px] font-bold no-underline" style={{ color: '#4F46E5' }}>
              <Edit3 className="h-3 w-3" />Edit Profile
            </Link>
            <button onClick={copyProfile} className="inline-flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-[12.5px] font-bold text-white cursor-pointer border-0" style={{ background: 'rgba(255,255,255,.12)', border: '1.5px solid rgba(255,255,255,.22)' }}>
              <Share2 className="h-3 w-3" />{copied ? 'Copied!' : 'Share'}
            </button>
          </div>
        </div>

        {/* Completion bar */}
        <div className="relative mt-5">
          <div className="mb-1.5 flex justify-between">
            <span className="text-[10.5px] font-bold uppercase tracking-widest" style={{ color: 'rgba(255,255,255,.65)' }}>Profile Completion</span>
            <span className="text-xs font-black text-white">{completeness}%</span>
          </div>
          <div className="h-1.5 rounded-full" style={{ background: 'rgba(255,255,255,.18)' }}>
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{ width: `${completeness}%`, background: completeness === 100 ? '#34D399' : 'rgba(255,255,255,.85)' }}
            />
          </div>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-4 gap-3">
        {stats.map(s => (
          <div key={s.label} className="rounded-[18px] bg-white p-5" style={{ border: '1.5px solid #E0E7FF', boxShadow: '0 4px 16px rgba(79,70,229,.08)' }}>
            <div className="mb-3 flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-widest" style={{ color: '#9CA3AF' }}>{s.label}</span>
              <div className="flex h-8 w-8 items-center justify-center rounded-[9px]" style={{ background: s.gradient }}>
                <s.icon className="h-3.5 w-3.5 text-white" />
              </div>
            </div>
            <div className="text-[1.7rem] font-black leading-none" style={{ color: '#1E1B4B', letterSpacing: '-0.03em' }}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Connected platforms */}
      {platforms.length > 0 && (
        <div className="rounded-[20px] bg-white p-5" style={{ border: '1.5px solid #E0E7FF', boxShadow: '0 4px 16px rgba(79,70,229,.06)' }}>
          <div className="mb-3 text-[10.5px] font-bold uppercase tracking-widest" style={{ color: '#9CA3AF' }}>Connected Platforms</div>
          <div className="grid gap-2" style={{ gridTemplateColumns: 'repeat(auto-fill,minmax(200px,1fr))' }}>
            {platforms.map((p, i) => (
              <div key={i} className="flex items-center justify-between rounded-xl p-2.5" style={{ background: '#F8FAFF', border: '1px solid #E0E7FF' }}>
                <div className="flex items-center gap-2.5">
                  <div className="flex h-8 w-8 items-center justify-center rounded-[9px]" style={{ background: p.color }}>
                    <p.icon className="h-3.5 w-3.5 text-white" />
                  </div>
                  <span className="text-sm font-semibold" style={{ color: '#1E1B4B' }}>@{p.handle}</span>
                </div>
                {p.followers > 0 && <span className="text-sm font-extrabold" style={{ color: '#4F46E5' }}>{fmt(p.followers)}</span>}
              </div>
            ))}
          </div>
          {creator?.website && (
            <a href={creator.website} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-1.5 text-[12.5px] font-semibold no-underline" style={{ color: '#4F46E5' }}>
              <Globe className="h-3 w-3" />{creator.website.replace(/^https?:\/\//, '')}
            </a>
          )}
        </div>
      )}

      {/* Action cards */}
      <div className="grid grid-cols-3 gap-4">
        {actions.map(a => (
          <ActionCard key={a.href} {...a} />
        ))}
      </div>
    </div>
  )
}

function ActionCard({ href, icon: Icon, label, desc, gradient, color }: {
  href: string; icon: React.ElementType; label: string; desc: string; gradient: string; color: string
}) {
  const [pressed, setPressed] = useState(false)
  return (
    <Link
      href={href}
      onMouseDown={() => setPressed(true)}
      onMouseUp={() => setPressed(false)}
      onMouseLeave={() => setPressed(false)}
      className="relative block overflow-hidden rounded-[20px] bg-white no-underline"
      style={{
        border: '1.5px solid #E0E7FF',
        boxShadow: pressed ? '0 2px 8px rgba(79,70,229,.06)' : '0 6px 24px rgba(79,70,229,.1)',
        transform: pressed ? 'scale(0.95) translateY(2px)' : 'scale(1)',
        transition: 'all 0.2s cubic-bezier(.34,1.56,.64,1)',
        padding: '1.4rem',
      }}
    >
      <div className="pointer-events-none absolute inset-0 rounded-[20px]" style={{ background: 'linear-gradient(135deg,rgba(238,242,255,.5) 0%,transparent 60%)' }} />
      <div className="relative">
        <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-[13px]" style={{ background: gradient, boxShadow: '0 4px 12px rgba(79,70,229,.22)' }}>
          <Icon className="h-5 w-5 text-white" />
        </div>
        <div className="mb-1 text-[0.95rem] font-extrabold" style={{ color: '#1E1B4B' }}>{label}</div>
        <div className="mb-3 text-[0.8rem] leading-relaxed" style={{ color: '#6B7280' }}>{desc}</div>
        <div className="text-[0.8rem] font-bold" style={{ color }}>Open →</div>
      </div>
    </Link>
  )
}
