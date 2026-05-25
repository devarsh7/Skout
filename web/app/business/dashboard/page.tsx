'use client'

import Link from 'next/link'
import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Search, Filter, Mail, BarChart3, Bot, Target, Map, MapPin, Building2 } from 'lucide-react'

const tools = [
  { href: '/business/discover', icon: Search, label: 'Discover Creators', desc: 'AI-powered natural language search across 50K+ creators', gradient: 'linear-gradient(135deg,#4F46E5,#7C3AED)', color: '#4F46E5' },
  { href: '/business/filter', icon: Filter, label: 'Filter & Refine', desc: 'Platform, location, niche and engagement filters', gradient: 'linear-gradient(135deg,#0EA5E9,#6366F1)', color: '#0EA5E9' },
  { href: '/business/outreach', icon: Mail, label: 'AI Outreach', desc: 'Personalised DMs and emails for each creator', gradient: 'linear-gradient(135deg,#059669,#10B981)', color: '#059669' },
  { href: '/business/campaigns', icon: BarChart3, label: 'Campaigns', desc: 'Track outreach status and campaign ROI in one view', gradient: 'linear-gradient(135deg,#D97706,#F59E0B)', color: '#D97706' },
  { href: '/business/ai-agent', icon: Bot, label: 'AI Agent', desc: 'Describe your campaign — AI discovers, filters and drafts', gradient: 'linear-gradient(135deg,#7C3AED,#EC4899)', color: '#7C3AED' },
  { href: '/business/creator-match', icon: Target, label: 'Creator Match', desc: 'AI matching based on your brand profile and goals', gradient: 'linear-gradient(135deg,#0F766E,#14B8A6)', color: '#0F766E' },
  { href: '/business/map', icon: Map, label: 'Creator Map', desc: 'Browse creators by city and geographic region', gradient: 'linear-gradient(135deg,#DC2626,#F97316)', color: '#DC2626' },
  { href: '/business/local-market', icon: MapPin, label: 'Local Market', desc: 'Hyperlocal leaderboards and benchmarks by city', gradient: 'linear-gradient(135deg,#7C3AED,#4F46E5)', color: '#7C3AED' },
]

function ToolCard({ href, icon: Icon, label, desc, gradient, color }: typeof tools[0]) {
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
        boxShadow: pressed ? '0 2px 6px rgba(79,70,229,.06)' : '0 5px 20px rgba(79,70,229,.09)',
        transform: pressed ? 'scale(0.95) translateY(2px)' : 'scale(1)',
        transition: 'all 0.2s cubic-bezier(.34,1.56,.64,1)',
        padding: '1.35rem',
      }}
    >
      <div className="pointer-events-none absolute inset-0 rounded-[20px]" style={{ background: 'linear-gradient(135deg,rgba(238,242,255,.55) 0%,transparent 55%)' }} />
      <div className="relative">
        <div className="mb-3 flex h-[42px] w-[42px] items-center justify-center rounded-[13px]" style={{ background: gradient, boxShadow: '0 4px 12px rgba(79,70,229,.2)' }}>
          <Icon className="h-[19px] w-[19px] text-white" />
        </div>
        <div className="mb-1 text-[0.92rem] font-extrabold" style={{ color: '#1E1B4B' }}>{label}</div>
        <div className="mb-3 text-[0.78rem] leading-relaxed" style={{ color: '#6B7280' }}>{desc}</div>
        <div className="text-[0.78rem] font-bold" style={{ color }}>Open →</div>
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
    <div className="space-y-5">

      {/* Hero */}
      <div className="relative overflow-hidden rounded-3xl p-7" style={{ background: 'linear-gradient(135deg,#1E1B4B 0%,#312E81 45%,#4F46E5 100%)', boxShadow: '0 8px 32px rgba(30,27,75,.35)' }}>
        <div className="pointer-events-none absolute -right-14 -top-20 h-72 w-72 rounded-full" style={{ background: 'rgba(99,102,241,.25)' }} />
        <div className="pointer-events-none absolute -bottom-16 -left-8 h-48 w-48 rounded-full" style={{ background: 'rgba(139,92,246,.15)' }} />

        <div className="relative flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-2xl" style={{ background: 'rgba(255,255,255,.15)', border: '2px solid rgba(255,255,255,.28)' }}>
              <Building2 className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="text-xl font-black text-white" style={{ letterSpacing: '-0.02em' }}>
                Welcome back, {companyName} 👋
              </div>
              <div className="mt-1 flex items-center gap-3">
                {industry && <span className="text-[12.5px] font-medium" style={{ color: 'rgba(255,255,255,.7)' }}>{industry}</span>}
                {country && (
                  <span className="flex items-center gap-1 text-[12.5px]" style={{ color: 'rgba(255,255,255,.6)' }}>
                    <MapPin className="h-2.5 w-2.5" />{country}
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            {!meta?.company_name ? (
              <Link href="/business/onboarding" className="inline-flex items-center gap-1.5 rounded-xl bg-white px-4 py-2 text-[13px] font-bold no-underline" style={{ color: '#4F46E5' }}>
                Complete Profile →
              </Link>
            ) : (
              <Link href="/business/discover" className="inline-flex items-center gap-1.5 rounded-xl bg-white px-4 py-2 text-[13px] font-bold no-underline" style={{ color: '#4F46E5', boxShadow: '0 4px 14px rgba(0,0,0,.1)' }}>
                <Search className="h-3 w-3" />Find Creators
              </Link>
            )}
            <Link href="/business/ai-agent" className="inline-flex items-center gap-1.5 rounded-xl px-4 py-2 text-[13px] font-bold text-white no-underline" style={{ background: 'rgba(255,255,255,.14)', border: '1.5px solid rgba(255,255,255,.28)' }}>
              <Bot className="h-3 w-3" />AI Agent
            </Link>
          </div>
        </div>

        {/* Stat strip */}
        <div className="relative mt-5 flex gap-6 border-t pt-5" style={{ borderColor: 'rgba(255,255,255,.12)' }}>
          {[
            { label: 'Searches', value: '∞' },
            { label: 'Creators Indexed', value: '50K+' },
            { label: 'AI Models', value: '3' },
            { label: 'Outreach Tools', value: '4' },
          ].map(s => (
            <div key={s.label}>
              <div className="text-[1.3rem] font-black text-white" style={{ letterSpacing: '-0.02em' }}>{s.value}</div>
              <div className="text-[11px] font-medium" style={{ color: 'rgba(255,255,255,.55)' }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Profile incomplete prompt */}
      {!meta?.company_name && (
        <div className="flex items-center justify-between gap-3 rounded-2xl p-4" style={{ background: '#FFF7ED', border: '1.5px solid #FED7AA' }}>
          <div>
            <div className="mb-0.5 text-sm font-bold" style={{ color: '#92400E' }}>Complete your brand profile</div>
            <div className="text-[12.5px]" style={{ color: '#B45309' }}>Help creators understand your brand for better matching.</div>
          </div>
          <Link href="/business/onboarding" className="flex-shrink-0 rounded-xl px-4 py-2 text-[13px] font-bold text-white no-underline" style={{ background: 'linear-gradient(135deg,#D97706,#F59E0B)' }}>
            Complete →
          </Link>
        </div>
      )}

      {/* Section label */}
      <div className="text-[10.5px] font-bold uppercase tracking-widest" style={{ color: '#9CA3AF' }}>
        Tools & Features
      </div>

      {/* Tool cards */}
      <div className="grid grid-cols-4 gap-3">
        {tools.map(t => <ToolCard key={t.href} {...t} />)}
      </div>

      {/* AI Agent spotlight */}
      <div className="flex flex-wrap items-center justify-between gap-5 rounded-[20px] p-6" style={{ background: 'linear-gradient(135deg,#EEF2FF 0%,#F3F0FF 100%)', border: '1.5px solid #C7D2FE' }}>
        <div className="flex items-center gap-4">
          <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-[14px]" style={{ background: 'linear-gradient(135deg,#7C3AED,#4F46E5)', boxShadow: '0 4px 14px rgba(79,70,229,.3)' }}>
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="mb-0.5 text-[0.95rem] font-extrabold" style={{ color: '#1E1B4B' }}>Try the AI Campaign Agent</div>
            <div className="text-[0.82rem] leading-relaxed" style={{ color: '#6B7280', maxWidth: 460 }}>
              Describe your campaign in plain English — the AI discovers creators, applies filters, and drafts outreach in a single conversation.
            </div>
          </div>
        </div>
        <Link href="/business/ai-agent" className="inline-flex flex-shrink-0 items-center gap-1.5 rounded-xl px-5 py-2.5 text-[13px] font-bold text-white no-underline" style={{ background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', boxShadow: '0 4px 14px rgba(79,70,229,.3)', whiteSpace: 'nowrap' }}>
          Open AI Agent →
        </Link>
      </div>
    </div>
  )
}
