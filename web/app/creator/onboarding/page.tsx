'use client'

import { useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { sendOTP, registerCreator, getInstagramAuthUrl, getInstagramOauthData } from '@/lib/api'
import { APIError } from '@/lib/api'
import { CheckCircle2, Instagram, Loader2 } from 'lucide-react'

const IG_FORM_KEY = 'skout_onboarding_form'

type Step = 'account' | 'otp' | 'profile'

const NICHES = ['Fashion', 'Beauty', 'Fitness', 'Food', 'Travel', 'Tech', 'Gaming', 'Lifestyle', 'Business', 'Education', 'Music', 'Art']

export default function CreatorOnboarding() {
  const router = useRouter()
  const { setUserFromResponse } = useAuth()
  const [step, setStep] = useState<Step>('account')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [devOTP, setDevOTP] = useState('')

  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    otp: '',
    full_name: '',
    display_name: '',
    instagram_handle: '',
    tiktok_handle: '',
    youtube_channel: '',
    instagram_followers: '',
    tiktok_followers: '',
    youtube_subscribers: '',
    avg_engagement_rate: '',
    bio: '',
    niches: [] as string[],
    country: 'US',
    city: '',
    min_rate_usd: '',
  })

  const [igStatus, setIgStatus] = useState<'idle' | 'connecting' | 'connected' | 'error'>('idle')
  const [igSummary, setIgSummary] = useState('')
  const [igToken, setIgToken] = useState('')

  const set = (k: keyof typeof form, v: string | string[]) =>
    setForm(prev => ({ ...prev, [k]: v }))

  // Returning from Instagram OAuth: restore form, pull fetched data, prefill
  const igFetched = useRef(false)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)

    // Backend redirected with a readable error code
    const igError = params.get('ig_error')
    if (igError && !igFetched.current) {
      igFetched.current = true
      const saved = sessionStorage.getItem(IG_FORM_KEY)
      if (saved) {
        try {
          const { form: savedForm, step: savedStep } = JSON.parse(saved)
          setForm(prev => ({ ...prev, ...savedForm }))
          setStep(savedStep || 'profile')
        } catch { /* ignore corrupt state */ }
        sessionStorage.removeItem(IG_FORM_KEY)
      }
      setIgStatus('error')
      setError({
        expired: 'The Instagram connection took too long and expired — please try again.',
        token_exchange: "Instagram didn't accept the connection — please try again.",
      }[igError] || 'Instagram connection failed — please try again.')
      window.history.replaceState({}, '', '/creator/onboarding')
      return
    }

    const igState = params.get('ig_state')
    if (!igState || igFetched.current) return
    igFetched.current = true

    const saved = sessionStorage.getItem(IG_FORM_KEY)
    if (saved) {
      try {
        const { form: savedForm, step: savedStep } = JSON.parse(saved)
        setForm(prev => ({ ...prev, ...savedForm }))
        setStep(savedStep || 'profile')
      } catch { /* ignore corrupt state */ }
      sessionStorage.removeItem(IG_FORM_KEY)
    }

    setIgStatus('connecting')
    getInstagramOauthData(igState)
      .then(({ profile, reels, token }) => {
        if (!profile?.found) { setIgStatus('error'); return }
        setIgToken(token || '')
        setForm(prev => ({
          ...prev,
          instagram_handle: profile.username || prev.instagram_handle,
          instagram_followers: String(profile.followers ?? prev.instagram_followers),
          full_name: prev.full_name || profile.full_name || '',
          bio: prev.bio || profile.bio || '',
        }))
        const withReach = (reels || []).filter(r => r.reach > 0)
        if (withReach.length) {
          const avgEng = withReach.reduce((s, r) => s + ((r.likes + r.comments) / r.reach) * 100, 0) / withReach.length
          setForm(prev => ({ ...prev, avg_engagement_rate: avgEng.toFixed(1) }))
        }
        setIgSummary(
          `@${profile.username} · ${(profile.followers ?? 0).toLocaleString()} followers` +
          (reels?.length ? ` · ${reels.length} recent reels` : '')
        )
        setIgStatus('connected')
      })
      .catch(() => setIgStatus('error'))
      .finally(() => window.history.replaceState({}, '', '/creator/onboarding'))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleConnectInstagram = async () => {
    setError('')
    setIgStatus('connecting')
    try {
      sessionStorage.setItem(IG_FORM_KEY, JSON.stringify({ form, step }))
      const { url } = await getInstagramAuthUrl()
      window.location.href = url
    } catch (err) {
      setIgStatus('error')
      setError(err instanceof APIError ? err.message : 'Could not start Instagram login')
    }
  }

  const toggleNiche = (n: string) =>
    set('niches', form.niches.includes(n) ? form.niches.filter(x => x !== n) : [...form.niches, n])

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await sendOTP(form.email, form.username)
      if (res.dev_otp) setDevOTP(res.dev_otp)
      setStep('otp')
    } catch (err) {
      setError(err instanceof APIError ? err.message : 'Failed to send code')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOTP = (e: React.FormEvent) => {
    e.preventDefault()
    if (form.otp.length < 4) { setError('Enter the code we just sent you'); return }
    setError('')
    setStep('profile')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const payload = {
        ...form,
        instagram_followers: parseInt(form.instagram_followers) || 0,
        tiktok_followers: parseInt(form.tiktok_followers) || 0,
        youtube_subscribers: parseInt(form.youtube_subscribers) || 0,
        avg_engagement_rate: parseFloat(form.avg_engagement_rate) || 0,
        min_rate_usd: parseFloat(form.min_rate_usd) || 0,
        open_to_collabs: true,
        languages: ['English'],
        preferred_collab_types: [],
        instagram_access_token: igToken || undefined,
      }
      const user = await registerCreator(payload)
      setUserFromResponse(user)
      router.push('/creator/dashboard')
    } catch (err) {
      setError(err instanceof APIError ? err.message : 'Something broke. Try again?')
    } finally {
      setLoading(false)
    }
  }

  const steps = ['Sign up', 'Verify', 'Profile']

  const heroCopy = {
    account: {
      title: 'Get Found Before Famous.',
      sub: 'Three fields, two minutes. Local brands are already searching.',
    },
    otp: {
      title: 'Check your inbox.',
      sub: 'We just sent a 6-digit code. Drop it in to keep going.',
    },
    profile: {
      title: 'Tell brands who you are.',
      sub: 'The more you share, the better we match. Skip anything you’re not sure about.',
    },
  }[step]

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12" style={{ background: 'linear-gradient(150deg,#EEF2FF 0%,#F8FAFF 50%,#EFF6FF 100%)' }}>
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div style={{ position: 'absolute', width: 500, height: 500, top: -100, right: -100, background: 'rgba(99,102,241,.15)', borderRadius: '50%', filter: 'blur(60px)' }} />
        <div style={{ position: 'absolute', width: 400, height: 400, bottom: -80, left: -80, background: 'rgba(139,92,246,.1)', borderRadius: '50%', filter: 'blur(60px)' }} />
      </div>

      <div className="relative w-full max-w-lg">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-4">
            <div className="w-9 h-9 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold">S</span>
            </div>
          </Link>

          <div
            className="inline-flex items-center gap-2 mb-3"
            style={{
              background: '#fff',
              border: '1.5px solid #C7D2FE',
              color: '#4F46E5',
              fontWeight: 700,
              fontSize: 10.5,
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              padding: '5px 14px',
              borderRadius: 999,
              boxShadow: '0 2px 8px rgba(79,70,229,.1)',
            }}
          >
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#4F46E5' }} />
            Built for 500–50K Followers
          </div>

          <h1
            className="text-3xl font-black mb-2"
            style={{ color: '#1E1B4B', letterSpacing: '-0.03em', lineHeight: 1.1 }}
          >
            {heroCopy.title.includes('Famous') ? (
              <>
                Get Found{' '}
                <span
                  style={{
                    background: 'linear-gradient(135deg,#4F46E5,#8B5CF6)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                  }}
                >
                  Before Famous.
                </span>
              </>
            ) : (
              heroCopy.title
            )}
          </h1>
          <p className="text-sm max-w-sm mx-auto" style={{ color: '#6B7280', lineHeight: 1.6 }}>{heroCopy.sub}</p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {steps.map((s, i) => {
            const stepKeys: Step[] = ['account', 'otp', 'profile']
            const isActive = stepKeys[i] === step
            const isDone = stepKeys.indexOf(step) > i
            return (
              <div key={s} className="flex items-center gap-2">
                <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                  isActive ? 'bg-[#EEF2FF] text-[#4F46E5] border border-[#C7D2FE]' :
                  isDone ? 'bg-green-50 text-green-600' : 'text-[#9CA3AF]'
                }`}>
                  {isDone && <CheckCircle2 className="w-3.5 h-3.5" />}
                  {s}
                </div>
                {i < 2 && <div className="w-6 h-px bg-[#E2E8F0]" />}
              </div>
            )
          })}
        </div>

        <div className="card p-8">
          {error && (
            <div className="mb-5 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm">{error}</div>
          )}

          {/* Step 1: Account */}
          {step === 'account' && (
            <form onSubmit={handleSendOTP} className="space-y-4">
              <div>
                <label className="label">Your @ on Skout</label>
                <input className="input" placeholder="your_handle" value={form.username} onChange={e => set('username', e.target.value)} required minLength={3} />
              </div>
              <div>
                <label className="label">Email</label>
                <input type="email" className="input" placeholder="you@example.com" value={form.email} onChange={e => set('email', e.target.value)} required />
              </div>
              <div>
                <label className="label">Password</label>
                <input type="password" className="input" placeholder="Min 8 characters" value={form.password} onChange={e => set('password', e.target.value)} required minLength={8} />
              </div>
              <button type="submit" className="btn-primary w-full mt-2" disabled={loading}>
                {loading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Send My Code →'}
              </button>
              <p className="text-center text-[11px] text-[#9CA3AF] pt-1">
                Free forever for creators &nbsp;·&nbsp; No follower minimum
              </p>
            </form>
          )}

          {/* Step 2: OTP */}
          {step === 'otp' && (
            <form onSubmit={handleVerifyOTP} className="space-y-4">
              <p className="text-[#6B7280] text-sm text-center mb-4">
                Code sent to <span className="font-semibold" style={{ color: '#4F46E5' }}>{form.email}</span>
              </p>
              {devOTP && (
                <div className="px-4 py-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-700 text-sm text-center">
                  Dev mode — your code is: <span className="font-bold">{devOTP}</span>
                </div>
              )}
              <div>
                <label className="label">6-digit code</label>
                <input className="input text-center text-2xl tracking-[0.5em] font-bold" placeholder="------" maxLength={6} value={form.otp} onChange={e => set('otp', e.target.value)} required />
              </div>
              <button type="submit" className="btn-primary w-full">Verify & Continue →</button>
              <button type="button" onClick={() => setStep('account')} className="w-full text-[#9CA3AF] text-sm hover:text-[#1E1B4B] transition-colors">
                ← Back
              </button>
            </form>
          )}

          {/* Step 3: Profile */}
          {step === 'profile' && (
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Instagram connect — auto-fills handle, followers, bio, engagement */}
              <div className="rounded-xl border border-[#C7D2FE] bg-[#EEF2FF] p-4">
                {igStatus === 'connected' ? (
                  <div className="flex items-center gap-2 text-sm text-[#1E1B4B]">
                    <CheckCircle2 className="w-4 h-4 text-green-600 shrink-0" />
                    <span className="font-semibold">{igSummary}</span>
                    <span className="text-[#6B7280]">— stats auto-filled below</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-[#1E1B4B]">Connect Instagram</p>
                      <p className="text-xs text-[#6B7280]">Auto-fill your real followers, bio & engagement</p>
                    </div>
                    <button
                      type="button"
                      onClick={handleConnectInstagram}
                      disabled={igStatus === 'connecting'}
                      className="btn-primary shrink-0 !px-4 !py-2 text-sm flex items-center gap-2"
                    >
                      {igStatus === 'connecting'
                        ? <Loader2 className="w-4 h-4 animate-spin" />
                        : <><Instagram className="w-4 h-4" /> Connect</>}
                    </button>
                  </div>
                )}
                {igStatus === 'error' && (
                  <p className="text-xs text-red-600 mt-2">Instagram connection failed — you can fill the fields manually.</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Full name *</label>
                  <input className="input" placeholder="Jane Doe" value={form.full_name} onChange={e => set('full_name', e.target.value)} required />
                </div>
                <div>
                  <label className="label">Creator name</label>
                  <input className="input" placeholder="Jane Creates" value={form.display_name} onChange={e => set('display_name', e.target.value)} />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Instagram</label>
                  <input className="input" placeholder="@handle" value={form.instagram_handle} onChange={e => set('instagram_handle', e.target.value.replace('@', ''))} />
                </div>
                <div>
                  <label className="label">TikTok</label>
                  <input className="input" placeholder="@handle" value={form.tiktok_handle} onChange={e => set('tiktok_handle', e.target.value.replace('@', ''))} />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="label">IG followers</label>
                  <input type="number" className="input" placeholder="0" value={form.instagram_followers} onChange={e => set('instagram_followers', e.target.value)} />
                </div>
                <div>
                  <label className="label">TikTok followers</label>
                  <input type="number" className="input" placeholder="0" value={form.tiktok_followers} onChange={e => set('tiktok_followers', e.target.value)} />
                </div>
                <div>
                  <label className="label">Engagement %</label>
                  <input type="number" step="0.1" className="input" placeholder="3.5" value={form.avg_engagement_rate} onChange={e => set('avg_engagement_rate', e.target.value)} />
                </div>
              </div>

              <div>
                <label className="label">Pitch yourself</label>
                <textarea
                  className="input resize-none h-20"
                  placeholder="What do you make, and for whom? Two sentences is plenty."
                  value={form.bio}
                  onChange={e => set('bio', e.target.value)}
                />
              </div>

              <div>
                <label className="label">Pick your niches</label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {NICHES.map(n => (
                    <button
                      key={n}
                      type="button"
                      onClick={() => toggleNiche(n)}
                      className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                        form.niches.includes(n)
                          ? 'bg-[#EEF2FF] text-[#4F46E5] border border-[#C7D2FE]'
                          : 'bg-white text-[#6B7280] border border-[#E2E8F0] hover:border-[#C7D2FE]'
                      }`}
                    >
                      {n}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Country</label>
                  <input className="input" placeholder="US" value={form.country} onChange={e => set('country', e.target.value)} />
                </div>
                <div>
                  <label className="label">City</label>
                  <input className="input" placeholder="Brooklyn" value={form.city} onChange={e => set('city', e.target.value)} />
                </div>
              </div>

              <div>
                <label className="label">Your rate (USD per collab)</label>
                <input
                  type="number"
                  className="input"
                  placeholder="500 — leave blank if you want brands to offer"
                  value={form.min_rate_usd}
                  onChange={e => set('min_rate_usd', e.target.value)}
                />
              </div>

              <button type="submit" className="btn-primary w-full mt-2" disabled={loading}>
                {loading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Go Live on Skout →'}
              </button>
              <p className="text-center text-[11px] text-[#9CA3AF] pt-1">
                You can edit any of this later from your dashboard.
              </p>
            </form>
          )}
        </div>

        <p className="text-center text-[#6B7280] text-sm mt-6">
          Already on Skout?{' '}
          <Link href="/login" className="font-semibold transition-colors" style={{ color: '#4F46E5' }}>
            Log in
          </Link>
        </p>
      </div>
    </div>
  )
}
