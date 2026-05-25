'use client'

import { useState } from 'react'
import { draftOutreach } from '@/lib/api'
import { APIError } from '@/lib/api'
import { Loader2, Copy, CheckCheck, Mail } from 'lucide-react'

export default function OutreachPage() {
  const [form, setForm] = useState({
    creator_name: '',
    creator_niche: '',
    brand_name: '',
    campaign_brief: '',
    outreach_type: 'dm',
  })
  const [draft, setDraft] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  const set = (k: keyof typeof form, v: string) => setForm(p => ({ ...p, [k]: v }))

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await draftOutreach(form)
      setDraft(res.draft)
    } catch (err) {
      setError(err instanceof APIError ? err.message : 'Failed to generate draft')
    } finally {
      setLoading(false)
    }
  }

  const copyDraft = () => {
    navigator.clipboard.writeText(draft)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">AI Outreach</h1>
        <p className="text-gray-500">Generate personalized messages for creators — ready to send.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-white font-semibold mb-5 flex items-center gap-2">
            <Mail className="w-4 h-4 text-violet-400" />
            Campaign Details
          </h2>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="label">Creator Name</label>
              <input className="input" placeholder="Emma Johnson" value={form.creator_name} onChange={e => set('creator_name', e.target.value)} required />
            </div>
            <div>
              <label className="label">Creator's Niche</label>
              <input className="input" placeholder="Sustainable fashion, lifestyle" value={form.creator_niche} onChange={e => set('creator_niche', e.target.value)} />
            </div>
            <div>
              <label className="label">Your Brand Name</label>
              <input className="input" placeholder="Acme Corp" value={form.brand_name} onChange={e => set('brand_name', e.target.value)} required />
            </div>
            <div>
              <label className="label">Campaign Brief</label>
              <textarea
                className="input resize-none h-28"
                placeholder="Describe your campaign: product, goals, deliverables, budget range..."
                value={form.campaign_brief}
                onChange={e => set('campaign_brief', e.target.value)}
                required
              />
            </div>
            <div>
              <label className="label">Outreach Type</label>
              <div className="flex gap-3">
                {['dm', 'email'].map(t => (
                  <button key={t} type="button" onClick={() => set('outreach_type', t)}
                    className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                      form.outreach_type === t ? 'bg-violet-500/25 text-violet-300 border border-violet-500/40' : 'bg-white/5 text-gray-400 border border-white/10 hover:border-white/20'
                    }`}>
                    {t === 'dm' ? 'Direct Message' : 'Email'}
                  </button>
                ))}
              </div>
            </div>
            {error && <div className="px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Generate Draft'}
            </button>
          </form>
        </div>

        <div className="card p-6 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white font-semibold">Generated Draft</h2>
            {draft && (
              <button onClick={copyDraft} className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-white transition-colors px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10">
                {copied ? <CheckCheck className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? 'Copied!' : 'Copy'}
              </button>
            )}
          </div>

          {draft ? (
            <textarea
              className="input flex-1 resize-none text-sm leading-relaxed min-h-[300px]"
              value={draft}
              onChange={e => setDraft(e.target.value)}
            />
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-600 text-sm">
              {loading ? (
                <div className="text-center">
                  <Loader2 className="w-6 h-6 animate-spin text-violet-500 mx-auto mb-2" />
                  <p>Crafting your message…</p>
                </div>
              ) : (
                'Fill in the campaign details and click Generate'
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
