'use client'

import { useEffect, useState } from 'react'
import { Brain, Plus, X, Loader2, ChevronDown, ChevronUp } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { listBrandFacts, addBrandFact, deleteBrandFact, BrandFact } from '@/lib/api'

const CATEGORIES = [
  { id: 'budget',     label: 'Budget',     color: '#10B981' },
  { id: 'preference', label: 'Preference', color: '#4F46E5' },
  { id: 'constraint', label: 'Constraint', color: '#EF4444' },
  { id: 'context',    label: 'Context',    color: '#7C3AED' },
  { id: 'goal',       label: 'Goal',       color: '#F59E0B' },
  { id: 'outcome',    label: 'Outcome',    color: '#06B6D4' },
  { id: 'other',      label: 'Other',      color: '#6B7280' },
] as const

function catColor(id: string): string {
  return CATEGORIES.find(c => c.id === id)?.color || '#6B7280'
}

function catLabel(id: string): string {
  return CATEGORIES.find(c => c.id === id)?.label || id
}

export default function BrandMemoryPanel({ defaultOpen = true }: { defaultOpen?: boolean }) {
  const { token } = useAuth()
  const [facts, setFacts] = useState<BrandFact[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(defaultOpen)
  const [adding, setAdding] = useState(false)
  const [newFact, setNewFact] = useState('')
  const [newCategory, setNewCategory] = useState('other')

  const refresh = async () => {
    if (!token) return
    setLoading(true)
    try {
      const res = await listBrandFacts(token)
      setFacts(res.facts)
    } catch {/* ignore */}
    finally { setLoading(false) }
  }

  useEffect(() => { refresh() /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [token])

  const handleAdd = async () => {
    if (!token || !newFact.trim()) return
    try {
      const created = await addBrandFact(newFact.trim(), newCategory, token)
      setFacts(prev => [created, ...prev])
      setNewFact('')
      setAdding(false)
    } catch {/* ignore */}
  }

  const handleDelete = async (id: string) => {
    if (!token) return
    setFacts(prev => prev.filter(f => f.id !== id))   // optimistic
    try {
      await deleteBrandFact(id, token)
    } catch {
      refresh()
    }
  }

  return (
    <div className="card overflow-hidden animate-fade-up">
      <button
        type="button"
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between gap-2 px-4 py-3 hover:bg-[#FAFAFE] transition-colors"
      >
        <div className="flex items-center gap-2">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED)' }}
          >
            <Brain className="w-3.5 h-3.5 text-white" />
          </div>
          <div className="text-left">
            <div className="text-sm font-extrabold text-[#1E1B4B]">What I remember</div>
            <div className="text-[10px] text-[#9CA3AF] tracking-wide uppercase font-bold">
              {facts.length} {facts.length === 1 ? 'fact' : 'facts'} learned
            </div>
          </div>
        </div>
        {open
          ? <ChevronUp className="w-4 h-4 text-[#6B7280]" />
          : <ChevronDown className="w-4 h-4 text-[#6B7280]" />}
      </button>

      {open && (
        <div className="border-t border-[#E2E8F0] p-4 space-y-3 animate-fade-up">
          {loading ? (
            <div className="flex justify-center py-3">
              <Loader2 className="w-4 h-4 animate-spin text-[#7C3AED]" />
            </div>
          ) : facts.length === 0 ? (
            <p className="text-xs text-[#6B7280] text-center py-2 leading-relaxed">
              Nothing yet — I&apos;ll start remembering things about your business as we chat.
            </p>
          ) : (
            <div className="space-y-1.5 max-h-[280px] overflow-y-auto pr-1">
              {facts.map((f, i) => (
                <div
                  key={f.id}
                  className="group flex items-start gap-2 p-2.5 rounded-lg hover:bg-[#FAFAFE] transition-all animate-fade-up"
                  style={{ animationDelay: `${i * 25}ms` }}
                >
                  <span
                    className="mt-1 w-1.5 h-1.5 rounded-full shrink-0"
                    style={{ background: catColor(f.category) }}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs text-[#1E1B4B] leading-snug">{f.fact}</div>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className="text-[9px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded"
                        style={{ background: `${catColor(f.category)}15`, color: catColor(f.category) }}
                      >
                        {catLabel(f.category)}
                      </span>
                      <span className="text-[9px] text-[#9CA3AF] font-bold">
                        {Math.round(f.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleDelete(f.id)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity text-[#9CA3AF] hover:text-red-500 p-0.5"
                    title="Forget this fact"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Add new fact */}
          {adding ? (
            <div className="space-y-2 animate-fade-up">
              <textarea
                className="input text-xs min-h-[60px]"
                placeholder="e.g. Budget is $300 per piece, prefers nano creators"
                value={newFact}
                onChange={e => setNewFact(e.target.value)}
                autoFocus
              />
              <div className="flex flex-wrap gap-1">
                {CATEGORIES.map(c => {
                  const active = c.id === newCategory
                  return (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => setNewCategory(c.id)}
                      className="text-[10px] font-bold uppercase tracking-wide px-2 py-1 rounded transition-all"
                      style={{
                        background: active ? c.color : `${c.color}15`,
                        color: active ? '#fff' : c.color,
                      }}
                    >
                      {c.label}
                    </button>
                  )
                })}
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleAdd}
                  disabled={!newFact.trim()}
                  className="btn-primary text-xs px-3 py-1.5 flex-1"
                >Save</button>
                <button
                  type="button"
                  onClick={() => { setAdding(false); setNewFact('') }}
                  className="btn-ghost text-xs px-3 py-1.5"
                >Cancel</button>
              </div>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => setAdding(true)}
              className="w-full inline-flex items-center justify-center gap-1.5 text-xs font-bold text-[#4F46E5] hover:text-[#4338CA] hover:bg-[#EEF2FF] rounded-lg py-2 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              Add a fact manually
            </button>
          )}
        </div>
      )}
    </div>
  )
}
