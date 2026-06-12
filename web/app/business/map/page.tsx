'use client'

import { useState, useEffect, useMemo } from 'react'
import dynamic from 'next/dynamic'
import { listCreators } from '@/lib/api'
import { Creator } from '@/types'
import { MapPin, Loader2, Globe, X, Filter, Users } from 'lucide-react'

// Leaflet touches `window` on import → SSR-disable the map component.
const MapView = dynamic(() => import('@/components/MapView'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-[580px] bg-[#EEF2FF] rounded-2xl">
      <Loader2 className="w-7 h-7 animate-spin text-[#4F46E5]" />
    </div>
  ),
})

function fmt(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`
  return String(n)
}

// Cities whose coordinates MapView knows about — kept in sync with components/MapView.tsx.
// Toronto first since that's our primary market.
const MAPPED_CITIES = new Set<string>([
  // Primary market
  'Toronto',
  // Other Canadian cities
  'Vancouver', 'Montreal', 'Calgary', 'Ottawa',
  // International markets
  'New York', 'Los Angeles', 'Chicago', 'London',
  'Singapore', 'Dubai', 'Sydney', 'Melbourne', 'Berlin', 'Paris', 'Tokyo',
  // Legacy (kept so historical creator rows still resolve)
  'Mumbai', 'Delhi', 'New Delhi', 'Bangalore', 'Bengaluru',
  'Hyderabad', 'Chennai', 'Kolkata', 'Pune',
])

const FOLLOWER_BUCKETS = [
  { label: 'Any reach',        min: 0,       max: Infinity },
  { label: 'Nano (<10K)',      min: 0,       max: 10_000 },
  { label: 'Micro (10K–50K)',  min: 10_000,  max: 50_000 },
  { label: 'Mid (50K–500K)',   min: 50_000,  max: 500_000 },
  { label: 'Macro (500K+)',    min: 500_000, max: Infinity },
]

export default function CreatorMapPage() {
  const [creators, setCreators] = useState<Creator[]>([])
  const [loading, setLoading] = useState(true)

  // Filters
  const [cityFilter, setCityFilter] = useState<string>('')           // single-select pill
  const [nicheFilters, setNicheFilters] = useState<Set<string>>(new Set())
  const [followerBucket, setFollowerBucket] = useState<number>(0)    // index into FOLLOWER_BUCKETS
  const [collabsOnly, setCollabsOnly] = useState(false)

  useEffect(() => {
    listCreators(500).then(setCreators).catch(() => {}).finally(() => setLoading(false))
  }, [])

  // Derive city list (with counts) from creators that actually have a city we can pin
  const cityOptions = useMemo(() => {
    const m = new Map<string, number>()
    for (const c of creators) {
      if (c.city && MAPPED_CITIES.has(c.city)) {
        m.set(c.city, (m.get(c.city) || 0) + 1)
      }
    }
    return Array.from(m.entries())
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      .map(([city, count]) => ({ city, count }))
  }, [creators])

  const nicheOptions = useMemo(() => {
    const m = new Map<string, number>()
    for (const c of creators) {
      for (const n of c.niches || []) m.set(n, (m.get(n) || 0) + 1)
    }
    return Array.from(m.entries())
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      .map(([niche, count]) => ({ niche, count }))
  }, [creators])

  // Apply filters → creators shown on the map
  const filtered = useMemo(() => {
    const bucket = FOLLOWER_BUCKETS[followerBucket]
    return creators.filter(c => {
      const total = (c.instagram_followers || 0) + (c.tiktok_followers || 0) + (c.youtube_subscribers || 0)
      if (cityFilter && c.city !== cityFilter) return false
      if (nicheFilters.size > 0 && !(c.niches || []).some(n => nicheFilters.has(n))) return false
      if (total < bucket.min || total > bucket.max) return false
      if (collabsOnly && !c.open_to_collabs) return false
      return true
    })
  }, [creators, cityFilter, nicheFilters, followerBucket, collabsOnly])

  // Only creators with mappable coordinates render as pins
  const onMap = filtered.filter(c => c.city && MAPPED_CITIES.has(c.city))
  const offMap = filtered.filter(c => !c.city || !MAPPED_CITIES.has(c.city))

  const activeFilterCount =
    (cityFilter ? 1 : 0) + nicheFilters.size + (followerBucket > 0 ? 1 : 0) + (collabsOnly ? 1 : 0)

  const clearAll = () => {
    setCityFilter('')
    setNicheFilters(new Set())
    setFollowerBucket(0)
    setCollabsOnly(false)
  }

  const toggleNiche = (n: string) => {
    const next = new Set(nicheFilters)
    next.has(n) ? next.delete(n) : next.add(n)
    setNicheFilters(next)
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#1E1B4B] mb-1">Creator Map</h1>
          <p className="text-[#6B7280] text-sm">
            Every Skout creator on the map. Filter by city, niche, and reach.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="badge">
            <Users className="w-3 h-3" />
            {onMap.length} on map
          </span>
          <span className="badge">
            <Globe className="w-3 h-3" />
            {cityOptions.length} {cityOptions.length === 1 ? 'city' : 'cities'}
          </span>
        </div>
      </div>

      {/* Filter strip */}
      {!loading && creators.length > 0 && (
        <div className="card p-4 mb-5 space-y-3">
          {/* Row 1: Cities */}
          {cityOptions.length > 0 && (
            <div className="flex items-start gap-3 flex-wrap">
              <span className="text-[11px] font-bold uppercase tracking-widest text-[#9CA3AF] pt-1.5 shrink-0">City</span>
              <div className="flex items-center gap-2 flex-wrap flex-1">
                {cityOptions.map(({ city, count }) => {
                  const active = cityFilter === city
                  return (
                    <button
                      key={city}
                      onClick={() => setCityFilter(active ? '' : city)}
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                        active
                          ? 'bg-[#4F46E5] text-white border border-[#4F46E5]'
                          : 'bg-white text-[#1E1B4B] border border-[#E2E8F0] hover:border-[#C7D2FE]'
                      }`}
                    >
                      <MapPin className="w-3 h-3" />
                      {city}
                      <span className={active ? 'text-white/70' : 'text-[#9CA3AF]'}>· {count}</span>
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {/* Row 2: Niches */}
          {nicheOptions.length > 0 && (
            <div className="flex items-start gap-3 flex-wrap pt-2 border-t border-[#F1F5F9]">
              <span className="text-[11px] font-bold uppercase tracking-widest text-[#9CA3AF] pt-1.5 shrink-0">Niche</span>
              <div className="flex items-center gap-2 flex-wrap flex-1">
                {nicheOptions.map(({ niche, count }) => {
                  const active = nicheFilters.has(niche)
                  return (
                    <button
                      key={niche}
                      onClick={() => toggleNiche(niche)}
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold transition-colors capitalize ${
                        active
                          ? 'bg-[#7C3AED] text-white border border-[#7C3AED]'
                          : 'bg-white text-[#1E1B4B] border border-[#E2E8F0] hover:border-[#DDD6FE]'
                      }`}
                    >
                      {niche}
                      <span className={active ? 'text-white/70' : 'text-[#9CA3AF]'}>· {count}</span>
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {/* Row 3: Reach + collabs + clear */}
          <div className="flex items-center gap-3 flex-wrap pt-2 border-t border-[#F1F5F9]">
            <span className="text-[11px] font-bold uppercase tracking-widest text-[#9CA3AF] shrink-0">Reach</span>
            <div className="flex items-center gap-2 flex-wrap">
              {FOLLOWER_BUCKETS.map((b, i) => {
                const active = followerBucket === i
                return (
                  <button
                    key={b.label}
                    onClick={() => setFollowerBucket(i)}
                    className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                      active
                        ? 'bg-[#1E1B4B] text-white border border-[#1E1B4B]'
                        : 'bg-white text-[#1E1B4B] border border-[#E2E8F0] hover:border-[#C7D2FE]'
                    }`}
                  >
                    {b.label}
                  </button>
                )
              })}
            </div>

            <label className="inline-flex items-center gap-2 text-xs font-semibold text-[#1E1B4B] cursor-pointer ml-auto">
              <input
                type="checkbox"
                checked={collabsOnly}
                onChange={e => setCollabsOnly(e.target.checked)}
                className="w-4 h-4 rounded border-[#C7D2FE] text-[#4F46E5]"
              />
              Open to collabs only
            </label>

            {activeFilterCount > 0 && (
              <button
                onClick={clearAll}
                className="inline-flex items-center gap-1 text-xs font-semibold text-[#6B7280] hover:text-[#4F46E5]"
              >
                <X className="w-3 h-3" /> Clear {activeFilterCount} filter{activeFilterCount === 1 ? '' : 's'}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Map / states */}
      {loading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="w-7 h-7 animate-spin text-[#4F46E5]" />
        </div>
      ) : creators.length === 0 ? (
        <div className="card p-10 text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full mb-3" style={{ background: 'linear-gradient(135deg,#EEF2FF,#F3F0FF)' }}>
            <MapPin className="w-6 h-6 text-[#4F46E5]" />
          </div>
          <div className="text-[#1E1B4B] font-bold text-lg mb-1">No creators on the map yet</div>
          <p className="text-[#6B7280] text-sm max-w-sm mx-auto">
            Run <code className="px-1.5 py-0.5 rounded bg-[#EEF2FF] text-[#4F46E5] text-xs">python scripts/seed_demo_creators.py</code> to populate the directory, or invite creators to onboard.
          </p>
        </div>
      ) : (
        <>
          <div className="card p-0 overflow-hidden" style={{ height: 580 }}>
            <MapView creators={onMap} />
          </div>

          {/* Sub-line: counts + filtered list overflow */}
          <div className="flex items-center justify-between flex-wrap gap-2 mt-3 text-xs text-[#6B7280]">
            <span>
              Showing <span className="text-[#1E1B4B] font-semibold">{onMap.length}</span> of {creators.length} creators
              {activeFilterCount > 0 && <span> · {activeFilterCount} active filter{activeFilterCount === 1 ? '' : 's'}</span>}
            </span>
            {offMap.length > 0 && (
              <span className="inline-flex items-center gap-1">
                <Filter className="w-3 h-3" />
                {offMap.length} creator{offMap.length === 1 ? '' : 's'} not pinnable (no mapped city)
              </span>
            )}
          </div>

          {/* Empty filter state */}
          {onMap.length === 0 && (
            <div className="card p-8 mt-5 text-center">
              <div className="text-[#1E1B4B] font-bold mb-1">No creators match these filters</div>
              <p className="text-[#6B7280] text-sm mb-4">Try widening the reach, clearing a niche, or picking a different city.</p>
              <button
                onClick={clearAll}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-bold text-white"
                style={{ background: 'linear-gradient(135deg,#4F46E5,#7C3AED)' }}
              >
                <X className="w-3.5 h-3.5" /> Clear filters
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
