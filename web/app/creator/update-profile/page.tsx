'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { getCreator, updateCreator } from '@/lib/api'
import { Creator } from '@/types'
import { APIError } from '@/lib/api'
import { Loader2, CheckCircle2 } from 'lucide-react'

const NICHES = ['Fashion', 'Beauty', 'Fitness', 'Food', 'Travel', 'Tech', 'Gaming', 'Lifestyle', 'Business', 'Education', 'Music', 'Art']

export default function UpdateProfilePage() {
  const { user, token } = useAuth()
  const [creator, setCreator] = useState<Creator | null>(null)
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    display_name: '',
    bio: '',
    instagram_handle: '',
    tiktok_handle: '',
    youtube_channel: '',
    instagram_followers: '',
    tiktok_followers: '',
    youtube_subscribers: '',
    avg_engagement_rate: '',
    avg_views: '',
    niches: [] as string[],
    city: '',
    country: '',
    min_rate_usd: '',
    open_to_collabs: true,
  })

  useEffect(() => {
    if (!user?.creator_id) return
    getCreator(user.creator_id).then(c => {
      setCreator(c)
      setForm({
        display_name: c.display_name || '',
        bio: c.bio || '',
        instagram_handle: c.instagram_handle || '',
        tiktok_handle: c.tiktok_handle || '',
        youtube_channel: c.youtube_channel || '',
        instagram_followers: String(c.instagram_followers || 0),
        tiktok_followers: String(c.tiktok_followers || 0),
        youtube_subscribers: String(c.youtube_subscribers || 0),
        avg_engagement_rate: String(c.avg_engagement_rate || 0),
        avg_views: String(c.avg_views || 0),
        niches: c.niches || [],
        city: c.city || '',
        country: c.country || '',
        min_rate_usd: String(c.min_rate_usd || 0),
        open_to_collabs: c.open_to_collabs,
      })
    }).catch(() => {})
  }, [user])

  const set = (k: keyof typeof form, v: string | string[] | boolean) =>
    setForm(prev => ({ ...prev, [k]: v }))

  const toggleNiche = (n: string) =>
    set('niches', form.niches.includes(n) ? form.niches.filter(x => x !== n) : [...form.niches, n])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user?.creator_id || !token) return
    setError('')
    setLoading(true)
    try {
      const payload = {
        ...form,
        instagram_followers: parseInt(form.instagram_followers) || 0,
        tiktok_followers: parseInt(form.tiktok_followers) || 0,
        youtube_subscribers: parseInt(form.youtube_subscribers) || 0,
        avg_engagement_rate: parseFloat(form.avg_engagement_rate) || 0,
        avg_views: parseInt(form.avg_views) || 0,
        min_rate_usd: parseFloat(form.min_rate_usd) || 0,
      }
      await updateCreator(user.creator_id, payload, token)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err) {
      setError(err instanceof APIError ? err.message : 'Save failed')
    } finally {
      setLoading(false)
    }
  }

  if (!creator) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-6 h-6 animate-spin text-violet-500" />
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Update Profile</h1>
        <p className="text-gray-500">Keep your stats current to improve brand matching.</p>
      </div>

      <form onSubmit={handleSave} className="max-w-2xl space-y-6">
        {error && <div className="px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}
        {saved && (
          <div className="px-4 py-3 rounded-xl bg-green-500/10 border border-green-500/20 text-green-400 text-sm flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            Profile saved successfully
          </div>
        )}

        <div className="card p-6 space-y-4">
          <h2 className="text-white font-semibold">Basic Info</h2>
          <div>
            <label className="label">Display Name</label>
            <input className="input" value={form.display_name} onChange={e => set('display_name', e.target.value)} />
          </div>
          <div>
            <label className="label">Bio</label>
            <textarea className="input resize-none h-24" value={form.bio} onChange={e => set('bio', e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">City</label>
              <input className="input" value={form.city} onChange={e => set('city', e.target.value)} />
            </div>
            <div>
              <label className="label">Country</label>
              <input className="input" value={form.country} onChange={e => set('country', e.target.value)} />
            </div>
          </div>
        </div>

        <div className="card p-6 space-y-4">
          <h2 className="text-white font-semibold">Social Handles</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Instagram</label>
              <input className="input" placeholder="handle (no @)" value={form.instagram_handle} onChange={e => set('instagram_handle', e.target.value)} />
            </div>
            <div>
              <label className="label">TikTok</label>
              <input className="input" placeholder="handle (no @)" value={form.tiktok_handle} onChange={e => set('tiktok_handle', e.target.value)} />
            </div>
            <div>
              <label className="label">YouTube Channel</label>
              <input className="input" value={form.youtube_channel} onChange={e => set('youtube_channel', e.target.value)} />
            </div>
          </div>
        </div>

        <div className="card p-6 space-y-4">
          <h2 className="text-white font-semibold">Stats</h2>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="label">IG Followers</label>
              <input type="number" className="input" value={form.instagram_followers} onChange={e => set('instagram_followers', e.target.value)} />
            </div>
            <div>
              <label className="label">TikTok Followers</label>
              <input type="number" className="input" value={form.tiktok_followers} onChange={e => set('tiktok_followers', e.target.value)} />
            </div>
            <div>
              <label className="label">YT Subscribers</label>
              <input type="number" className="input" value={form.youtube_subscribers} onChange={e => set('youtube_subscribers', e.target.value)} />
            </div>
            <div>
              <label className="label">Engagement %</label>
              <input type="number" step="0.1" className="input" value={form.avg_engagement_rate} onChange={e => set('avg_engagement_rate', e.target.value)} />
            </div>
            <div>
              <label className="label">Avg Views</label>
              <input type="number" className="input" value={form.avg_views} onChange={e => set('avg_views', e.target.value)} />
            </div>
            <div>
              <label className="label">Min Rate (USD)</label>
              <input type="number" className="input" value={form.min_rate_usd} onChange={e => set('min_rate_usd', e.target.value)} />
            </div>
          </div>

          <div className="flex items-center gap-3">
            <input type="checkbox" id="collab" checked={form.open_to_collabs} onChange={e => set('open_to_collabs', e.target.checked)} className="w-4 h-4 accent-violet-500" />
            <label htmlFor="collab" className="text-gray-400 text-sm cursor-pointer">Open to collaborations</label>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-white font-semibold mb-3">Niches</h2>
          <div className="flex flex-wrap gap-2">
            {NICHES.map(n => (
              <button key={n} type="button" onClick={() => toggleNiche(n)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                  form.niches.includes(n) ? 'bg-violet-500/25 text-violet-300 border border-violet-500/40' : 'bg-white/5 text-gray-400 border border-white/10 hover:border-white/20'
                }`}>
                {n}
              </button>
            ))}
          </div>
        </div>

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
          {loading ? 'Saving…' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}
