'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { getCreator } from '@/lib/api'
import { Creator } from '@/types'
import { Instagram, Youtube, Music2, Twitter, Globe, MapPin, TrendingUp, Users, Edit3, DollarSign, Loader2 } from 'lucide-react'

function fmt(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`
  return n > 0 ? String(n) : '—'
}

export default function CreatorProfilePage() {
  const { user } = useAuth()
  const [creator, setCreator] = useState<Creator | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user?.creator_id) {
      getCreator(user.creator_id).then(setCreator).catch(() => {}).finally(() => setLoading(false))
    }
  }, [user])

  if (loading) return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: '5rem' }}>
      <Loader2 style={{ width: 28, height: 28, color: '#4F46E5', animation: 'spin 1s linear infinite' }} />
    </div>
  )

  if (!creator) return (
    <div style={{ textAlign: 'center', padding: '5rem 2rem' }}>
      <p style={{ color: '#6B7280' }}>Profile not found. <Link href="/creator/onboarding" style={{ color: '#4F46E5' }}>Complete onboarding →</Link></p>
    </div>
  )

  const totalFollowers = (creator.instagram_followers || 0) + (creator.tiktok_followers || 0) + (creator.youtube_subscribers || 0)

  const platforms = [
    creator.instagram_handle && { icon: Instagram, handle: creator.instagram_handle, followers: creator.instagram_followers, color: 'linear-gradient(135deg,#E1306C,#C13584)', name: 'Instagram' },
    creator.tiktok_handle && { icon: Music2, handle: creator.tiktok_handle, followers: creator.tiktok_followers, color: 'linear-gradient(135deg,#010101,#69C9D0)', name: 'TikTok' },
    creator.youtube_channel && { icon: Youtube, handle: creator.youtube_channel, followers: creator.youtube_subscribers, color: 'linear-gradient(135deg,#FF0000,#CC0000)', name: 'YouTube' },
    creator.twitter_handle && { icon: Twitter, handle: creator.twitter_handle, followers: 0, color: 'linear-gradient(135deg,#1DA1F2,#0D8BD9)', name: 'Twitter' },
  ].filter(Boolean) as { icon: React.ElementType; handle: string; followers: number; color: string; name: string }[]

  return (
    <div style={{ fontFamily: 'Inter,sans-serif', maxWidth: 680, margin: '0 auto' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#1E1B4B', margin: 0 }}>Public Profile</h1>
          <p style={{ fontSize: 13, color: '#9CA3AF', marginTop: 2 }}>This is how brands see you on Skout</p>
        </div>
        <Link href="/creator/update-profile"
          style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', color: '#fff', padding: '9px 18px', borderRadius: 12, fontSize: 13, fontWeight: 700, textDecoration: 'none', boxShadow: '0 4px 14px rgba(79,70,229,.3)' }}>
          <Edit3 style={{ width: 14, height: 14 }} /> Edit Profile
        </Link>
      </div>

      {/* Profile card */}
      <div style={{ background: '#fff', border: '1.5px solid #E0E7FF', borderRadius: 24, overflow: 'hidden', boxShadow: '0 8px 32px rgba(79,70,229,.1)', marginBottom: 20 }}>

        {/* Banner */}
        <div style={{ height: 100, background: 'linear-gradient(135deg,#4F46E5 0%,#7C3AED 50%,#8B5CF6 100%)', position: 'relative' }}>
          <div style={{ position: 'absolute', width: 200, height: 200, top: -60, right: -40, background: 'rgba(255,255,255,.1)', borderRadius: '50%' }} />
        </div>

        <div style={{ padding: '0 2rem 2rem' }}>
          {/* Avatar */}
          <div style={{ marginTop: -36, marginBottom: 16 }}>
            <div style={{ width: 72, height: 72, borderRadius: 20, background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', border: '3px solid #fff', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 16px rgba(79,70,229,.3)' }}>
              <span style={{ fontSize: 30, fontWeight: 900, color: '#fff' }}>
                {(creator.display_name || creator.full_name).charAt(0).toUpperCase()}
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
            <div>
              <h2 style={{ fontSize: '1.3rem', fontWeight: 900, color: '#1E1B4B', margin: '0 0 4px' }}>
                {creator.display_name || creator.full_name}
              </h2>
              {creator.city && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: '#6B7280', fontSize: 13 }}>
                  <MapPin style={{ width: 13, height: 13 }} />
                  {creator.city}{creator.country ? `, ${creator.country}` : ''}
                </div>
              )}
            </div>
            {creator.open_to_collabs && (
              <div style={{ background: '#F0FDF4', border: '1.5px solid #A7F3D0', color: '#065F46', fontSize: 12, fontWeight: 700, padding: '5px 14px', borderRadius: 999 }}>
                ✓ Open to Collabs
              </div>
            )}
          </div>

          {creator.bio && (
            <p style={{ fontSize: 14, color: '#374151', lineHeight: 1.75, margin: '14px 0 0' }}>{creator.bio}</p>
          )}

          {creator.website && (
            <a href={creator.website} target="_blank" rel="noreferrer"
              style={{ display: 'inline-flex', alignItems: 'center', gap: 5, marginTop: 10, fontSize: 13, color: '#4F46E5', fontWeight: 600, textDecoration: 'none' }}>
              <Globe style={{ width: 13, height: 13 }} />{creator.website.replace(/^https?:\/\//, '')}
            </a>
          )}

          {/* Niches */}
          {creator.niches.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 16 }}>
              {creator.niches.map(n => (
                <span key={n} style={{ background: '#EEF2FF', color: '#4F46E5', fontSize: 12, fontWeight: 700, padding: '4px 12px', borderRadius: 999, border: '1.5px solid #C7D2FE' }}>{n}</span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12, marginBottom: 20 }}>
        {[
          { label: 'Total Reach', value: fmt(totalFollowers), icon: Users, gradient: 'linear-gradient(135deg,#4F46E5,#7C3AED)' },
          { label: 'Avg Engagement', value: creator.avg_engagement_rate ? `${creator.avg_engagement_rate.toFixed(1)}%` : '—', icon: TrendingUp, gradient: 'linear-gradient(135deg,#059669,#10B981)' },
          { label: 'Min Rate', value: creator.min_rate_usd ? `$${creator.min_rate_usd.toLocaleString()}` : '—', icon: DollarSign, gradient: 'linear-gradient(135deg,#D97706,#F59E0B)' },
        ].map(s => (
          <div key={s.label} style={{ background: '#fff', border: '1.5px solid #E0E7FF', borderRadius: 18, padding: '1.1rem', boxShadow: '0 4px 14px rgba(79,70,229,.06)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
              <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#9CA3AF' }}>{s.label}</span>
              <div style={{ width: 28, height: 28, borderRadius: 8, background: s.gradient, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <s.icon style={{ width: 13, height: 13, color: '#fff' }} />
              </div>
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 900, color: '#1E1B4B', letterSpacing: '-0.03em' }}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Platforms */}
      {platforms.length > 0 && (
        <div style={{ background: '#fff', border: '1.5px solid #E0E7FF', borderRadius: 20, padding: '1.4rem', boxShadow: '0 4px 16px rgba(79,70,229,.06)', marginBottom: 20 }}>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#9CA3AF', marginBottom: 14 }}>Platforms</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {platforms.map(p => (
              <div key={p.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', borderRadius: 12, background: '#F8FAFF', border: '1px solid #E0E7FF' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ width: 34, height: 34, borderRadius: 10, background: p.color, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <p.icon style={{ width: 16, height: 16, color: '#fff' }} />
                  </div>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 600, color: '#1E1B4B' }}>@{p.handle}</div>
                    <div style={{ fontSize: 11, color: '#9CA3AF' }}>{p.name}</div>
                  </div>
                </div>
                {p.followers > 0 && (
                  <span style={{ fontSize: 13, fontWeight: 800, color: '#4F46E5' }}>{fmt(p.followers)}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Collab preferences */}
      {creator.preferred_collab_types?.length > 0 && (
        <div style={{ background: '#fff', border: '1.5px solid #E0E7FF', borderRadius: 20, padding: '1.4rem', boxShadow: '0 4px 16px rgba(79,70,229,.06)' }}>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#9CA3AF', marginBottom: 12 }}>Collaboration Types</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {creator.preferred_collab_types.map(t => (
              <span key={t} style={{ background: '#F3F0FF', color: '#7C3AED', fontSize: 12, fontWeight: 700, padding: '5px 14px', borderRadius: 999, border: '1.5px solid #DDD6FE' }}>{t}</span>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: 24, textAlign: 'center' }}>
        <Link href="/creator/dashboard" style={{ fontSize: 13, color: '#9CA3AF', textDecoration: 'none', fontWeight: 600 }}>← Back to Dashboard</Link>
      </div>
    </div>
  )
}
