'use client'

import { useEffect, useRef, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { agentChat, agentHistory, AgentToolStep, AgentTurn } from '@/lib/api'
import { Send, Bot, Loader2, Sparkles, Wrench } from 'lucide-react'
import BrandMemoryPanel from '@/components/business/BrandMemoryPanel'
import ToolTrace from '@/components/business/ToolTrace'

interface Message {
  role: 'user' | 'assistant'
  content: string
  tool_trace?: AgentToolStep[]
}

// Toronto-flavoured starters — local-business voice.
const STARTERS = [
  'Find 3 micro food creators in Toronto under 30K followers for a Queen West cafe.',
  'My Liberty Village pilates studio wants to launch May 15 — who should I reach out to?',
  'Draft an outreach email to a Yorkville lifestyle creator for a new boutique.',
  'Pricing range for a Kensington Market bookstore — 1 reel + 2 stories?',
]

// Live "thinking" hints to keep the UX feeling alive while the tool loop runs.
const THINKING_PHRASES = [
  'Reading your brand memory…',
  'Searching the Toronto creator index…',
  'Cross-checking engagement benchmarks…',
  'Composing your next step…',
]

function turnToMessage(t: AgentTurn): Message {
  return {
    role: t.role,
    content: t.content || t.response || '',
    tool_trace: t.action_data?.tool_trace,
  }
}

export default function AIAgentPage() {
  const { token } = useAuth()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const [thinkingIdx, setThinkingIdx] = useState(0)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!token) return
    agentHistory(token)
      .then(h => setMessages((h || []).map(turnToMessage)))
      .catch(() => {})
      .finally(() => setLoadingHistory(false))
  }, [token])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Cycle "thinking" phrases while the tool loop runs
  useEffect(() => {
    if (!loading) {
      setThinkingIdx(0)
      return
    }
    const t = setInterval(() => {
      setThinkingIdx(i => (i + 1) % THINKING_PHRASES.length)
    }, 1800)
    return () => clearInterval(t)
  }, [loading])

  const send = async (override?: string) => {
    const text = (override ?? input).trim()
    if (!text || !token || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setLoading(true)
    try {
      const res = await agentChat(text, token)
      const reply: Message = {
        role: 'assistant',
        content: res.content || res.response || '',
        tool_trace: res.action_data?.tool_trace,
      }
      setMessages(prev => [...prev, reply])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Something went wrong. Please try again.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 animate-fade-up">
        <div
          className="w-11 h-11 rounded-2xl flex items-center justify-center animate-gradient"
          style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED, #8B5CF6)' }}
        >
          <Bot className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-black text-[#1E1B4B] tracking-tight">AI Campaign Agent</h1>
          <p className="text-sm text-[#6B7280]">
            Discover Toronto creators, draft outreach, and remember your preferences — all in one chat.
          </p>
        </div>
        <span className="ml-auto hidden md:inline-flex badge animate-pop">
          <Wrench className="w-3 h-3" /> Tool-enabled
        </span>
      </div>

      {/* Two-col layout: memory panel + chat */}
      <div className="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-5">
        <aside className="space-y-4">
          <BrandMemoryPanel />
        </aside>

        <section className="flex flex-col h-[calc(100vh-13rem)] card p-5 animate-fade-up delay-1">
          <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
            {loadingHistory ? (
              <div className="flex justify-center py-10">
                <Loader2 className="w-6 h-6 animate-spin text-[#7C3AED]" />
              </div>
            ) : messages.length === 0 ? (
              <div className="py-6 animate-fade-up">
                <p className="text-sm text-[#6B7280] text-center mb-4">
                  Describe your campaign — the AI handles the rest.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {STARTERS.map((s, i) => (
                    <button
                      key={s}
                      onClick={() => send(s)}
                      className="text-left p-4 rounded-xl border border-[#E2E8F0] bg-white text-sm text-[#1E1B4B] hover:border-[#C7D2FE] hover:-translate-y-[2px] hover:shadow-md transition-all duration-200 animate-fade-up"
                      style={{ animationDelay: `${i * 60}ms` }}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((m, i) => (
                <div key={i} className={`flex animate-fade-up ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {m.role === 'assistant' && (
                    <div
                      className="w-7 h-7 rounded-lg flex items-center justify-center mr-2 mt-1 flex-shrink-0"
                      style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED)' }}
                    >
                      <Sparkles className="w-3.5 h-3.5 text-white" />
                    </div>
                  )}
                  <div className={`flex flex-col gap-1.5 max-w-[80%] ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                    {m.role === 'assistant' && m.tool_trace && m.tool_trace.length > 0 && (
                      <ToolTrace steps={m.tool_trace} />
                    )}
                    <div
                      className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap shadow-sm ${
                        m.role === 'user'
                          ? 'text-white rounded-br-sm'
                          : 'bg-white border border-[#E2E8F0] text-[#1E1B4B] rounded-bl-sm'
                      }`}
                      style={m.role === 'user' ? { background: 'linear-gradient(135deg, #4F46E5, #7C3AED)' } : {}}
                    >
                      {m.content}
                    </div>
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="flex items-start gap-2 animate-fade-in">
                <div
                  className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 animate-gradient"
                  style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED, #8B5CF6)' }}
                >
                  <Sparkles className="w-3.5 h-3.5 text-white" />
                </div>
                <div className="card px-4 py-3 min-w-[220px]">
                  <div className="flex items-center gap-2.5">
                    <div className="flex gap-1.5">
                      {[0, 1, 2].map(i => (
                        <div
                          key={i}
                          className="w-2 h-2 rounded-full bg-[#7C3AED] animate-bounce"
                          style={{ animationDelay: `${i * 0.15}s` }}
                        />
                      ))}
                    </div>
                    <span
                      key={thinkingIdx}
                      className="text-[11px] font-bold text-[#4F46E5] tracking-wide uppercase animate-fade-in"
                    >
                      {THINKING_PHRASES[thinkingIdx]}
                    </span>
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
            <button
              onClick={() => send()}
              disabled={loading || !input.trim()}
              className="btn-primary px-5"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </section>
      </div>
    </div>
  )
}
