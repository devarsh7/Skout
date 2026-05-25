'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { getCreator } from '@/lib/api'
import { Creator } from '@/types'
import {
  Users, TrendingUp, Eye, DollarSign,
  Sparkles, UserCog, Instagram, Youtube, Music2,
  Twitter, Globe, MapPin, Edit3, Share2,
} from 'lucide-react'

function fmt(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`
  return n > 0 ? String(n) : '—'
}

function StatCard({ label, value, icon: Icon, gradient }: {
  label: string; value: string; icon: React.ElementType; gradient: string
}) {
  const [pressed, setPressed] = useState(false)
  return (
    <div
      onMouseDown={() => setPressed(true)}
      onMouseUp={() => setPressed(false)}
      onMouseLeave={() => setPressed(false)}
      style={{
        background: '#fff', border: '1.5px solid #E0E7FF', borderRadius: 18, padding: '1.25rem',
        boxShadow: pressed ? '0 1px 4px rgba(79,70,229,.06)' : '0 4px 16px rgba(79,70,229,.08)',
        transform: pressed ? 'scale(0.96)' : 'scale(1)',
        transition: 'all 0.18s cubic-bezier(.34,1.56,.64,1)', cursor: 'default',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
        <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#9CA3AF' }}>{label}</div>
        <div style={{ width: 32, height: 32, borderRadius: 9, background: gradient, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon style={{ width: 15, height: 15, color: '#fff' }} />
        </div>
      </div>
      <div style={{ fontSize: '1.7rem', fontWeight: 900, color: '#1E1B4B', letterSpacing: '-0.03em', lineHeight: 1 }}>{value}</div>
    </div>
  )
}

function ActionCard({ href, icon: Icon, label, desc, gradient, arrowColor }: {
  href: string; icon: React.ElementType; label: string; desc: string; gradient: string; arrowColor: string
}) {
  const [pressed, setPressed] = useState(false)
  return (
    <Link href={href}
      onMouseDown={() => setPressed(true)}
      onMouseUp={() => setPressed(false)}
      onMouseLeave={() => setPressed(false)}
      style={{
        display: 'block', background: '#fff', border: '1.5px solid #E0E7FF', borderRadius: 20,
        padding: '1.4rem',
        boxShadow: pressed ? '0 2px 8px rgba(79,70,229,.06)' : '0 6px 24px rgba(79,70,229,.1)',
        transform: pressed ? 'scale(0.95) translateY(2px)' : 'scale(1) translateY(0)',
        transition: 'all 0.2s cubic-bezier(.34,1.56,.64,1)', textDecoration: 'none',
        position: 'relative', overflow: 'hidden',
      }}>
      <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg,rgba(238,242,255,.5) 0%,transparent 60%)', borderRadius: 20, pointerEvents: 'none' }} />
      <div style={{ position: 'relative' }}>
        <div style={{ width: 44, height: 44, borderRadius: 13, background: gradient, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 12, boxShadow: '0 4px 12px rgba(79,70,229,.22)' }}>
          <Icon style={{ width: 20, height: 20, color: '#fff' }} />
        </div>
        <div style={{ fontWeight: 800, fontSize: '0.95rem', color: '#1E1B4B', marginBottom: 4 }}>{label}</div>
        <div style={{ fontSize: '0.8rem', color: '#6B7280', lineHeight: 1.6, marginBottom: 12 }}>{desc}</div>
        <div style={{ fontSize: '0.8rem', fontWeight: 700, color: arrowColor }}>Open →</div>
      </div>
    </Link>
  )
}

function PlatformRow({ icon: Icon, handle, followers, color }: { icon: React.ElementType; handle: string; followers: number; color: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '9px 12px', borderRadius: 11, background: '#F8FAFF', border: '1px solid #E0E7FF' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
        <div style={{ width: 30, height: 30, borderRadius: 9, background: color, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon style={{ width: 14, height: 14, color: '#fff' }} />
        </div>
        <span style={{ fontSize: 13, fontWeight: 600, color: '#1E1B4B' }}>@{handle}</span>
      </div>
      <span style={{ fontSize: 13, fontWeight: 800, color: '#4F46E5' }}>{fmt(followers)}</span>
    </div>
  )
}

export default function CreatorDashboard() {
  const { user } = useAuth()
  const [creator, setCreator] = useState<Creator | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (user?.creator_id) getCreator(user.creator_id).then(setCreator).catch(() => {})
  }, [user])

  const totalFollowers = (creator?.instagram_followers || 0) + (creator?.tiktok_followers || 0) + (creator?.youtube_subscribers || 0)

  const profileFields = [creator?.bio, creator?.instagram_handle || creator?.tiktok_handle || creator?.youtube_channel, creator?.niches?.length, creator?.city, creator?.avg_engagement_rate]
  const completeness = Math.round((profileFields.filter(Boolean).length / profileFields.length) * 100)

  const copyProfile = () => {
    navigator.clipboard.writeText(`${window.location.origin}/creator/profile`)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div style={{ fontFamily: 'Inter,sans-serif' }}>

      {/* Hero Banner */}
      <div style={{ borderRadius: 24, marginBottom: 24, position: 'relative', background: 'linear-gradient(135deg,#4F46E5 0%,#7C3AED 60%,#8B5CF6 100%)', padding: '1.75rem 2rem', boxShadow: '0 8px 32px rgba(79,70,229,.28)', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', width: 280, height: 280, top: -80, right: -50, background: 'rgba(255,255,255,.08)', borderRadius: '50%', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', width: 180, height: 180, bottom: -60, left: -20, background: 'rgba(255,255,255,.05)', borderRadius: '50%', pointerEvents: 'none' }} />

        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ width: 58, height: 58, borderRadius: 18, background: 'rgba(255,255,255,.2)', border: '2px solid rgba(255,255,255,.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <span style={{ fontSize: 24, fontWeight: 900, color: '#fff' }}>{(creator?.display_name || user?.username || 'C').charAt(0).toUpperCase()}</span>
            </div>
            <div>
              <div style={{ fontSize: '1.25rem', fontWeight: 900, color: '#fff', letterSpacing: '-0.02em' }}>{creator?.display_name || user?.username}</div>
              {creator?.city && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 3, color: 'rgba(255,255,255,.72)', fontSize: 12.5 }}>
                  <MapPin style={{ width: 12, height: 12 }} />{creator.city}{creator.country ? `, ${creator.country}` : ''}
                </div>
              )}
              {creator?.niches && creator.niches.length > 0 && (
                <div style={{ display: 'flex', gap: 5, marginTop: 7, flexWrap: 'wrap' }}>
                  {creator.niches.slice(0, 3).map(n => (
                    <span key={n} style={{ background: 'rgba(255,255,255,.18)', color: '#fff', fontSize: 10.5, fontWeight: 700, padding: '2px 9px', borderRadius: 999, border: '1px solid rgba(255,255,255,.28)' }}>{n}</span>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap' }}>
            <Link href="/creator/profile" style={{ display: 'inline-flex', alignItems: 'center', gap: 5, background: 'rgba(255,255,255,.16)', color: '#fff', border: '1.5px solid rgba(255,255,255,.32)', borderRadius: 11, padding: '7px 14px', fontSize: 12.5, fontWeight: 700, textDecoration: 'none' }}>
              <Eye style={{ width: 13, height: 13 }} />View Profile
            </Link>
            <Link href="/creator/update-profile" style={{ display: 'inline-flex', alignItems: 'center', gap: 5, background: '#fff', color: '#4F46E5', borderRadius: 11, padding: '7px 14px', fontSize: 12.5, fontWeight: 700, textDecoration: 'none' }}>
              <Edit3 style={{ width: 13, height: 13 }} />Edit Profile
            </Link>
            <button onClick={copyProfile} style={{ display: 'inline-flex', alignItems: 'center', gap: 5, background: 'rgba(255,255,255,.12)', color: '#fff', border: '1.5px solid rgba(255,255,255,.22)', borderRadius: 11, padding: '7px 14px', fontSize: 12.5, fontWeight: 700, cursor: 'pointer' }}>
              <Share2 style={{ width: 13, height: 13 }} />{copied ? 'Copied!' : 'Share'}
            </button>
          </div>
        </div>

        {/* Completion bar */}
        <div style={{ marginTop: '1.25rem', position: 'relative' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
            <span style={{ fontSize: 10.5, fontWeight: 700, color: 'rgba(255,255,255,.65)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>Profile Completion</span>
            <span style={{ fontSize: 11.5, fontWeight: 800, color: '#fff' }}>{completeness}%</span>
          </div>
          <div style={{ height: 5, background: 'rgba(255,255,255,.18)', borderRadius: 99 }}>
            <div style={{ height: '100%', width: `${completeness}%`, background: completeness === 100 ? '#34D399' : 'rgba(255,255,255,.85)', borderRadius: 99, transition: 'width 1s cubic-bezier(.34,1.56,.64,1)' }} />
          </div>
        </div>
      </div>

      {/* Stats — 4 in a row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, marginBottom: 20 }}>
        <StatCard label="Total Followers" value={fmt(totalFollowers)} icon={Users} gradient="linear-gradient(135deg,#4F46E5,#7C3AED)" />
        <StatCard label="Avg Engagement" value={creator?.avg_engagement_rate ? `${creator.avg_engagement_rate.toFixed(1)}%` : '—'} icon={TrendingUp} gradient="linear-gradient(135deg,#059669,#10B981)" />
        <StatCard label="Avg Views" value={fmt(creator?.avg_views || 0)} icon={Eye} gradient="linear-gradient(135deg,#0EA5E9,#38BDF8)" />
        <StatCard label="Min Rate" value={creator?.min_rate_usd ? `$${creator.min_rate_usd.toLocaleString()}` : 'Not set'} icon={DollarSign} gradient="linear-gradient(135deg,#D97706,#F59E0B)" />
      </div>

      {/* Platforms row */}
      {creator && (creator.instagram_handle || creator.tiktok_handle || creator.youtube_channel || creator.twitter_handle) && (
        <div style={{ background: '#fff', border: '1.5px solid #E0E7FF', borderRadius: 20, padding: '1.25rem 1.4rem', boxShadow: '0 4px 16px rgba(79,70,229,.06)', marginBottom: 20 }}>
          <div style={{ fontSize: 10.5, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#9CA3AF', marginBottom: 12 }}>Connected Platforms</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(200px,1fr))', gap: 8 }}>
            {creator.instagram_handle && <PlatformRow icon={Instagram} handle={creator.instagram_handle} followers={creator.instagram_followers} color="linear-gradient(135deg,#E1306C,#C13584)" />}
            {creator.tiktok_handle && <PlatformRow icon={Music2} handle={creator.tiktok_handle} followers={creator.tiktok_followers} color="linear-gradient(135deg,#010101,#69C9D0)" />}
            {creator.youtube_channel && <PlatformRow icon={Youtube} handle={creator.youtube_channel} followers={creator.youtube_subscribers} color="linear-gradient(135deg,#FF0000,#CC0000)" />}
            {creator.twitter_handle && <PlatformRow icon={Twitter} handle={creator.twitter_handle} followers={0} color="linear-gradient(135deg,#1DA1F2,#0D8BD9)" />}
          </div>
          {creator.website && (
            <a href={creator.website} target="_blank" rel="noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: 5, marginTop: 12, fontSize: 12.5, color: '#4F46E5', fontWeight: 600, textDecoration: 'none' }}>
              <Globe style={{ width: 13, height: 13 }} />{creator.website.replace(/^https?:\/\//, '')}
            </a>
          )}
        </div>
      )}

      {/* 3 Action cards in a row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 14 }}>
        <ActionCard href="/creator/career-manager" icon={Sparkles} label="AI Career Manager"
          desc="Personalised growth advice, pitch templates and collab strategies."
          gradient="linear-gradient(135deg,#4F46E5,#7C3AED)" arrowColor="#4F46E5" />
        <ActionCard href="/creator/update-profile" icon={UserCog} label="Edit Profile"
          desc="Update stats, handles, niches and rates to attract better brand matches."
          gradient="linear-gradient(135deg,#0EA5E9,#6366F1)" arrowColor="#0EA5E9" />
        <ActionCard href="/creator/profile" icon={Eye} label="View Public Profile"
          desc="See exactly how brands discover and view your profile on Skout."
          gradient="linear-gradient(135deg,#059669,#10B981)" arrowColor="#059669" />
      </div>
    </div>
  )
}
