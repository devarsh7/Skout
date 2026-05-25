export interface AuthUser {
  user_id: string
  username: string
  email: string
  role: 'creator' | 'business'
  is_verified: boolean
  token?: string
  creator_id?: string
  profile_meta?: Record<string, unknown>
}

export interface Creator {
  id: string
  full_name: string
  display_name?: string
  email?: string
  instagram_handle?: string
  tiktok_handle?: string
  youtube_channel?: string
  twitter_handle?: string
  website?: string
  instagram_followers: number
  tiktok_followers: number
  youtube_subscribers: number
  avg_engagement_rate: number
  avg_views: number
  bio?: string
  niches: string[]
  languages: string[]
  country: string
  city?: string
  audience_countries: string[]
  audience_age_range?: string
  min_rate_usd: number
  open_to_collabs: boolean
  preferred_collab_types: string[]
}

export interface DiscoveryResult {
  creators: Creator[]
  total: number
  query?: string
}

export interface FilterParams {
  platform?: string
  min_followers?: number
  max_followers?: number
  country?: string
  city?: string
  niches?: string[]
  languages?: string[]
  min_engagement_rate?: number
  open_to_collabs?: boolean
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export interface Campaign {
  id: string
  name: string
  status: string
  created_at: string
  filters?: Record<string, unknown>
}
