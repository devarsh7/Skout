import { Creator } from '@/types'
import { MapPin, TrendingUp, Users } from 'lucide-react'

function fmt(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`
  return String(n)
}

interface Props {
  creator: Creator
  score?: number
  onSelect?: (creator: Creator) => void
}

export default function CreatorCard({ creator, score, onSelect }: Props) {
  const totalFollowers =
    (creator.instagram_followers || 0) +
    (creator.tiktok_followers || 0) +
    (creator.youtube_subscribers || 0)

  const platforms = [
    creator.instagram_handle && 'Instagram',
    creator.tiktok_handle && 'TikTok',
    creator.youtube_channel && 'YouTube',
    creator.twitter_handle && 'Twitter',
  ].filter(Boolean)

  return (
    <div
      className="card p-5 hover:border-[#C7D2FE] hover:shadow-md transition-all cursor-pointer"
      onClick={() => onSelect?.(creator)}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-full flex items-center justify-center border border-[#E0E7FF] flex-shrink-0 text-white font-semibold text-sm"
            style={{ background: 'linear-gradient(135deg,#4F46E5,#7C3AED)' }}>
            {(creator.display_name || creator.full_name).charAt(0).toUpperCase()}
          </div>
          <div>
            <div className="text-[#1E1B4B] font-bold text-sm leading-tight">
              {creator.display_name || creator.full_name}
            </div>
            {creator.instagram_handle && (
              <div className="text-[#9CA3AF] text-xs mt-0.5">@{creator.instagram_handle}</div>
            )}
          </div>
        </div>
        {score !== undefined && (
          <div className="badge text-xs">
            {Math.round(score * 100)}% match
          </div>
        )}
      </div>

      {creator.bio && (
        <p className="text-[#6B7280] text-xs leading-relaxed mb-3 line-clamp-2">{creator.bio}</p>
      )}

      <div className="flex items-center gap-4 mb-3 text-xs text-[#6B7280]">
        <div className="flex items-center gap-1">
          <Users className="w-3.5 h-3.5" />
          <span>{fmt(totalFollowers)}</span>
        </div>
        {creator.avg_engagement_rate > 0 && (
          <div className="flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>{creator.avg_engagement_rate.toFixed(1)}%</span>
          </div>
        )}
        {creator.city && (
          <div className="flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5" />
            <span>{creator.city}, {creator.country}</span>
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-1.5">
        {creator.niches.slice(0, 3).map(n => (
          <span key={n} className="px-2 py-0.5 rounded-full bg-[#F3F4FF] text-[#4F46E5] text-[11px] font-medium border border-[#E0E7FF]">
            {n}
          </span>
        ))}
        {platforms.slice(0, 2).map(p => (
          <span key={p} className="px-2 py-0.5 rounded-full bg-[#EEF2FF] text-[#6B7280] text-[11px] border border-[#E0E7FF]">
            {p}
          </span>
        ))}
      </div>

      {creator.min_rate_usd > 0 && (
        <div className="mt-3 pt-3 border-t border-[#E2E8F0] text-xs text-[#9CA3AF]">
          From <span className="text-[#1E1B4B] font-semibold">${creator.min_rate_usd.toLocaleString()}</span> / collab
        </div>
      )}
    </div>
  )
}
