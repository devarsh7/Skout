'use client'

import { useEffect, useState } from 'react'
import { Mic, RefreshCw, Loader2, X, Check } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { creatorAgentGetVoice, creatorAgentRefreshVoice } from '@/lib/api'

export default function VoiceProfileCard() {
  const { token } = useAuth()
  const [voice, setVoice] = useState('')
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [mode, setMode] = useState<'view' | 'samples'>('view')
  const [samplesText, setSamplesText] = useState('')
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return
    creatorAgentGetVoice(token)
      .then(r => setVoice(r.voice_description))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [token])

  const handleRefresh = async (samples: string[] | null) => {
    if (!token) return
    setRefreshing(true)
    setError(null)
    try {
      const res = await creatorAgentRefreshVoice(samples, token)
      setVoice(res.voice_description)
      setSaved(true)
      setMode('view')
      setSamplesText('')
      setTimeout(() => setSaved(false), 1800)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not refresh voice')
    } finally {
      setRefreshing(false)
    }
  }

  const submitSamples = () => {
    const samples = samplesText
      .split(/\n{2,}|---/)
      .map(s => s.trim())
      .filter(s => s.length > 5)
    if (samples.length === 0) {
      setError('Paste at least one caption.')
      return
    }
    handleRefresh(samples)
  }

  return (
    <div
      className="card p-5 animate-fade-up delay-1 relative overflow-hidden"
      style={{
        background: 'linear-gradient(135deg, #FAFAFE 0%, #EEF2FF 100%)',
        borderColor: '#E0E7FF',
      }}
    >
      <div className="absolute -top-8 -right-8 w-32 h-32 rounded-full bg-[#7C3AED]/10 blur-2xl" />
      <div className="relative">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED)' }}
            >
              <Mic className="w-3.5 h-3.5 text-white" />
            </div>
            <div className="text-sm font-extrabold text-[#1E1B4B]">Your voice profile</div>
            {saved && (
              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-600 animate-fade-in">
                <Check className="w-3 h-3" /> Updated
              </span>
            )}
          </div>
        </div>

        {loading ? (
          <div className="h-16 skeleton-shimmer rounded-lg" />
        ) : voice ? (
          <p className="text-sm text-[#1E1B4B] leading-relaxed italic">&ldquo;{voice}&rdquo;</p>
        ) : (
          <p className="text-sm text-[#6B7280] leading-relaxed">
            We haven&apos;t profiled your voice yet. Refresh once and the agent will sound like you in every draft.
          </p>
        )}

        {/* Actions */}
        {mode === 'view' && (
          <div className="flex flex-wrap gap-2 mt-4">
            <button
              type="button"
              onClick={() => handleRefresh(null)}
              disabled={refreshing}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-[#4F46E5] hover:text-[#4338CA] hover:bg-white/60 px-2.5 py-1.5 rounded-lg transition-colors"
            >
              {refreshing
                ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Profiling…</>
                : <><RefreshCw className="w-3.5 h-3.5" /> Refresh from bio</>}
            </button>
            <button
              type="button"
              onClick={() => setMode('samples')}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-[#7C3AED] hover:text-[#6D28D9] hover:bg-white/60 px-2.5 py-1.5 rounded-lg transition-colors"
            >
              Paste captions to improve
            </button>
          </div>
        )}

        {mode === 'samples' && (
          <div className="mt-4 space-y-2 animate-fade-up">
            <textarea
              className="input text-xs min-h-[110px]"
              placeholder="Paste 3-5 of your real captions, one per blank line…"
              value={samplesText}
              onChange={e => setSamplesText(e.target.value)}
              autoFocus
            />
            <div className="flex gap-2">
              <button
                type="button"
                onClick={submitSamples}
                disabled={refreshing}
                className="btn-primary text-xs px-3 py-1.5 flex-1"
              >
                {refreshing
                  ? <><Loader2 className="w-3.5 h-3.5 animate-spin mr-1" /> Profiling…</>
                  : 'Profile my voice'}
              </button>
              <button
                type="button"
                onClick={() => { setMode('view'); setSamplesText(''); setError(null) }}
                className="btn-ghost text-xs px-3 py-1.5"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        {error && (
          <p className="text-[11px] text-red-600 mt-2 animate-fade-in">{error}</p>
        )}
      </div>
    </div>
  )
}
