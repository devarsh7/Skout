'use client'

import { useState } from 'react'
import { filterSearch } from '@/lib/api'
import { Creator } from '@/types'
import CreatorCard from '@/components/creator/CreatorCard'
import { Loader2 } from 'lucide-react'

const PLATFORMS = ['Instagram', 'TikTok', 'YouTube', 'Twitter']
const NICHES = ['Fashion', 'Beauty', 'Fitness', 'Food', 'Travel', 'Tech', 'Gaming', 'Lifestyle', 'Business', 'Education']

export default function FilterPage() {
  const [results, setResults] = useState<Creator[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  const [filters, setFilters] = useState({
    platform: '',
    min_followers: '',
    max_followers: '',
    country: '',
    city: '',
    niches: [] as string[],
    min_engagement_rate: '',
    open_to_collabs: false,
  })

  const set = (k: keyof typeof filters, v: string | string[] | boolean) =>
    setFilters(prev => ({ ...prev, [k]: v }))

  const toggleNiche = (n: string) =>
    set('niches', filters.niches.includes(n) ? filters.niches.filter(x => x !== n) : [...filters.niches, n])

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSearched(true)
    try {
      const payload = {
        platform: filters.platform || undefined,
        min_followers: filters.min_followers ? parseInt(filters.min_followers) : undefined,
        max_followers: filters.max_followers ? parseInt(filters.max_followers) : undefined,
        country: filters.country || undefined,
        city: filters.city || undefined,
        niches: filters.niches.length > 0 ? filters.niches : undefined,
        min_engagement_rate: filters.min_engagement_rate ? parseFloat(filters.min_engagement_rate) : undefined,
        open_to_collabs: filters.open_to_collabs || undefined,
      }
      const res = await filterSearch(payload)
      setResults(res.creators || [])
    } catch {
      setError('Filter search failed. Make sure the API is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-1">Filter & Refine</h1>
        <p className="text-gray-500">Use structured filters to find exactly who you need.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Filters panel */}
        <div className="md:col-span-1">
          <form onSubmit={handleSearch} className="card p-6 space-y-5">
            <div>
              <label className="label">Platform</label>
              <select className="input" value={filters.platform} onChange={e => set('platform', e.target.value)}>
                <option value="">All platforms</option>
                {PLATFORMS.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>

            <div>
              <label className="label">Followers</label>
              <div className="grid grid-cols-2 gap-2">
                <input type="number" className="input" placeholder="Min" value={filters.min_followers} onChange={e => set('min_followers', e.target.value)} />
                <input type="number" className="input" placeholder="Max" value={filters.max_followers} onChange={e => set('max_followers', e.target.value)} />
              </div>
            </div>

            <div>
              <label className="label">Country</label>
              <input className="input" placeholder="US, UK, CA..." value={filters.country} onChange={e => set('country', e.target.value)} />
            </div>

            <div>
              <label className="label">City</label>
              <input className="input" placeholder="New York, London..." value={filters.city} onChange={e => set('city', e.target.value)} />
            </div>

            <div>
              <label className="label">Min Engagement Rate (%)</label>
              <input type="number" step="0.1" className="input" placeholder="2.0" value={filters.min_engagement_rate} onChange={e => set('min_engagement_rate', e.target.value)} />
            </div>

            <div>
              <label className="label mb-2 block">Niches</label>
              <div className="flex flex-wrap gap-1.5">
                {NICHES.map(n => (
                  <button key={n} type="button" onClick={() => toggleNiche(n)}
                    className={`px-2.5 py-1 rounded-full text-xs transition-colors ${
                      filters.niches.includes(n) ? 'bg-violet-500/25 text-violet-300 border border-violet-500/40' : 'bg-white/5 text-gray-400 border border-white/10'
                    }`}>
                    {n}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <input type="checkbox" id="collab" checked={filters.open_to_collabs} onChange={e => set('open_to_collabs', e.target.checked)} className="w-4 h-4 accent-violet-500" />
              <label htmlFor="collab" className="text-gray-400 text-sm cursor-pointer">Open to collabs only</label>
            </div>

            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Apply Filters'}
            </button>
          </form>
        </div>

        {/* Results */}
        <div className="md:col-span-2">
          {error && <div className="mb-4 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

          {loading && (
            <div className="flex justify-center py-20">
              <Loader2 className="w-7 h-7 animate-spin text-violet-500" />
            </div>
          )}

          {!loading && searched && results.length === 0 && (
            <div className="text-center py-20 text-gray-500">No creators match these filters.</div>
          )}

          {!loading && results.length > 0 && (
            <div>
              <p className="text-gray-400 text-sm mb-4">
                <span className="text-white font-semibold">{results.length}</span> creators found
              </p>
              <div className="grid gap-4">
                {results.map(c => <CreatorCard key={c.id} creator={c} />)}
              </div>
            </div>
          )}

          {!searched && !loading && (
            <div className="flex items-center justify-center h-60 text-gray-600 text-sm">
              Set your filters and click Apply
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
