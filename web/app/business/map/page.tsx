'use client'

import { useState, useEffect } from 'react'
import { listCreators } from '@/lib/api'
import { Creator } from '@/types'
import { MapPin, Loader2 } from 'lucide-react'

function fmt(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`
  return String(n)
}

export default function CreatorMapPage() {
  const [creators, setCreators] = useState<Creator[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<Creator | null>(null)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    listCreators(100).then(setCreators).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const cities = Array.from(new Set(creators.filter(c => c.city).map(c => c.city!)))
  const filtered = filter ? creators.filter(c => c.city === filter) : creators

  return (
    <div>
      <div className="mb-6 flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#1E1B4B] mb-1">Creator Map</h1>
          <p className="text-[#6B7280] text-sm">Browse creators by location.</p>
        </div>
        <select
          className="input max-w-xs"
          value={filter}
          onChange={e => { setFilter(e.target.value); setSelected(null) }}
        >
          <option value="">All Cities</option>
          {cities.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="w-7 h-7 animate-spin text-[#4F46E5]" />
        </div>
      ) : (
        <div className="grid md:grid-cols-3 gap-4">
          {/* City grouping */}
          {cities.filter(c => !filter || c === filter).map(city => {
            const cityCreators = filtered.filter(c => c.city === city)
            if (cityCreators.length === 0) return null
            return (
              <div key={city} className="card p-5">
                <div className="flex items-center gap-2 mb-4">
                  <MapPin className="w-4 h-4 text-[#4F46E5]" />
                  <h3 className="font-bold text-[#1E1B4B]">{city}</h3>
                  <span className="badge ml-auto">{cityCreators.length}</span>
                </div>
                <div className="space-y-3">
                  {cityCreators.map(c => {
                    const total = (c.instagram_followers || 0) + (c.tiktok_followers || 0) + (c.youtube_subscribers || 0)
                    return (
                      <button
                        key={c.id}
                        onClick={() => setSelected(selected?.id === c.id ? null : c)}
                        className="w-full text-left p-3 rounded-xl border border-[#E2E8F0] hover:border-[#C7D2FE] hover:bg-[#EEF2FF] transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
                            style={{ background: 'linear-gradient(135deg,#4F46E5,#7C3AED)' }}>
                            {(c.display_name || c.full_name).charAt(0).toUpperCase()}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="font-semibold text-sm text-[#1E1B4B] truncate">{c.display_name || c.full_name}</div>
                            <div className="text-xs text-[#6B7280]">{fmt(total)} followers</div>
                          </div>
                        </div>
                        {selected?.id === c.id && (
                          <div className="mt-3 pt-3 border-t border-[#E2E8F0] space-y-1">
                            {c.instagram_handle && <div className="text-xs text-[#6B7280]">📸 @{c.instagram_handle} — {fmt(c.instagram_followers)}</div>}
                            {c.tiktok_handle && <div className="text-xs text-[#6B7280]">🎵 @{c.tiktok_handle} — {fmt(c.tiktok_followers)}</div>}
                            {c.avg_engagement_rate > 0 && <div className="text-xs text-[#6B7280]">📈 {c.avg_engagement_rate.toFixed(1)}% engagement</div>}
                            {c.niches.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-1">
                                {c.niches.slice(0, 3).map(n => (
                                  <span key={n} className="badge text-[10px] py-0.5">{n}</span>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </button>
                    )
                  })}
                </div>
              </div>
            )
          })}

          {filtered.filter(c => !c.city).length > 0 && (
            <div className="card p-5">
              <div className="flex items-center gap-2 mb-4">
                <MapPin className="w-4 h-4 text-[#9CA3AF]" />
                <h3 className="font-bold text-[#1E1B4B]">Location not set</h3>
                <span className="badge ml-auto">{filtered.filter(c => !c.city).length}</span>
              </div>
              <div className="space-y-2">
                {filtered.filter(c => !c.city).map(c => (
                  <div key={c.id} className="flex items-center gap-2 p-2 rounded-lg">
                    <div className="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold"
                      style={{ background: 'linear-gradient(135deg,#9CA3AF,#6B7280)' }}>
                      {(c.display_name || c.full_name).charAt(0).toUpperCase()}
                    </div>
                    <span className="text-sm text-[#6B7280] truncate">{c.display_name || c.full_name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
