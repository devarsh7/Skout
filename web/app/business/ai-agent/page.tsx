'use client'

import { useState, useEffect, useRef } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { agentChat, agentHistory } from '@/lib/api'
import { Send, Bot, Loader2 } from 'lucide-react'

interface Message { role: 'user' | 'assistant'; content: string }

const starters = [
  'Find vegan beauty creators with 50K-200K followers in the US',
  'Draft an outreach email for a fitness brand campaign',
  'Show me top creators in the food & lifestyle niche in NYC',
  'What creators would work for a sustainable fashion brand?',
]

export default function AIAgentPage() {
  const { token } = useAuth()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!token) return
    agentHistory(token)
      .then(h => setMessages(h as Message[]))
      .catch(() => {})
      .finally(() => setLoadingHistory(false))
  }, [token])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async () => {
    if (!input.trim() || !token || loading) return
    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)
    try {
      const res = await agentChat(userMsg, token)
      setMessages(prev => [...prev, { role: 'assistant', content: res.response }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Something went wrong. Please try again.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-violet-500/15 border border-violet-500/20 flex items-center justify-center">
            <Bot className="w-5 h-5 text-violet-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">AI Campaign Agent</h1>
            <p className="text-gray-500 text-sm">Discover, filter, and draft outreach in one conversation</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
        {loadingHistory ? (
          <div className="flex justify-center py-10">
            <Loader2 className="w-6 h-6 animate-spin text-violet-500" />
          </div>
        ) : messages.length === 0 ? (
          <div className="py-8">
            <p className="text-gray-500 text-sm mb-4 text-center">Describe your campaign — the AI handles the rest.</p>
            <div className="grid grid-cols-2 gap-3">
              {starters.map(s => (
                <button key={s} onClick={() => setInput(s)} className="card p-4 text-left text-sm text-gray-400 hover:text-white hover:border-violet-500/30 transition-all">
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {m.role === 'assistant' && (
                <div className="w-7 h-7 rounded-lg bg-violet-500/20 border border-violet-500/20 flex items-center justify-center mr-2 mt-1 flex-shrink-0">
                  <Bot className="w-3.5 h-3.5 text-violet-400" />
                </div>
              )}
              <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                m.role === 'user'
                  ? 'bg-violet-600 text-white rounded-br-sm'
                  : 'bg-[#13131A] border border-white/[0.08] text-gray-200 rounded-bl-sm'
              }`}>
                {m.content}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex items-start gap-2">
            <div className="w-7 h-7 rounded-lg bg-violet-500/20 border border-violet-500/20 flex items-center justify-center flex-shrink-0">
              <Bot className="w-3.5 h-3.5 text-violet-400" />
            </div>
            <div className="card px-4 py-3">
              <div className="flex gap-1.5">
                {[0, 1, 2].map(i => (
                  <div key={i} className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-3">
        <input
          type="text"
          className="input flex-1"
          placeholder="Describe your campaign or ask anything…"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          disabled={loading}
        />
        <button onClick={send} disabled={loading || !input.trim()} className="btn-primary px-5">
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
