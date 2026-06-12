'use client'

import { useState } from 'react'
import {
  Search, Filter, User, Mail, BarChart3, TrendingUp, Save, Wrench,
  ChevronDown,
} from 'lucide-react'

export interface ToolStep {
  name: string
  args?: Record<string, unknown>
  label: string
  result_summary: string
}

const ICONS: Record<string, typeof Search> = {
  discover_creators:      Search,
  filter_creators:        Filter,
  get_creator_profile:    User,
  draft_outreach_message: Mail,
  get_campaign_status:    BarChart3,
  get_local_benchmark:    TrendingUp,
  save_brand_fact:        Save,
}

function formatArgs(args?: Record<string, unknown>): string {
  if (!args) return ''
  const entries = Object.entries(args).filter(([, v]) => v !== null && v !== undefined && v !== '')
  if (entries.length === 0) return ''
  return entries
    .map(([k, v]) => {
      if (Array.isArray(v)) return `${k}: [${v.length}]`
      if (typeof v === 'string') return v.length > 40 ? `${k}: ${v.slice(0, 40)}…` : `${k}: ${v}`
      return `${k}: ${v}`
    })
    .join(' · ')
}

function ToolStepRow({ step, delayMs }: { step: ToolStep; delayMs: number }) {
  const [open, setOpen] = useState(false)
  const Icon = ICONS[step.name] || Wrench
  const isError = step.result_summary.startsWith('error')
  const argsLine = formatArgs(step.args)
  const expandable = !!argsLine

  return (
    <div
      className="rounded-lg border border-[#E0E7FF] bg-[#FAFAFE] overflow-hidden animate-fade-up hover:border-[#C7D2FE] transition-colors"
      style={{ animationDelay: `${delayMs}ms` }}
    >
      <button
        type="button"
        onClick={() => expandable && setOpen(o => !o)}
        disabled={!expandable}
        className={`w-full flex items-center gap-2 px-2.5 py-1.5 text-left ${
          expandable ? 'cursor-pointer hover:bg-white' : 'cursor-default'
        } transition-colors`}
      >
        <div
          className="w-5 h-5 rounded-md flex items-center justify-center shrink-0"
          style={{ background: 'linear-gradient(135deg, #4F46E5, #7C3AED)' }}
        >
          <Icon className="w-3 h-3 text-white" />
        </div>
        <span className="text-[11px] font-bold text-[#1E1B4B] truncate flex-1">
          {step.label}
        </span>
        <span
          className={`text-[10px] font-bold uppercase tracking-wide whitespace-nowrap ${
            isError ? 'text-red-600' : 'text-emerald-600'
          }`}
        >
          {isError ? '⚠' : '✓'} {step.result_summary}
        </span>
        {expandable && (
          <ChevronDown
            className={`w-3 h-3 text-[#6B7280] transition-transform duration-200 ${
              open ? 'rotate-180' : ''
            }`}
          />
        )}
      </button>
      {expandable && open && (
        <div className="px-3 pb-2 pt-1 border-t border-[#E0E7FF] bg-white animate-fade-in">
          <div className="text-[9px] tracking-[0.12em] uppercase font-bold text-[#9CA3AF] mb-1">
            Arguments
          </div>
          <div className="text-[11px] text-[#1E1B4B] font-mono leading-snug break-words">
            {argsLine}
          </div>
        </div>
      )}
    </div>
  )
}

export default function ToolTrace({ steps }: { steps: ToolStep[] }) {
  if (!steps || steps.length === 0) return null
  return (
    <div className="space-y-1.5 mb-1 w-full max-w-full">
      {steps.map((s, i) => (
        <ToolStepRow key={i} step={s} delayMs={i * 60} />
      ))}
    </div>
  )
}
