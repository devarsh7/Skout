'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { sendOTP, registerBusiness } from '@/lib/api'
import { APIError } from '@/lib/api'
import { CheckCircle2, Loader2 } from 'lucide-react'

type Step = 'account' | 'otp' | 'brand'

const PLATFORMS = ['Instagram', 'TikTok', 'YouTube', 'Twitter', 'LinkedIn', 'Pinterest']
const INDUSTRIES = ['Fashion & Beauty', 'Food & Beverage', 'Tech & Gaming', 'Health & Fitness', 'Travel', 'Finance', 'Education', 'Entertainment', 'Retail', 'Other']

export default function BusinessOnboarding() {
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
    company_name: '',
    website: '',
    contact_name: '',
    country: 'US',
    industry: '',
    budget: '',
    platforms: [] as string[],
    goals: '',
  })

  const set = (k: keyof typeof form, v: string | string[]) =>
    setForm(prev => ({ ...prev, [k]: v }))

  const togglePlatform = (p: string) =>
    set('platforms', form.platforms.includes(p) ? form.platforms.filter(x => x !== p) : [...form.platforms, p])

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await sendOTP(form.email, form.company_name || form.username)
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
    setStep('brand')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const user = await registerBusiness(form)
      setUserFromResponse(user)
      router.push('/business/dashboard')
    } catch (err) {
      setError(err instanceof APIError ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const steps = ['Account', 'Verify', 'Brand']

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
          <h1 className="text-2xl font-bold text-white mb-1">Join as a Brand</h1>
          <p className="text-gray-500 text-sm">Start discovering the right creators for your campaigns</p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {steps.map((s, i) => {
            const stepKeys: Step[] = ['account', 'otp', 'brand']
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

          {step === 'account' && (
            <form onSubmit={handleSendOTP} className="space-y-4">
              <div>
                <label className="label">Username</label>
                <input className="input" placeholder="brand_account" value={form.username} onChange={e => set('username', e.target.value)} required minLength={3} />
              </div>
              <div>
                <label className="label">Work Email</label>
                <input type="email" className="input" placeholder="you@company.com" value={form.email} onChange={e => set('email', e.target.value)} required />
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

          {step === 'otp' && (
            <form onSubmit={handleVerifyOTP} className="space-y-4">
              <p className="text-[#6B7280] text-sm text-center mb-4">
                We sent a code to <span className="text-white">{form.email}</span>
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
              <button type="button" onClick={() => setStep('account')} className="w-full text-[#9CA3AF] text-sm hover:text-[#1E1B4B] transition-colors">← Back</button>
            </form>
          )}

          {step === 'brand' && (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">Company Name *</label>
                <input className="input" placeholder="Acme Corp" value={form.company_name} onChange={e => set('company_name', e.target.value)} required />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Contact Name</label>
                  <input className="input" placeholder="Your name" value={form.contact_name} onChange={e => set('contact_name', e.target.value)} />
                </div>
                <div>
                  <label className="label">Country</label>
                  <input className="input" placeholder="US" value={form.country} onChange={e => set('country', e.target.value)} />
                </div>
              </div>
              <div>
                <label className="label">Website</label>
                <input className="input" placeholder="https://yourcompany.com" value={form.website} onChange={e => set('website', e.target.value)} />
              </div>
              <div>
                <label className="label">Industry</label>
                <select className="input" value={form.industry} onChange={e => set('industry', e.target.value)}>
                  <option value="">Select industry</option>
                  {INDUSTRIES.map(i => <option key={i} value={i}>{i}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Monthly Budget</label>
                <select className="input" value={form.budget} onChange={e => set('budget', e.target.value)}>
                  <option value="">Select budget range</option>
                  <option value="<$1K">Under $1,000</option>
                  <option value="$1K-$5K">$1,000 – $5,000</option>
                  <option value="$5K-$20K">$5,000 – $20,000</option>
                  <option value="$20K+">$20,000+</option>
                </select>
              </div>
              <div>
                <label className="label">Target Platforms</label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {PLATFORMS.map(p => (
                    <button key={p} type="button" onClick={() => togglePlatform(p)}
                      className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                        form.platforms.includes(p) ? 'bg-[#EEF2FF] text-[#4F46E5] border border-[#C7D2FE]' : 'bg-white text-[#6B7280] border border-[#E2E8F0] hover:border-[#C7D2FE]'
                      }`}>
                      {p}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="label">Campaign Goals</label>
                <textarea className="input resize-none h-16" placeholder="e.g. Brand awareness, product launch, increase sales..." value={form.goals} onChange={e => set('goals', e.target.value)} />
              </div>
              <button type="submit" className="btn-primary w-full mt-2" disabled={loading}>
                {loading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Create Brand Account'}
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
