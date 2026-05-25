'use client'

import Link from 'next/link'
import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Search, Filter, Mail, BarChart3, Bot, Target, Map, MapPin, Building2 } from 'lucide-react'

const quickActions = [
  { href: '/business/discover', icon: Search, label: 'Discover Creators', desc: 'Find creators with AI-powered natural language search', gradient: 'linear-gradient(135deg,#4F46E5,#7C3AED)', arrow: '#4F46E5' },
  { href: '/business/filter', icon: Filter, label: 'Filter & Refine', desc: 'Structured filters by platform, location, niche and engagement', gradient: 'linear-gradient(135deg,#0EA5E9,#6366F1)', arrow: '#0EA5E9' },
  { href: '/business/outreach', icon: Mail, label: 'AI Outreach', desc: 'Draft personalised DMs and emails for each creator', gradient: 'linear-gradient(135deg,#059669,#10B981)', arrow: '#059669' },
  { href: '/business/campaigns', icon: BarChart3, label: 'Campaigns', desc: 'Track outreach status and campaign ROI in one view', gradient: 'linear-gradient(135deg,#D97706,#F59E0B)', arrow: '#D97706' },
  { href: '/business/ai-agent', icon: Bot, label: 'AI Agent', desc: 'Describe your campaign — AI discovers, filters and drafts', gradient: 'linear-gradient(135deg,#7C3AED,#EC4899)', arrow: '#7C3AED' },
  { href: '/business/creator-match', icon: Target, label: 'Creator Match', desc: 'AI matching based on your brand profile and goals', gradient: 'linear-gradient(135deg,#0F766E,#14B8A6)', arrow: '#0F766E' },
  { href: '/business/map', icon: Map, label: 'Creator Map', desc: 'Browse creators by city and geographic region', gradient: 'linear-gradient(135deg,#DC2626,#F97316)', arrow: '#DC2626' },
  { href: '/business/local-market', icon: MapPin, label: 'Local Market', desc: 'Hyperlocal leaderboards and benchmarks by city', gradient: 'linear-gradient(135deg,#7C3AED,#4F46E5)', arrow: '#7C3AED' },
]

function ActionCard({ href, icon: Icon, label, desc, gradient, arrow }: {
  href: string; icon: React.ElementType; label: string; desc: string; gradient: string; arrow: string
}) {
  const [pressed, setPressed] = useState(false)
  return (
    <Link href={href}
      onMouseDown={() => setPressed(true)}
      onMouseUp={() => setPressed(false)}
      onMouseLeave={() => setPressed(false)}
      style={{
        display: 'block', background: '#fff', border: '1.5px solid #E0E7FF', borderRadius: 20,
        padding: '1.35rem',
        boxShadow: pressed ? '0 2px 6px rgba(79,70,229,.06)' : '0 5px 20px rgba(79,70,229,.09)',
        transform: pressed ? 'scale(0.95) translateY(2px)' : 'scale(1) translateY(0)',
        transition: 'all 0.2s cubic-bezier(.34,1.56,.64,1)',
        textDecoration: 'none', position: 'relative', overflow: 'hidden',
      }}>
      <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg,rgba(238,242,255,.55) 0%,transparent 55%)', borderRadius: 20, pointerEvents: 'none' }} />
      <div style={{ position: 'relative' }}>
        <div style={{ width: 42, height: 42, borderRadius: 13, background: gradient, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 12, boxShadow: '0 4px 12px rgba(79,70,229,.2)' }}>
          <Icon style={{ width: 19, height: 19, color: '#fff' }} />
        </div>
        <div style={{ fontWeight: 800, fontSize: '0.92rem', color: '#1E1B4B', marginBottom: 4 }}>{label}</div>
        <div style={{ fontSize: '0.78rem', color: '#6B7280', lineHeight: 1.6, marginBottom: 12 }}>{desc}</div>
        <div style={{ fontSize: '0.78rem', fontWeight: 700, color: arrow }}>Open →</div>
      </div>
    </Link>
  )
}

export default function BusinessDashboard() {
  const { user } = useAuth()
  const meta = user?.profile_meta as Record<string, string> | undefined
  const companyName = meta?.company_name || user?.username || 'Brand'
  const industry = meta?.industry
  const country = meta?.country

  return (
    <div style={{ fontFamily: 'Inter,sans-serif' }}>

      {/* Hero Banner */}
      <div style={{ borderRadius: 24, marginBottom: 24, position: 'relative', background: 'linear-gradient(135deg,#1E1B4B 0%,#312E81 45%,#4F46E5 100%)', padding: '1.75rem 2rem', boxShadow: '0 8px 32px rgba(30,27,75,.35)', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', width: 300, height: 300, top: -90, right: -60, background: 'rgba(99,102,241,.25)', borderRadius: '50%', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', width: 200, height: 200, bottom: -70, left: -30, background: 'rgba(139,92,246,.15)', borderRadius: '50%', pointerEvents: 'none' }} />

        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ width: 58, height: 58, borderRadius: 18, background: 'rgba(255,255,255,.15)', border: '2px solid rgba(255,255,255,.28)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <Building2 style={{ width: 26, height: 26, color: '#fff' }} />
            </div>
            <div>
              <div style={{ fontSize: '1.25rem', fontWeight: 900, color: '#fff', letterSpacing: '-0.02em' }}>
                Welcome back, {companyName} 👋
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 5 }}>
                {industry && <span style={{ fontSize: 12.5, color: 'rgba(255,255,255,.7)', fontWeight: 500 }}>{industry}</span>}
                {country && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12.5, color: 'rgba(255,255,255,.6)' }}>
                    <MapPin style={{ width: 11, height: 11 }} />{country}
                  </span>
                )}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            {!meta?.company_name ? (
              <Link href="/business/onboarding" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: '#fff', color: '#4F46E5', borderRadius: 12, padding: '8px 16px', fontSize: 13, fontWeight: 700, textDecoration: 'none' }}>
                Complete Profile →
              </Link>
            ) : (
              <Link href="/business/discover" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: '#fff', color: '#4F46E5', borderRadius: 12, padding: '8px 16px', fontSize: 13, fontWeight: 700, textDecoration: 'none', boxShadow: '0 4px 14px rgba(0,0,0,.1)' }}>
                <Search style={{ width: 13, height: 13 }} />Find Creators
              </Link>
            )}
            <Link href="/business/ai-agent" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: 'rgba(255,255,255,.14)', color: '#fff', border: '1.5px solid rgba(255,255,255,.28)', borderRadius: 12, padding: '8px 16px', fontSize: 13, fontWeight: 700, textDecoration: 'none' }}>
              <Bot style={{ width: 13, height: 13 }} />AI Agent
            </Link>
          </div>
        </div>

        {/* Quick stat strip */}
        <div style={{ position: 'relative', display: 'flex', gap: 24, marginTop: '1.5rem', paddingTop: '1.25rem', borderTop: '1px solid rgba(255,255,255,.12)' }}>
          {[
            { label: 'Searches', value: '∞' },
            { label: 'Creators Indexed', value: '50K+' },
            { label: 'AI Models', value: '3' },
            { label: 'Outreach Tools', value: '4' },
          ].map(s => (
            <div key={s.label}>
              <div style={{ fontSize: '1.3rem', fontWeight: 900, color: '#fff', letterSpacing: '-0.02em' }}>{s.value}</div>
              <div style={{ fontSize: 11, color: 'rgba(255,255,255,.55)', fontWeight: 500 }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Profile incomplete prompt */}
      {!meta?.company_name && (
        <div style={{ background: '#FFF7ED', border: '1.5px solid #FED7AA', borderRadius: 16, padding: '1rem 1.25rem', marginBottom: 20, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
          <div>
            <div style={{ fontWeight: 700, color: '#92400E', fontSize: 14, marginBottom: 2 }}>Complete your brand profile</div>
            <div style={{ fontSize: 12.5, color: '#B45309' }}>Help creators understand your brand for better matching.</div>
          </div>
          <Link href="/business/onboarding" style={{ flexShrink: 0, background: 'linear-gradient(135deg,#D97706,#F59E0B)', color: '#fff', fontWeight: 700, fontSize: 13, padding: '8px 16px', borderRadius: 10, textDecoration: 'none' }}>
            Complete →
          </Link>
        </div>
      )}

      {/* Section label */}
      <div style={{ fontSize: 10.5, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#9CA3AF', marginBottom: 14 }}>
        Tools & Features
      </div>

      {/* Action cards — 4 per row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12 }}>
        {quickActions.map(a => (
          <ActionCard key={a.href} {...a} />
        ))}
      </div>

      {/* AI Agent spotlight */}
      <div style={{ marginTop: 20, background: 'linear-gradient(135deg,#EEF2FF 0%,#F3F0FF 100%)', border: '1.5px solid #C7D2FE', borderRadius: 20, padding: '1.4rem 1.6rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 20, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ width: 46, height: 46, borderRadius: 14, background: 'linear-gradient(135deg,#7C3AED,#4F46E5)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, boxShadow: '0 4px 14px rgba(79,70,229,.3)' }}>
            <Bot style={{ width: 22, height: 22, color: '#fff' }} />
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: '0.95rem', color: '#1E1B4B', marginBottom: 2 }}>Try the AI Campaign Agent</div>
            <div style={{ fontSize: '0.82rem', color: '#6B7280', lineHeight: 1.6, maxWidth: 460 }}>
              Describe your campaign in plain English — the AI discovers creators, applies filters, and drafts outreach in a single conversation.
            </div>
          </div>
        </div>
        <Link href="/business/ai-agent" style={{ flexShrink: 0, display: 'inline-flex', alignItems: 'center', gap: 6, background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', color: '#fff', fontWeight: 700, fontSize: 13, padding: '10px 20px', borderRadius: 12, textDecoration: 'none', boxShadow: '0 4px 14px rgba(79,70,229,.3)', whiteSpace: 'nowrap' }}>
          Open AI Agent →
        </Link>
      </div>
    </div>
  )
}
