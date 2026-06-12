'use client'

import { useState } from 'react'
import {
  FileSearch, AlertTriangle, DollarSign, MessageSquareQuote, Loader2,
  Copy, Check, Sparkles, ShieldCheck, TrendingDown, BadgeDollarSign,
} from 'lucide-react'
import { creatorAgentEvaluateBrief, BriefEvalResult } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

// ── Example brief (Toronto-flavoured) ─────────────────────────────────────────

const EXAMPLE_BRIEF = `Hi! We're a Toronto-based DTC skincare brand (Queen West area) launching a new vitamin C serum next month.

Looking for one Instagram Reel + 3 stories showing your morning routine. We'd love to have perpetual usage rights so we can use the content forever across our paid ads + organic.

Tight timeline — we need it live by next Tuesday. Budget: $300 USD. Great exposure to our 80K audience!

Also — we'd need 90-day exclusivity on the skincare category.

Let me know!
— Maya @ GlowLabs`

// ── Helpers ──────────────────────────────────────────────────────────────────

function verdictColor(verdict: string) {
  if (verdict === 'fair')     return { from: '#10B981', to: '#059669', Icon: ShieldCheck,  label: 'Fair offer' }
  if (verdict === 'below')    return { from: '#F59E0B', to: '#D97706', Icon: TrendingDown, label: 'Below market' }
  if (verdict === 'lowball')  return { from: '#EF4444', to: '#DC2626', Icon: AlertTriangle, label: 'Lowball' }
  return                            { from: '#6366F1', to: '#7C3AED', Icon: BadgeDollarSign, label: 'No offer stated' }
}

// ── Main ─────────────────────────────────────────────────────────────────────

export default function BriefEvaluator() {
  const { token } = useAuth()
  const [briefText, setBriefText] = useState('')
  const [loading,   setLoading]   = useState(false)
  const [error,     setError]     = useState<string | null>(null)
  const [result,    setResult]    = useState<BriefEvalResult | null>(null)
  const [copied,    setCopied]    = useState(false)

  const evaluate = async () => {
    if (!token || !briefText.trim() || loading) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await creatorAgentEvaluateBrief(briefText.trim(), token)
      setResult(res)
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Could not evaluate brief'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const copyCounter = async () => {
    if (!result) return
    try {
      await navigator.clipboard.writeText(result.counter_draft)
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    } catch {/* ignore */}
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start gap-3 animate-fade-up">
        <div
          className="w-11 h-11 rounded-2xl flex items-center justify-center animate-gradient shrink-0"
          style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED, #8B5CF6)' }}
        >
          <FileSearch className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-lg font-extrabold text-[#1E1B4B] tracking-tight">
            Brand Brief Evaluator
          </h2>
          <p className="text-sm text-[#6B7280] mt-0.5">
            Paste any inbound brand brief. We&apos;ll decode the asks, flag traps, and draft your counter.
          </p>
        </div>
      </div>

      {/* Input card */}
      <div className="card p-6 space-y-4 animate-fade-up delay-1">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="section-label !mb-0">The Brief</span>
            <button
              type="button"
              onClick={() => setBriefText(EXAMPLE_BRIEF)}
              className="text-[11px] font-bold text-[#4F46E5] hover:text-[#4338CA] transition-colors"
            >
              Try a sample brief
            </button>
          </div>
          <textarea
            className="input min-h-[200px] resize-y leading-relaxed"
            placeholder="Paste the full DM or email from the brand here…"
            value={briefText}
            onChange={e => setBriefText(e.target.value)}
          />
          <div className="text-[11px] text-[#9CA3AF] mt-1.5">
            {briefText.length} characters · we&apos;ll detect deliverables, pay, usage rights, exclusivity, and red flags.
          </div>
        </div>

        <button
          type="button"
          onClick={evaluate}
          disabled={loading || briefText.trim().length < 20}
          className="btn-primary w-full text-base py-3.5 group"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Reading the brief…
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 mr-2 transition-transform group-hover:rotate-[14deg]" />
              Evaluate Brief
            </>
          )}
        </button>

        {error && (
          <p className="text-xs text-red-600 text-center animate-fade-in">{error}</p>
        )}
      </div>

      {/* Result */}
      {result && (
        <div className="space-y-5">
          {/* Top row: 2 cards side by side */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Pay verdict */}
            {(() => {
              const v = verdictColor(result.pay_analysis.verdict)
              const Icon = v.Icon
              return (
                <div
                  className="rounded-2xl p-6 text-white relative overflow-hidden animate-pop"
                  style={{
                    background: `linear-gradient(135deg, ${v.from}, ${v.to})`,
                    boxShadow: `0 10px 30px ${v.from}55`,
                  }}
                >
                  <div className="absolute -top-10 -right-10 w-32 h-32 rounded-full bg-white/10 blur-2xl" />
                  <div className="flex items-center gap-2 mb-3 relative">
                    <Icon className="w-4 h-4" />
                    <span className="text-[10px] font-bold tracking-[0.18em] uppercase text-white/85">
                      {v.label}
                    </span>
                  </div>
                  <div className="relative">
                    <div className="flex items-baseline gap-2">
                      <span className="text-4xl font-black">
                        ${result.pay_analysis.fair_rate_usd.toLocaleString()}
                      </span>
                      <span className="text-sm font-bold text-white/85">fair rate</span>
                    </div>
                    {result.pay_analysis.offered_usd !== null && (
                      <div className="text-sm text-white/85 mt-1">
                        Brand offered:{' '}
                        <span className="font-bold text-white">
                          ${result.pay_analysis.offered_usd.toLocaleString()}
                        </span>
                        {result.pay_analysis.ratio !== undefined && (
                          <span className="ml-2 text-white/75">
                            ({(result.pay_analysis.ratio * 100).toFixed(0)}% of fair)
                          </span>
                        )}
                      </div>
                    )}
                    <p className="text-sm text-white/95 mt-3 leading-relaxed">
                      {result.pay_analysis.headline}
                    </p>
                  </div>
                </div>
              )
            })()}

            {/* Extracted facts */}
            <div className="card p-6 animate-fade-up delay-1">
              <div className="flex items-center gap-2 mb-3">
                <DollarSign className="w-4 h-4 text-[#4F46E5]" />
                <span className="text-sm font-extrabold text-[#1E1B4B]">What they&apos;re asking for</span>
              </div>
              <ul className="space-y-2 text-sm">
                {[
                  ['Brand',        result.extracted.brand_name || '—'],
                  ['Deliverables', result.extracted.deliverables],
                  ['Platform',     result.extracted.platform],
                  ['Usage',        result.extracted.usage],
                  ['Exclusivity',  result.extracted.exclusivity],
                  ['Timeline',     result.extracted.timeline],
                ].map(([k, v], i) => (
                  <li
                    key={k}
                    className="flex items-start justify-between gap-3 border-b border-[#EEF2FF] last:border-b-0 pb-2 last:pb-0 animate-fade-up"
                    style={{ animationDelay: `${i * 40}ms` }}
                  >
                    <span className="text-[#6B7280] text-xs font-bold uppercase tracking-wide">{k}</span>
                    <span className="text-[#1E1B4B] font-semibold text-right">{v as string}</span>
                  </li>
                ))}
              </ul>
              {result.extracted.key_clauses.length > 0 && (
                <div className="mt-4 pt-3 border-t border-[#EEF2FF]">
                  <div className="text-[10px] font-bold tracking-[0.12em] uppercase text-[#9CA3AF] mb-2">
                    Key clauses
                  </div>
                  <ul className="space-y-1.5">
                    {result.extracted.key_clauses.map((kc, i) => (
                      <li key={i} className="text-xs text-[#1E1B4B] flex items-start gap-1.5">
                        <span className="text-[#7C3AED] mt-0.5">▸</span>
                        <span>{kc}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Red flags */}
          {result.red_flags.length > 0 && (
            <div className="card p-6 border-l-4 !border-l-[#F59E0B] animate-fade-up delay-2">
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="w-4 h-4 text-[#D97706]" />
                <span className="text-sm font-extrabold text-[#1E1B4B]">
                  {result.red_flags.length} red flag{result.red_flags.length > 1 ? 's' : ''} detected
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {result.red_flags.map((rf, i) => (
                  <div
                    key={rf.label}
                    className="rounded-xl bg-[#FFFBEB] border border-[#FDE68A] p-4 transition-all hover:-translate-y-[1px] hover:shadow-md animate-fade-up"
                    style={{ animationDelay: `${i * 60}ms` }}
                  >
                    <div className="text-xs font-extrabold text-[#92400E] mb-1.5">{rf.label}</div>
                    <div className="text-xs text-[#1E1B4B] leading-relaxed">{rf.advice}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Counter draft */}
          <div className="card p-6 animate-fade-up delay-3">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <MessageSquareQuote className="w-4 h-4 text-[#7C3AED]" />
                <span className="text-sm font-extrabold text-[#1E1B4B]">Your counter-proposal</span>
              </div>
              <button
                type="button"
                onClick={copyCounter}
                className="inline-flex items-center gap-1.5 text-xs font-bold text-[#4F46E5] hover:text-[#4338CA] transition-colors"
              >
                {copied
                  ? <><Check className="w-3.5 h-3.5" /> Copied!</>
                  : <><Copy className="w-3.5 h-3.5" /> Copy</>}
              </button>
            </div>
            <pre className="whitespace-pre-wrap text-sm text-[#1E1B4B] leading-relaxed font-sans bg-[#FAFAFE] rounded-xl p-4 border border-[#E0E7FF]">
              {result.counter_draft}
            </pre>
            <p className="text-[11px] text-[#9CA3AF] mt-3">
              Tweak the tone to sound like you. Then send it before they hear back from someone else.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
