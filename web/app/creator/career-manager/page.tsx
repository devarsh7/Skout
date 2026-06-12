'use client'

import { useEffect, useRef, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { creatorAgentChat, creatorAgentHistory } from '@/lib/api'
import {
  MessageSquare, Calculator, FileSearch, Send, Sparkles, Loader2,
} from 'lucide-react'
import RateCalculator from '@/components/career/RateCalculator'
import BriefEvaluator from '@/components/career/BriefEvaluator'
import VoiceProfileCard from '@/components/career/VoiceProfileCard'

type Tab = 'chat' | 'calculator' | 'evaluator'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

// ── Tab strip ─────────────────────────────────────────────────────────────────

function TabStrip({ tab, setTab }: { tab: Tab; setTab: (t: Tab) => void }) {
  const tabs: { id: Tab; label: string; icon: typeof MessageSquare; sub: string }[] = [
    { id: 'chat',       label: 'Chat',            icon: MessageSquare, sub: 'Career advice' },
    { id: 'calculator', label: 'Rate Calculator', icon: Calculator,    sub: 'Quote in seconds' },
    { id: 'evaluator',  label: 'Brief Evaluator', icon: FileSearch,    sub: 'Decode brand briefs' },
  ]
  return (
    <div className="flex gap-2 p-1.5 bg-white border border-[#E2E8F0] rounded-2xl shadow-sm">
      {tabs.map((t, i) => {
        const Icon = t.icon
        const active = t.id === tab
        return (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`group flex-1 relative flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl font-bold text-sm transition-all duration-200 animate-fade-up
              ${active
                ? 'text-white shadow-[0_6px_18px_rgba(79,70,229,0.30)] -translate-y-[1px]'
                : 'text-[#1E1B4B] hover:bg-[#FAFAFE]'}`}
            style={{
              animationDelay: `${i * 40}ms`,
              ...(active ? { background: 'linear-gradient(135deg, #4F46E5, #7C3AED)' } : {}),
            }}
          >
            <Icon className={`w-4 h-4 transition-transform ${active ? '' : 'group-hover:rotate-[-6deg]'}`} />
            <span>{t.label}</span>
          </button>
        )
      })}
    </div>
  )
}

// ── Chat panel (now light theme to match surrounding layout) ──────────────────

function ChatPanel() {
  const { token } = useAuth()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!token) return
    creatorAgentHistory(token)
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
      const res = await creatorAgentChat(userMsg, token) as unknown as { content?: string; response?: string }
      const reply = res.content || res.response || ''
      setMessages(prev => [...prev, { role: 'assistant', content: reply }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' }])
    } finally {
      setLoading(false)
    }
  }

  // Toronto-flavoured starters
  const starters = [
    'A Queen West coffee shop wants 1 reel + 3 stories — what do I quote?',
    'Help me write a pitch for Toronto Tourism (lifestyle / parenting niche).',
    'My engagement dropped from 5.4% to 3.1% — diagnose me.',
    'Draft a counter-offer when a brand says they only have $300.',
  ]

  return (
    <div className="flex flex-col h-[calc(100vh-13rem)] animate-fade-in">
      {messages.length === 0 && !loadingHistory && (
        <div className="mb-4">
          <VoiceProfileCard />
        </div>
      )}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
        {loadingHistory ? (
          <div className="flex justify-center py-10">
            <Loader2 className="w-6 h-6 animate-spin text-[#7C3AED]" />
          </div>
        ) : messages.length === 0 ? (
          <div className="py-8 animate-fade-up">
            <p className="text-[#6B7280] text-sm mb-4 text-center">
              Start a conversation, or try one of these:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {starters.map((s, i) => (
                <button
                  key={s}
                  onClick={() => setInput(s)}
                  className="card p-4 text-left text-sm text-[#1E1B4B] hover:border-[#C7D2FE] hover:-translate-y-[2px] transition-all duration-200 animate-fade-up"
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
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap shadow-sm ${
                  m.role === 'user'
                    ? 'text-white rounded-br-sm'
                    : 'bg-white border border-[#E2E8F0] text-[#1E1B4B] rounded-bl-sm'
                }`}
                style={m.role === 'user' ? { background: 'linear-gradient(135deg, #4F46E5, #7C3AED)' } : {}}
              >
                {m.content}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex items-start gap-2 animate-fade-in">
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED)' }}
            >
              <Sparkles className="w-3.5 h-3.5 text-white" />
            </div>
            <div className="card px-4 py-3">
              <div className="flex gap-1.5">
                {[0, 1, 2].map(i => (
                  <div
                    key={i}
                    className="w-2 h-2 rounded-full bg-[#7C3AED] animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }}
                  />
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
          placeholder="Ask your career manager anything…"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          disabled={loading}
        />
        <button
          onClick={send}
          disabled={loading || !input.trim()}
          className="btn-primary px-5"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function CareerManagerPage() {
  const [tab, setTab] = useState<Tab>('chat')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 animate-fade-up">
        <div
          className="w-11 h-11 rounded-2xl flex items-center justify-center animate-gradient"
          style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED, #8B5CF6)' }}
        >
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-black text-[#1E1B4B] tracking-tight">
            AI Career Manager
          </h1>
          <p className="text-sm text-[#6B7280]">
            Your personal advisor — chat, calculate quotes, decode brand briefs.
          </p>
        </div>
      </div>

      {/* Tab strip */}
      <TabStrip tab={tab} setTab={setTab} />

      {/* Tab content */}
      <div key={tab} className="animate-fade-in">
        {tab === 'chat'       && <ChatPanel />}
        {tab === 'calculator' && <RateCalculator />}
        {tab === 'evaluator'  && <BriefEvaluator />}
      </div>
    </div>
  )
}
