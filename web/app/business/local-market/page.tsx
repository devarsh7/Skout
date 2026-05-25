'use client'

import { useState, useEffect } from 'react'
import { localLeaderboard, localCities } from '@/lib/api'
import { Creator } from '@/types'
import CreatorCard from '@/components/creator/CreatorCard'
import { MapPin, Loader2 } from 'lucide-react'

const CATEGORIES = ['food', 'fashion', 'beauty', 'fitness', 'tech', 'lifestyle']

export default function LocalMarketPage() {
  const [cities, setCities] = useState<{ city: string; country: string }[]>([])
  const [selectedCity, setSelectedCity] = useState('')
  const [category, setCategory] = useState('food')
  const [results, setResults] = useState<Creator[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    localCities().then(setCities).catch(() => {})
  }, [])

  const handleSearch = async () => {
    if (!selectedCity) return
    setLoading(true)
    try {
      const res = await localLeaderboard(selectedCity, category)
      setResults(res)
    } catch {
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Local Market</h1>
        <p className="text-gray-500">Discover top creators in specific cities and categories.</p>
      </div>

      <div className="card p-5 mb-6 flex flex-wrap gap-4 items-end">
        <div className="flex-1 min-w-40">
          <label className="label">City</label>
          <select className="input" value={selectedCity} onChange={e => setSelectedCity(e.target.value)}>
            <option value="">Select a city</option>
            {cities.map(c => <option key={c.city} value={c.city}>{c.city}, {c.country}</option>)}
          </select>
        </div>
        <div className="flex-1 min-w-40">
          <label className="label">Category</label>
          <select className="input" value={category} onChange={e => setCategory(e.target.value)}>
            {CATEGORIES.map(c => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
          </select>
        </div>
        <button onClick={handleSearch} className="btn-primary" disabled={loading || !selectedCity}>
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <MapPin className="w-4 h-4" />}
          <span className="ml-2">Show Leaderboard</span>
        </button>
      </div>

      {results.length > 0 && (
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
          {results.map(c => <CreatorCard key={c.id} creator={c} />)}
        </div>
      )}

      {!loading && results.length === 0 && selectedCity && (
        <div className="text-center py-16 text-gray-500">No creators found for this city and category.</div>
      )}
    </div>
  )
}
