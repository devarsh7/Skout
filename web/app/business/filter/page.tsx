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

  const reset = () => {
    setFilters({
      platform: '', min_followers: '', max_followers: '', country: '',
      city: '', niches: [], min_engagement_rate: '', open_to_collabs: false,
    })
    setResults([])
    setSearched(false)
    setError('')
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSearched(true)
    try {
      // filterSearch() now does the field-name translation for us.
      const res = await filterSearch({
        platform: filters.platform || undefined,
        min_followers: filters.min_followers ? parseInt(filters.min_followers) : undefined,
        max_followers: filters.max_followers ? parseInt(filters.max_followers) : undefined,
        country: filters.country || undefined,
        city: filters.city || undefined,
        niches: filters.niches.length > 0 ? filters.niches : undefined,
        min_engagement_rate: filters.min_engagement_rate ? parseFloat(filters.min_engagement_rate) : undefined,
        open_to_collabs: filters.open_to_collabs || undefined,
      })
      setResults(res.creators)
    } catch {
      setError('Filter search failed. Make sure the API is running.')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-[#1E1B4B] mb-1">Filter & Refine</h1>
        <p className="text-[#6B7280] text-sm">Use structured filters to find exactly who you need.</p>
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
              <label className="label">Country (ISO-2)</label>
              <input className="input" placeholder="US, GB, IN…" value={filters.country} onChange={e => set('country', e.target.value)} />
            </div>

            <div>
              <label className="label">City</label>
              <input className="input" placeholder="New York, London…" value={filters.city} onChange={e => set('city', e.target.value)} />
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
                    className={`px-2.5 py-1 rounded-full text-xs font-semibold transition-colors ${
                      filters.niches.includes(n)
                        ? 'bg-[#EEF2FF] text-[#4F46E5] border border-[#C7D2FE]'
                        : 'bg-white text-[#6B7280] border border-[#E2E8F0] hover:border-[#C7D2FE]'
                    }`}>
                    {n}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="collab"
                checked={filters.open_to_collabs}
                onChange={e => set('open_to_collabs', e.target.checked)}
                className="w-4 h-4 accent-[#4F46E5]"
              />
              <label htmlFor="collab" className="text-[#6B7280] text-sm cursor-pointer">Open to collabs only</label>
            </div>

            <div className="flex gap-2">
              <button type="submit" className="btn-primary flex-1" disabled={loading}>
                {loading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Apply Filters'}
              </button>
              <button type="button" onClick={reset} className="btn-ghost px-4" disabled={loading}>
                Reset
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        <div className="md:col-span-2">
          {error && <div className="mb-4 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm">{error}</div>}

          {loading && (
            <div className="flex justify-center py-20">
              <Loader2 className="w-7 h-7 animate-spin text-[#4F46E5]" />
            </div>
          )}

          {!loading && searched && results.length === 0 && (
            <div className="text-center py-20 text-[#6B7280]">
              No creators match these filters. Try loosening them — especially follower minimum.
            </div>
          )}

          {!loading && results.length > 0 && (
            <div>
              <p className="text-[#6B7280] text-sm mb-4">
                <span className="text-[#1E1B4B] font-semibold">{results.length}</span> {results.length === 1 ? 'creator' : 'creators'} found
              </p>
              <div className="grid gap-4">
                {results.map(c => <CreatorCard key={c.id} creator={c} />)}
              </div>
            </div>
          )}

          {!searched && !loading && (
            <div className="card flex items-center justify-center h-60 text-[#9CA3AF] text-sm">
              Set your filters and click Apply Filters
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
