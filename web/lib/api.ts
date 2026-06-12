import { AuthUser, Creator, FilterParams } from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message)
  }
}

async function req<T>(method: string, path: string, options: {
  body?: unknown
  token?: string
} = {}): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (options.token) headers['Authorization'] = `Bearer ${options.token}`

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    // FastAPI validation errors return detail as an array of objects
    const detail = typeof err.detail === 'string'
      ? err.detail
      : Array.isArray(err.detail)
        ? err.detail.map((d: { msg?: string }) => d.msg || JSON.stringify(d)).join('; ')
        : JSON.stringify(err.detail ?? 'Request failed')
    throw new APIError(res.status, detail)
  }

  if (res.status === 204 || res.headers.get('content-length') === '0') {
    return null as T
  }

  return res.json()
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export const sendOTP = (email: string, name = '') =>
  req<{ message: string; dev_otp?: string }>('POST', '/auth/send-otp', { body: { email, name } })

export const registerCreator = (payload: Record<string, unknown>) =>
  req<AuthUser>('POST', '/auth/register-creator', { body: payload })

export const registerBusiness = (payload: Record<string, unknown>) =>
  req<AuthUser>('POST', '/auth/register-business', { body: payload })

export const login = (email: string, password: string) =>
  req<AuthUser>('POST', '/auth/login', { body: { email, password } })

export const getMe = (token: string) =>
  req<AuthUser>('GET', '/auth/me', { token })

export const updateMe = (payload: Record<string, unknown>, token: string) =>
  req<AuthUser>('PATCH', '/auth/me', { body: payload, token })

// ── Instagram OAuth ───────────────────────────────────────────────────────────

export interface InstagramProfile {
  found: boolean
  username?: string
  full_name?: string
  bio?: string
  followers?: number
  media_count?: number
  website?: string
}

export interface InstagramReel {
  id: string
  caption: string
  timestamp: string
  likes: number
  comments: number
  video_views: number
  reach: number
  thumbnail?: string
  permalink?: string
}

/** Start OAuth. Pass userId for logged-in connect; omit during onboarding. */
export const getInstagramAuthUrl = (userId?: string) =>
  req<{ url: string; state: string }>(
    'GET',
    `/instagram/auth-url${userId ? `?user_id=${encodeURIComponent(userId)}` : ''}`
  )

/** One-time pickup of profile + reels after onboarding OAuth redirect. */
export const getInstagramOauthData = (state: string) =>
  req<{ profile: InstagramProfile; reels: InstagramReel[]; token: string }>(
    'GET',
    `/instagram/data/${encodeURIComponent(state)}`
  )

// ── Creators ──────────────────────────────────────────────────────────────────

export const listCreators = (limit = 50) =>
  req<Creator[]>('GET', `/creators?limit=${limit}`)

export const getCreator = (id: string) =>
  req<Creator>('GET', `/creators/${id}`)

export const updateCreator = (id: string, payload: Record<string, unknown>, token: string) =>
  req<Creator>('PATCH', `/creators/${id}`, { body: payload, token })

// ── Agents ────────────────────────────────────────────────────────────────────

// Backend AgentResponse shape: { agent, total, results: [{ score, reason, creator }], explanation }
interface BackendAgentResponse {
  agent: string
  total: number
  results: { score: number; reason?: string | null; creator: Creator }[]
  explanation?: string | null
}

function unwrap(res: BackendAgentResponse): { creators: Creator[]; total: number; explanation?: string | null } {
  return {
    creators: (res.results || []).map(h => h.creator),
    total: res.total ?? (res.results?.length || 0),
    explanation: res.explanation,
  }
}

export const discover = async (query: string, topK = 20) => {
  const res = await req<BackendAgentResponse>('POST', '/agents/discovery', {
    body: { query, top_k: topK },
  })
  return unwrap(res)
}

/**
 * Translate the UI's flat filter form into the backend Filters schema shape:
 *  - platform → platforms[]
 *  - country  → countries[]
 *  - city     → cities[]
 *  - min/max_followers → min/max_total_followers
 *  - open_to_collabs → open_to_collabs_only
 *  Empty/zero values are dropped so backend defaults don't over-filter.
 */
export const filterSearch = async (ui: FilterParams, query?: string, topK = 20) => {
  const filters: Record<string, unknown> = {
    platforms: ui.platform ? [ui.platform.toLowerCase()] : [],
    niches: ui.niches?.length ? ui.niches.map(n => n.toLowerCase()) : [],
    languages: ui.languages?.length ? ui.languages : [],
    countries: ui.country ? [ui.country.toUpperCase()] : [],
    cities: ui.city ? [ui.city] : [],
    min_total_followers: ui.min_followers ?? 0,
    max_total_followers: ui.max_followers ?? null,
    min_engagement_rate: ui.min_engagement_rate ?? 0,
    open_to_collabs_only: ui.open_to_collabs ?? false,
  }
  const res = await req<BackendAgentResponse>('POST', '/agents/filter', {
    body: { query: query || null, filters, top_k: topK },
  })
  return unwrap(res)
}

export const draftOutreach = (payload: Record<string, unknown>) =>
  req<{ draft: string }>('POST', '/agents/outreach', { body: payload })

// ── Agent Chat (Business) ─────────────────────────────────────────────────────

export interface AgentToolStep {
  name: string
  args?: Record<string, unknown>
  label: string
  result_summary: string
}

export interface AgentActionData {
  type?: 'creator_list' | 'brief' | 'outreach'
  creators?: { id: string; name: string }[]
  brief_text?: string
  creator_id?: string
  creator_name?: string
  actions?: string[]
  tool_trace?: AgentToolStep[]
}

export interface AgentTurn {
  id?: string
  role: 'user' | 'assistant'
  content: string
  intent?: string | null
  action_data?: AgentActionData | null
  timestamp?: string
  // Legacy keys the backend may still emit
  response?: string
}

export const agentChat = (message: string, token: string) =>
  req<AgentTurn>('POST', '/agent/chat', {
    body: { message },
    token,
  })

export const agentHistory = (token: string) =>
  req<AgentTurn[]>('GET', '/agent/history', { token })

// ── Creator Agent ─────────────────────────────────────────────────────────────

export const creatorAgentChat = (message: string, token: string) =>
  req<{ response: string }>('POST', '/creator-agent/chat', { body: { message }, token })

export const creatorAgentHistory = (token: string) =>
  req<{ role: string; content: string }[]>('GET', '/creator-agent/history', { token })

// ── Rate Calculator ───────────────────────────────────────────────────────────

export interface RateCalcInputs {
  platform: string          // 'instagram' | 'tiktok' | 'youtube'
  deliverable: string       // 'reel' | 'carousel' | 'static' | 'story' | 'bundle' | 'video' | 'integration' | 'dedicated' | 'short'
  quantity: number
  usage: string             // 'organic' | 'paid_30d' | 'paid_60d' | 'reuse_brand' | 'full_rights'
  exclusivity: string       // 'none' | '30d' | '60d' | '90d' | '180d'
  add_story_bundle: boolean
}

export interface RateCalcResult {
  quoted_usd: number
  currency: string
  followers_used: number
  platform: string
  deliverable: string
  quantity: number
  engagement_pct: number
  breakdown: {
    base_cpm: number
    base_unit_usd: number
    engagement_multiplier: number
    city_multiplier: number
    niche_multiplier: number
    usage_multiplier: number
    exclusivity_multiplier: number
    per_deliverable_usd: number
    subtotal_usd: number
    total_before_rounding: number
  }
  inputs: RateCalcInputs
  market_range: {
    city: string
    niche: string
    creator_count: number
    low: number
    high: number
  } | null
  explanation: string
  quote_text: string
}

export const creatorAgentCalculateRate = (inputs: RateCalcInputs, token: string) =>
  req<RateCalcResult>('POST', '/creator-agent/calculate-rate', { body: inputs, token })

// ── Brief Evaluator ───────────────────────────────────────────────────────────

export interface BriefEvalResult {
  extracted: {
    brand_name: string | null
    deliverables: string
    offered_usd: number | null
    usage: string
    exclusivity: string
    timeline: string
    platform: string
    key_clauses: string[]
  }
  red_flags: { label: string; advice: string }[]
  pay_analysis: {
    fair_rate_usd: number
    offered_usd: number | null
    ratio?: number
    verdict: 'fair' | 'below' | 'lowball' | 'no_offer' | string
    headline: string
  }
  counter_draft: string
  rate_basis: RateCalcResult
}

export const creatorAgentEvaluateBrief = (briefText: string, token: string) =>
  req<BriefEvalResult>('POST', '/creator-agent/evaluate-brief', {
    body: { brief_text: briefText },
    token,
  })

// ── Brand-fact memory ─────────────────────────────────────────────────────────

export interface BrandFact {
  id: string
  smb_id: string
  fact: string
  category: string         // budget | preference | constraint | context | goal | outcome | other
  confidence: number       // 0.0 - 1.0
  source: string           // chat | manual | onboarding
  created_at: string
  updated_at: string
}

export const listBrandFacts = (token: string) =>
  req<{ facts: BrandFact[] }>('GET', '/agent/facts', { token })

export const addBrandFact = (fact: string, category: string, token: string) =>
  req<BrandFact>('POST', '/agent/facts', { body: { fact, category }, token })

export const deleteBrandFact = (factId: string, token: string) =>
  req<{ deleted: boolean }>('DELETE', `/agent/facts/${factId}`, { token })

// ── Creator voice profile ─────────────────────────────────────────────────────

export const creatorAgentGetVoice = (token: string) =>
  req<{ voice_description: string }>('GET', '/creator-agent/voice', { token })

export const creatorAgentRefreshVoice = (samples: string[] | null, token: string) =>
  req<{ voice_description: string }>('POST', '/creator-agent/voice/refresh', {
    body: { samples },
    token,
  })

// ── Local Market ──────────────────────────────────────────────────────────────

export const localLeaderboard = (city: string, category: string, limit = 10) =>
  req<Creator[]>('GET', `/local/leaderboard?city=${city}&category=${category}&limit=${limit}`)

export const localBenchmarks = (city: string, category: string) =>
  req<Record<string, unknown>>('GET', `/local/benchmarks?city=${city}&category=${category}`)

export const localCities = () =>
  req<{ city: string; country: string }[]>('GET', '/local/cities')

export const health = () =>
  req<{ status: string }>('GET', '/health')
