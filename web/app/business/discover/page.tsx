'use client'

import { useState } from 'react'
import { discover } from '@/lib/api'
import { Creator } from '@/types'
import CreatorCard from '@/components/creator/CreatorCard'
import { Search, Loader2 } from 'lucide-react'

export default function DiscoverPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Creator[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError('')
    setSearched(true)
    try {
      const res = await discover(query.trim(), 20)
      setResults(res.creators || [])
    } catch {
      setError('Search failed. Make sure the API is running.')
    } finally {
      setLoading(false)
    }
  }

  const examples = [
    'Vegan fitness micro-influencers in Los Angeles',
    'Tech reviewers with 50K-500K followers',
    'Beauty creators who work with sustainable brands',
    'Food bloggers in New York with high engagement',
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Discover Creators</h1>
        <p className="text-gray-500">Describe who you're looking for in plain English.</p>
      </div>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              className="input pl-12 py-4 text-base"
              placeholder="e.g. fashion micro-influencers in London with high engagement..."
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
          <button type="submit" className="btn-primary px-8" disabled={loading || !query.trim()}>
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Search'}
          </button>
        </div>
      </form>

      {!searched && (
        <div className="mb-8">
          <p className="text-gray-500 text-sm mb-3">Try these examples:</p>
          <div className="flex flex-wrap gap-2">
            {examples.map(ex => (
              <button
                key={ex}
                onClick={() => setQuery(ex)}
                className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-gray-400 text-xs hover:text-white hover:border-white/20 transition-colors"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-violet-500 mx-auto mb-3" />
            <p className="text-gray-500 text-sm">AI is searching for the best matches…</p>
          </div>
        </div>
      )}

      {!loading && searched && results.length === 0 && (
        <div className="text-center py-20">
          <p className="text-gray-500">No creators found for this query. Try a different description.</p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-5">
            <p className="text-gray-400 text-sm">
              Found <span className="text-white font-semibold">{results.length}</span> creators
            </p>
          </div>
          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
            {results.map(c => (
              <CreatorCard key={c.id} creator={c} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
