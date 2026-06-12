'use client'

import { useEffect, useState } from 'react'
import {
  Calculator, Sparkles, Copy, Check, Info, TrendingUp,
  Instagram, Music2, Youtube, Loader2, MapPin, Wand2,
} from 'lucide-react'
import { creatorAgentCalculateRate, RateCalcInputs, RateCalcResult } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

// ── Option tables ─────────────────────────────────────────────────────────────

const PLATFORMS = [
  { id: 'instagram', label: 'Instagram', icon: Instagram, color: '#E1306C' },
  { id: 'tiktok',    label: 'TikTok',    icon: Music2,    color: '#1E1B4B' },
  { id: 'youtube',   label: 'YouTube',   icon: Youtube,   color: '#FF0000' },
] as const

const DELIVERABLES: Record<string, { id: string; label: string; sub: string }[]> = {
  instagram: [
    { id: 'reel',     label: 'Reel',          sub: '15-90s vertical video' },
    { id: 'carousel', label: 'Carousel',      sub: '3-10 image swipe post' },
    { id: 'static',   label: 'Static Post',   sub: 'Single image / graphic' },
    { id: 'story',    label: 'Story (3-pack)',sub: 'Three 15s stories' },
    { id: 'bundle',   label: 'Reel + Stories', sub: 'Reel + 3-pack bundle' },
  ],
  tiktok: [
    { id: 'video',  label: 'Standard Video', sub: '15-60s in-feed' },
    { id: 'bundle', label: 'Video + Stitches', sub: 'Video + 1 follow-up' },
  ],
  youtube: [
    { id: 'integration', label: '60-90s Integration', sub: 'Mid-roll mention' },
    { id: 'dedicated',   label: 'Dedicated Video',   sub: 'Full sponsored video' },
    { id: 'short',       label: 'YouTube Short',     sub: '<60s vertical' },
  ],
}

const USAGE = [
  { id: 'organic',     label: 'Organic only',         sub: 'Posts on your channel — no ads' },
  { id: 'paid_30d',    label: 'Paid whitelisting 30d', sub: 'Brand can boost as ads (30 days)' },
  { id: 'paid_60d',    label: 'Paid whitelisting 60d', sub: 'Brand can boost as ads (60 days)' },
  { id: 'reuse_brand', label: 'Brand reuse',          sub: 'Brand reposts on owned channels' },
  { id: 'full_rights', label: 'Full rights',          sub: 'Perpetual + paid + reuse' },
] as const

const EXCLUSIVITY = [
  { id: 'none', label: 'None',  sub: 'Work with competitors anytime' },
  { id: '30d',  label: '30 days', sub: 'No competitor work for 30d' },
  { id: '60d',  label: '60 days', sub: 'No competitor work for 60d' },
  { id: '90d',  label: '90 days', sub: 'No competitor work for 90d' },
  { id: '180d', label: '180 days',sub: 'No competitor work for 180d' },
] as const

// ── Animated counter ──────────────────────────────────────────────────────────

function AnimatedNumber({ value }: { value: number }) {
  const [display, setDisplay] = useState(0)
  useEffect(() => {
    const start = performance.now()
    const dur = 750
    const from = display
    let raf = 0
    const tick = (t: number) => {
      const p = Math.min(1, (t - start) / dur)
      // ease-out cubic
      const eased = 1 - Math.pow(1 - p, 3)
      setDisplay(Math.round(from + (value - from) * eased))
      if (p < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value])
  return <>{display.toLocaleString()}</>
}

// ── Pill selector ─────────────────────────────────────────────────────────────

function Pills<T extends { id: string; label: string; sub?: string }>({
  options, value, onChange,
}: { options: readonly T[] | T[]; value: string; onChange: (id: string) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((o, i) => {
        const active = o.id === value
        return (
          <button
            key={o.id}
            type="button"
            onClick={() => onChange(o.id)}
            className={`group relative px-3.5 py-2 rounded-xl text-xs font-bold border transition-all duration-200 animate-fade-up
              ${active
                ? 'text-white border-transparent shadow-[0_4px_14px_rgba(79,70,229,0.35)] -translate-y-[1px]'
                : 'bg-white text-[#1E1B4B] border-[#E2E8F0] hover:border-[#C7D2FE] hover:-translate-y-[1px]'}`}
            style={{
              animationDelay: `${i * 30}ms`,
              ...(active
                ? { background: 'linear-gradient(135deg, #4F46E5, #7C3AED)' }
                : {}),
            }}
            title={o.sub}
          >
            {o.label}
          </button>
        )
      })}
    </div>
  )
}

// ── Main ──────────────────────────────────────────────────────────────────────

export default function RateCalculator() {
  const { token, user } = useAuth()
  const [platform,    setPlatform]    = useState<'instagram' | 'tiktok' | 'youtube'>('instagram')
  const [deliverable, setDeliverable] = useState('reel')
  const [quantity,    setQuantity]    = useState(1)
  const [usage,       setUsage]       = useState('organic')
  const [exclusivity, setExclusivity] = useState('none')
  const [addBundle,   setAddBundle]   = useState(false)
  const [loading,     setLoading]     = useState(false)
  const [error,       setError]       = useState<string | null>(null)
  const [result,      setResult]      = useState<RateCalcResult | null>(null)
  const [copied,      setCopied]      = useState<'quote' | 'number' | null>(null)

  // Reset deliverable when platform changes
  useEffect(() => {
    setDeliverable(DELIVERABLES[platform][0].id)
  }, [platform])

  const calculate = async () => {
    if (!token) return
    setLoading(true)
    setError(null)
    try {
      const inputs: RateCalcInputs = {
        platform, deliverable, quantity, usage, exclusivity, add_story_bundle: addBundle,
      }
      const res = await creatorAgentCalculateRate(inputs, token)
      setResult(res)
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Could not calculate rate'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const copyText = async (text: string, key: 'quote' | 'number') => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(key)
      setTimeout(() => setCopied(null), 1600)
    } catch {/* ignore */}
  }

  // For Toronto-based creators, the suggested example.
  const profileFullName = (user?.profile_meta?.full_name as string | undefined) || ''
  const firstName = (profileFullName || user?.username || '').split(' ')[0] || 'creator'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 animate-fade-up">
        <div className="flex items-start gap-3">
          <div
            className="w-11 h-11 rounded-2xl flex items-center justify-center animate-gradient shrink-0"
            style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED, #8B5CF6)' }}
          >
            <Calculator className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-extrabold text-[#1E1B4B] tracking-tight">
              Rate Calculator
            </h2>
            <p className="text-sm text-[#6B7280] mt-0.5">
              Plug in the deliverable, see a quote-ready number — based on your real followers, engagement, and Toronto market rates.
            </p>
          </div>
        </div>
      </div>

      {/* Inputs */}
      <div className="card p-6 space-y-6 animate-fade-up delay-1">
        {/* Platform */}
        <div>
          <span className="section-label">Platform</span>
          <div className="grid grid-cols-3 gap-2">
            {PLATFORMS.map((p, i) => {
              const Icon = p.icon
              const active = p.id === platform
              return (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => setPlatform(p.id as 'instagram' | 'tiktok' | 'youtube')}
                  className={`group relative flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-bold text-sm border transition-all duration-200 animate-fade-up
                    ${active
                      ? 'text-white border-transparent shadow-[0_6px_18px_rgba(79,70,229,0.30)] -translate-y-[1px]'
                      : 'bg-white text-[#1E1B4B] border-[#E2E8F0] hover:border-[#C7D2FE] hover:-translate-y-[1px]'}`}
                  style={{
                    animationDelay: `${i * 40}ms`,
                    ...(active
                      ? { background: 'linear-gradient(135deg, #4F46E5, #7C3AED)' }
                      : {}),
                  }}
                >
                  <Icon className="w-4 h-4" />
                  {p.label}
                </button>
              )
            })}
          </div>
        </div>

        {/* Deliverable */}
        <div>
          <span className="section-label">Deliverable</span>
          <Pills options={DELIVERABLES[platform]} value={deliverable} onChange={setDeliverable} />
          <p className="text-[11px] text-[#9CA3AF] mt-2">
            {DELIVERABLES[platform].find(d => d.id === deliverable)?.sub}
          </p>
        </div>

        {/* Quantity + Story bundle */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <span className="section-label">Quantity</span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setQuantity(q => Math.max(1, q - 1))}
                className="w-10 h-10 rounded-xl border border-[#E2E8F0] bg-white text-[#1E1B4B] font-bold text-lg transition-all hover:border-[#C7D2FE] active:scale-95"
              >−</button>
              <div className="flex-1 text-center text-2xl font-extrabold text-[#1E1B4B] animate-fade-in" key={quantity}>
                {quantity}
              </div>
              <button
                type="button"
                onClick={() => setQuantity(q => Math.min(20, q + 1))}
                className="w-10 h-10 rounded-xl border border-[#E2E8F0] bg-white text-[#1E1B4B] font-bold text-lg transition-all hover:border-[#C7D2FE] active:scale-95"
              >+</button>
            </div>
          </div>

          <div>
            <span className="section-label">Story Add-on</span>
            <button
              type="button"
              onClick={() => setAddBundle(b => !b)}
              className={`w-full h-10 rounded-xl border font-bold text-xs transition-all duration-200
                ${addBundle
                  ? 'text-white border-transparent shadow-[0_4px_14px_rgba(79,70,229,0.35)]'
                  : 'bg-white text-[#1E1B4B] border-[#E2E8F0] hover:border-[#C7D2FE]'}`}
              style={addBundle ? { background: 'linear-gradient(135deg, #4F46E5, #7C3AED)' } : {}}
            >
              {addBundle ? '✓  Story 3-pack bundled (+30%)' : '+ Add Story 3-pack bundle'}
            </button>
          </div>
        </div>

        {/* Usage */}
        <div>
          <span className="section-label">Usage Rights</span>
          <Pills options={USAGE} value={usage} onChange={setUsage} />
          <p className="text-[11px] text-[#9CA3AF] mt-2">
            {USAGE.find(u => u.id === usage)?.sub}
          </p>
        </div>

        {/* Exclusivity */}
        <div>
          <span className="section-label">Category Exclusivity</span>
          <Pills options={EXCLUSIVITY} value={exclusivity} onChange={setExclusivity} />
          <p className="text-[11px] text-[#9CA3AF] mt-2">
            {EXCLUSIVITY.find(e => e.id === exclusivity)?.sub}
          </p>
        </div>

        {/* CTA */}
        <div className="pt-2">
          <button
            type="button"
            onClick={calculate}
            disabled={loading}
            className="btn-primary w-full text-base py-3.5 group"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Calculating…
              </>
            ) : (
              <>
                <Wand2 className="w-4 h-4 mr-2 transition-transform group-hover:rotate-[14deg]" />
                Calculate My Rate
              </>
            )}
          </button>
          {error && (
            <p className="text-xs text-red-600 mt-3 text-center animate-fade-in">{error}</p>
          )}
        </div>
      </div>

      {/* Result */}
      {result && (
        <div className="space-y-4">
          {/* Quote card */}
          <div
            className="rounded-3xl p-7 text-white relative overflow-hidden animate-pop"
            style={{
              background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #8B5CF6 100%)',
              boxShadow: '0 14px 40px rgba(79, 70, 229, 0.35)',
            }}
          >
            <div className="absolute -top-12 -right-12 w-48 h-48 rounded-full bg-white/10 blur-2xl" />
            <div className="absolute -bottom-16 -left-12 w-56 h-56 rounded-full bg-white/10 blur-2xl" />
            <div className="relative">
              <div className="text-[10px] font-bold tracking-[0.18em] uppercase text-white/80 mb-2">
                Your suggested rate
              </div>
              <div className="flex items-baseline gap-3 flex-wrap">
                <span className="text-5xl sm:text-6xl font-black tracking-tight animate-count-glow">
                  $<AnimatedNumber value={result.quoted_usd} />
                </span>
                <span className="text-base font-bold text-white/85">USD</span>
                <button
                  type="button"
                  onClick={() => copyText(String(result.quoted_usd), 'number')}
                  className="ml-auto inline-flex items-center gap-1.5 bg-white/15 hover:bg-white/25 text-white text-xs font-bold px-3 py-1.5 rounded-full transition-all backdrop-blur-sm"
                >
                  {copied === 'number'
                    ? <><Check className="w-3.5 h-3.5" /> Copied</>
                    : <><Copy className="w-3.5 h-3.5" /> Copy</>}
                </button>
              </div>
              <p className="mt-4 text-sm text-white/90 leading-relaxed max-w-2xl">
                {result.explanation}
              </p>
              <div className="mt-5 flex flex-wrap gap-2">
                {result.market_range && (
                  <span className="inline-flex items-center gap-1.5 bg-white/15 text-white text-[11px] font-bold px-3 py-1.5 rounded-full backdrop-blur-sm">
                    <MapPin className="w-3 h-3" />
                    {result.market_range.city} {result.market_range.niche} market: ${result.market_range.low.toLocaleString()}–${result.market_range.high.toLocaleString()}
                  </span>
                )}
                <span className="inline-flex items-center gap-1.5 bg-white/15 text-white text-[11px] font-bold px-3 py-1.5 rounded-full backdrop-blur-sm">
                  <TrendingUp className="w-3 h-3" />
                  {result.engagement_pct.toFixed(1)}% engagement
                </span>
                <span className="inline-flex items-center gap-1.5 bg-white/15 text-white text-[11px] font-bold px-3 py-1.5 rounded-full backdrop-blur-sm">
                  {result.followers_used.toLocaleString()} followers
                </span>
              </div>
            </div>
          </div>

          {/* Breakdown */}
          <div className="card p-6 animate-fade-up delay-2">
            <div className="flex items-center gap-2 mb-4">
              <Info className="w-4 h-4 text-[#4F46E5]" />
              <span className="text-sm font-extrabold text-[#1E1B4B]">How we got there</span>
            </div>
            <div className="space-y-2 text-sm">
              {[
                { label: `Base CPM (${result.platform} · ${result.deliverable})`, value: `$${result.breakdown.base_cpm.toFixed(2)} / 1K`, mult: false },
                { label: `Followers × CPM`,        value: `$${result.breakdown.base_unit_usd.toLocaleString()}`, mult: false },
                { label: `Engagement multiplier`,  value: `${result.breakdown.engagement_multiplier}×`, mult: true },
                { label: `City multiplier`,        value: `${result.breakdown.city_multiplier}×`, mult: true },
                { label: `Niche multiplier`,       value: `${result.breakdown.niche_multiplier}×`, mult: true },
                { label: `Quantity`,               value: `× ${result.quantity}`, mult: true },
                { label: `Usage multiplier`,       value: `${result.breakdown.usage_multiplier}×`, mult: true },
                { label: `Exclusivity multiplier`, value: `${result.breakdown.exclusivity_multiplier}×`, mult: true },
              ].map((row, i) => (
                <div
                  key={row.label}
                  className="flex items-center justify-between border-b border-[#EEF2FF] last:border-b-0 py-2 animate-fade-up"
                  style={{ animationDelay: `${i * 35}ms` }}
                >
                  <span className="text-[#6B7280]">{row.label}</span>
                  <span className={`font-bold ${row.mult ? 'text-[#7C3AED]' : 'text-[#1E1B4B]'}`}>{row.value}</span>
                </div>
              ))}
              <div className="flex items-center justify-between pt-3">
                <span className="text-[#1E1B4B] font-extrabold">Total (rounded to nearest $25)</span>
                <span className="text-[#1E1B4B] font-extrabold text-lg">${result.quoted_usd.toLocaleString()}</span>
              </div>
            </div>
          </div>

          {/* Quote text */}
          <div className="card p-6 animate-fade-up delay-3">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#7C3AED]" />
                <span className="text-sm font-extrabold text-[#1E1B4B]">Quote-ready message</span>
              </div>
              <button
                type="button"
                onClick={() => copyText(result.quote_text, 'quote')}
                className="inline-flex items-center gap-1.5 text-xs font-bold text-[#4F46E5] hover:text-[#4338CA] transition-colors"
              >
                {copied === 'quote'
                  ? <><Check className="w-3.5 h-3.5" /> Copied!</>
                  : <><Copy className="w-3.5 h-3.5" /> Copy</>}
              </button>
            </div>
            <pre className="whitespace-pre-wrap text-sm text-[#1E1B4B] leading-relaxed font-sans bg-[#FAFAFE] rounded-xl p-4 border border-[#E0E7FF]">
              {result.quote_text}
            </pre>
            <p className="text-[11px] text-[#9CA3AF] mt-3">
              Hey {firstName} — paste this into your reply. Tweak the tone to match how you usually talk.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
