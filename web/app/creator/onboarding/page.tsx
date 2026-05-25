'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { sendOTP, registerCreator } from '@/lib/api'
import { APIError } from '@/lib/api'
import { CheckCircle2, Loader2 } from 'lucide-react'

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

  const set = (k: keyof typeof form, v: string | string[]) =>
    setForm(prev => ({ ...prev, [k]: v }))

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
      setError(err instanceof APIError ? err.message : 'Failed to send OTP')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOTP = (e: React.FormEvent) => {
    e.preventDefault()
    if (form.otp.length < 4) { setError('Enter the OTP sent to your email'); return }
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
      }
      const user = await registerCreator(payload)
      setUserFromResponse(user)
      router.push('/creator/dashboard')
    } catch (err) {
      setError(err instanceof APIError ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const steps = ['Account', 'Verify', 'Profile']

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
          <h1 className="text-2xl font-bold mb-1" style={{ color: '#1E1B4B' }}>Join as a Creator</h1>
          <p className="text-sm" style={{ color: '#6B7280' }}>Get discovered by brands and grow your career</p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {steps.map((s, i) => {
            const stepKeys: Step[] = ['account', 'otp', 'profile']
            const isActive = stepKeys[i] === step
            const isDone = stepKeys.indexOf(step) > i
            return (
              <div key={s} className="flex items-center gap-2">
                <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
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
                <label className="label">Username</label>
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
                {loading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Send Verification Code'}
              </button>
            </form>
          )}

          {/* Step 2: OTP */}
          {step === 'otp' && (
            <form onSubmit={handleVerifyOTP} className="space-y-4">
              <p className="text-[#6B7280] text-sm text-center mb-4">
                We sent a code to <span className="font-semibold" style={{ color: '#4F46E5' }}>{form.email}</span>
              </p>
              {devOTP && (
                <div className="px-4 py-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-700 text-sm text-center">
                  Dev mode — your OTP is: <span className="font-bold">{devOTP}</span>
                </div>
              )}
              <div>
                <label className="label">Verification Code</label>
                <input className="input text-center text-2xl tracking-[0.5em] font-bold" placeholder="------" maxLength={6} value={form.otp} onChange={e => set('otp', e.target.value)} required />
              </div>
              <button type="submit" className="btn-primary w-full">Continue</button>
              <button type="button" onClick={() => setStep('account')} className="w-full text-[#9CA3AF] text-sm hover:text-[#1E1B4B] transition-colors">
                ← Back
              </button>
            </form>
          )}

          {/* Step 3: Profile */}
          {step === 'profile' && (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Full Name *</label>
                  <input className="input" placeholder="Jane Doe" value={form.full_name} onChange={e => set('full_name', e.target.value)} required />
                </div>
                <div>
                  <label className="label">Display Name</label>
                  <input className="input" placeholder="Jane Creates" value={form.display_name} onChange={e => set('display_name', e.target.value)} />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Instagram Handle</label>
                  <input className="input" placeholder="@handle" value={form.instagram_handle} onChange={e => set('instagram_handle', e.target.value.replace('@', ''))} />
                </div>
                <div>
                  <label className="label">TikTok Handle</label>
                  <input className="input" placeholder="@handle" value={form.tiktok_handle} onChange={e => set('tiktok_handle', e.target.value.replace('@', ''))} />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="label">IG Followers</label>
                  <input type="number" className="input" placeholder="0" value={form.instagram_followers} onChange={e => set('instagram_followers', e.target.value)} />
                </div>
                <div>
                  <label className="label">TikTok Followers</label>
                  <input type="number" className="input" placeholder="0" value={form.tiktok_followers} onChange={e => set('tiktok_followers', e.target.value)} />
                </div>
                <div>
                  <label className="label">Engagement %</label>
                  <input type="number" step="0.1" className="input" placeholder="3.5" value={form.avg_engagement_rate} onChange={e => set('avg_engagement_rate', e.target.value)} />
                </div>
              </div>

              <div>
                <label className="label">Bio</label>
                <textarea className="input resize-none h-20" placeholder="Tell brands about yourself..." value={form.bio} onChange={e => set('bio', e.target.value)} />
              </div>

              <div>
                <label className="label">Niches (select all that apply)</label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {NICHES.map(n => (
                    <button key={n} type="button" onClick={() => toggleNiche(n)}
                      className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                        form.niches.includes(n) ? 'bg-[#EEF2FF] text-[#4F46E5] border border-[#C7D2FE]' : 'bg-white text-[#6B7280] border border-[#E2E8F0] hover:border-[#C7D2FE]'
                      }`}>
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
                  <input className="input" placeholder="New York" value={form.city} onChange={e => set('city', e.target.value)} />
                </div>
              </div>

              <div>
                <label className="label">Minimum Rate (USD / collab)</label>
                <input type="number" className="input" placeholder="500" value={form.min_rate_usd} onChange={e => set('min_rate_usd', e.target.value)} />
              </div>

              <button type="submit" className="btn-primary w-full mt-2" disabled={loading}>
                {loading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Create Creator Profile'}
              </button>
            </form>
          )}
        </div>

        <p className="text-center text-[#6B7280] text-sm mt-6">
          Already have an account?{' '}
          <Link href="/login" className="text-violet-400 hover:text-violet-300 transition-colors">Log in</Link>
        </p>
      </div>
    </div>
  )
}
