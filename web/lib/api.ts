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
    throw new APIError(res.status, err.detail || 'Request failed')
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

// ── Creators ──────────────────────────────────────────────────────────────────

export const listCreators = (limit = 50) =>
  req<Creator[]>('GET', `/creators?limit=${limit}`)

export const getCreator = (id: string) =>
  req<Creator>('GET', `/creators/${id}`)

export const updateCreator = (id: string, payload: Record<string, unknown>, token: string) =>
  req<Creator>('PATCH', `/creators/${id}`, { body: payload, token })

// ── Agents ────────────────────────────────────────────────────────────────────

export const discover = (query: string, topK = 20) =>
  req<{ creators: Creator[]; total: number }>('POST', '/agents/discovery', {
    body: { query, top_k: topK },
  })

export const filterSearch = (filters: FilterParams, query?: string, topK = 20) =>
  req<{ creators: Creator[]; total: number }>('POST', '/agents/filter', {
    body: { query, filters, top_k: topK },
  })

export const draftOutreach = (payload: Record<string, unknown>) =>
  req<{ draft: string }>('POST', '/agents/outreach', { body: payload })

// ── Agent Chat (Business) ─────────────────────────────────────────────────────

export const agentChat = (message: string, token: string) =>
  req<{ response: string; actions?: unknown[] }>('POST', '/agent/chat', {
    body: { message },
    token,
  })

export const agentHistory = (token: string) =>
  req<{ role: string; content: string }[]>('GET', '/agent/history', { token })

// ── Creator Agent ─────────────────────────────────────────────────────────────

export const creatorAgentChat = (message: string, token: string) =>
  req<{ response: string }>('POST', '/creator-agent/chat', { body: { message }, token })

export const creatorAgentHistory = (token: string) =>
  req<{ role: string; content: string }[]>('GET', '/creator-agent/history', { token })

// ── Local Market ──────────────────────────────────────────────────────────────

export const localLeaderboard = (city: string, category: string, limit = 10) =>
  req<Creator[]>('GET', `/local/leaderboard?city=${city}&category=${category}&limit=${limit}`)

export const localBenchmarks = (city: string, category: string) =>
  req<Record<string, unknown>>('GET', `/local/benchmarks?city=${city}&category=${category}`)

export const localCities = () =>
  req<{ city: string; country: string }[]>('GET', '/local/cities')

export const health = () =>
  req<{ status: string }>('GET', '/health')
