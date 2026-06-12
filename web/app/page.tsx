'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import Navbar from '@/components/layout/Navbar'

export default function LandingPage() {
  const [howItWorksTab, setHowItWorksTab] = useState<'creator' | 'brand'>('creator')

  const creatorSteps = [
    { icon: '🔗', n: '01', title: 'Add your handles', desc: 'Drop your Instagram, TikTok, YouTube — whatever you’re on. Two minutes, no follower minimum.' },
    { icon: '✨', n: '02', title: 'Get matched', desc: 'Brands describe what they need. Our AI puts you in front of the ones that actually fit your audience.' },
    { icon: '💸', n: '03', title: 'Get paid', desc: 'Approve the brief, post the content, get paid. No agency taking 30% off the top.' },
  ]

  const brandSteps = [
    { icon: '🎯', n: '01', title: 'Describe your campaign', desc: 'Tell Skout your target audience, niche, location, and budget in plain English.' },
    { icon: '🤖', n: '02', title: 'AI finds your matches', desc: 'Our discovery engine searches verified creators and ranks them by audience fit.' },
    { icon: '✉️', n: '03', title: 'Outreach in one click', desc: 'AI drafts personalized messages. You review, approve, and send.' },
  ]

  const steps = howItWorksTab === 'creator' ? creatorSteps : brandSteps

  return (
    <div className="min-h-screen" style={{ background: '#FAFAFE', fontFamily: 'Inter, sans-serif' }}>
      <Navbar />

      {/* Hero */}
      <section style={{ padding: '8rem 2rem 4rem', textAlign: 'center', position: 'relative', overflow: 'hidden', background: 'linear-gradient(165deg,#F0EFFF 0%,#EEF0FF 45%,#F5F3FF 100%)' }}>
        <div style={{ position: 'absolute', width: 650, height: 650, top: -200, right: -130, background: 'rgba(99,102,241,.2)', borderRadius: '50%', filter: 'blur(50px)', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', width: 500, height: 500, bottom: -160, left: -100, background: 'rgba(139,92,246,.15)', borderRadius: '50%', filter: 'blur(50px)', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', width: 280, height: 280, top: '35%', left: '18%', background: 'rgba(167,139,250,.1)', borderRadius: '50%', filter: 'blur(40px)', pointerEvents: 'none' }} />

        <div style={{ position: 'relative', maxWidth: 860, margin: '0 auto' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: '#fff', border: '1.5px solid #C7D2FE', color: '#4F46E5', fontWeight: 700, fontSize: 11.5, letterSpacing: '0.1em', textTransform: 'uppercase', padding: '7px 18px', borderRadius: 999, marginBottom: '1.75rem', boxShadow: '0 3px 10px rgba(79,70,229,.12)' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#4F46E5', display: 'inline-block' }} />
            Built for Micro-Creators · 500–50K Followers
          </div>

          <h1 style={{ fontFamily: 'Inter, sans-serif', fontSize: 'clamp(2.8rem,6.5vw,5.2rem)', fontWeight: 900, lineHeight: 1.04, letterSpacing: '-0.045em', color: '#1E1B4B', margin: '0 auto 0.9rem', maxWidth: 840 }}>
            Get Found{' '}
            <span style={{ background: 'linear-gradient(135deg,#4F46E5 20%,#8B5CF6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              Before Famous.
            </span>
          </h1>

          <p style={{ fontSize: 'clamp(1rem,2vw,1.18rem)', color: '#6B7280', lineHeight: 1.82, maxWidth: 580, margin: '0 auto 1.25rem' }}>
            Local brands are looking for creators right now — not Kardashians. Add your handles, get matched, get paid. Skip the cold DMs.
          </p>

          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap', paddingTop: '1.5rem' }}>
            <Link href="/creator/onboarding"
              style={{ display: 'inline-flex', alignItems: 'center', background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', color: '#fff', fontWeight: 800, fontSize: 15, padding: '13px 30px', borderRadius: 999, border: 'none', boxShadow: '0 6px 22px rgba(79,70,229,.38)', textDecoration: 'none', transition: 'all .24s' }}>
              Join as Creator — Free
            </Link>
            <Link href="/business/onboarding"
              style={{ display: 'inline-flex', alignItems: 'center', background: '#fff', color: '#4F46E5', border: '1.5px solid #C7D2FE', fontWeight: 700, fontSize: 14.5, padding: '12px 28px', borderRadius: 999, textDecoration: 'none', boxShadow: '0 2px 8px rgba(79,70,229,.08)' }}>
              I’m a Brand →
            </Link>
          </div>

          <p style={{ fontSize: 13.5, color: '#9CA3AF', fontWeight: 500, marginTop: '2rem' }}>
            ✓ Free to join for creators &nbsp;·&nbsp; ✓ No follower minimum &nbsp;·&nbsp; ✓ Your data stays yours
          </p>
        </div>
      </section>

      {/* Differentiators strip */}
      <section style={{ padding: '3.5rem 2rem', background: '#fff', borderTop: '1px solid #E2E8F0', borderBottom: '1px solid #E2E8F0' }}>
        <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', background: 'linear-gradient(135deg,#4338CA,#7C3AED)', borderRadius: 22, padding: '3rem 1.5rem', maxWidth: 940, margin: '0 auto', boxShadow: '0 14px 44px rgba(79,70,229,.32)' }}>
          {[
            { icon: '🔒', value: 'Owned data', label: 'Creators opt in. No scraping, no surprises.' },
            { icon: '🚫', value: 'No agency fees', label: 'Skip the 30% middleman cut. Keep your budget.' },
            { icon: '✅', value: 'Verified handles', label: 'Every creator confirms their socials at sign-up.' },
            { icon: '📍', value: 'Hyperlocal', label: 'Match by city, neighborhood, even zip code.' },
          ].map((s, i) => (
            <div key={s.value} style={{ flex: 1, minWidth: 170, textAlign: 'center', padding: '0.5rem 1rem', borderLeft: i > 0 ? '1px solid rgba(255,255,255,.15)' : 'none' }}>
              <div style={{ fontSize: '1.6rem', marginBottom: '0.6rem' }}>{s.icon}</div>
              <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#fff', lineHeight: 1.2, letterSpacing: '-0.02em' }}>{s.value}</div>
              <div style={{ fontSize: '0.78rem', color: 'rgba(255,255,255,.72)', marginTop: '0.45rem', fontWeight: 500, lineHeight: 1.5 }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section style={{ padding: '5.5rem 2rem', background: '#EEF2FF' }}>
        <div style={{ maxWidth: 940, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
            <span style={{ fontSize: 11, fontWeight: 800, letterSpacing: '0.15em', textTransform: 'uppercase', color: '#4F46E5', display: 'block', marginBottom: '0.55rem' }}>How it works</span>
            <h2 style={{ fontFamily: 'Inter,sans-serif', fontSize: 'clamp(2rem,4vw,2.9rem)', fontWeight: 800, color: '#1E1B4B', letterSpacing: '-0.03em', margin: '0 auto 0.75rem', maxWidth: 640 }}>
              {howItWorksTab === 'creator' ? 'Three steps from handle to paycheck' : 'Three steps to your perfect creator'}
            </h2>
            <p style={{ fontSize: '1rem', color: '#6B7280', lineHeight: 1.82, maxWidth: 520, margin: '0 auto' }}>
              {howItWorksTab === 'creator'
                ? 'No portfolio decks. No DM grind. Just the brands that fit your audience.'
                : 'From campaign brief to shortlist in minutes, not weeks.'}
            </p>
          </div>

          {/* Tab toggle */}
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '3rem' }}>
            <div style={{ display: 'inline-flex', background: '#fff', border: '1.5px solid #E0E7FF', borderRadius: 999, padding: 5, boxShadow: '0 2px 10px rgba(79,70,229,.06)' }}>
              {(['creator', 'brand'] as const).map((t) => {
                const active = howItWorksTab === t
                return (
                  <button
                    key={t}
                    onClick={() => setHowItWorksTab(t)}
                    style={{
                      padding: '9px 22px',
                      borderRadius: 999,
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: 13.5,
                      fontWeight: 800,
                      fontFamily: 'Inter, sans-serif',
                      letterSpacing: '0.01em',
                      color: active ? '#fff' : '#6B7280',
                      background: active ? 'linear-gradient(135deg,#4F46E5,#7C3AED)' : 'transparent',
                      boxShadow: active ? '0 4px 14px rgba(79,70,229,.28)' : 'none',
                      transition: 'all .2s',
                    }}
                  >
                    {t === 'creator' ? "I’m a Creator" : "I’m a Brand"}
                  </button>
                )
              })}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 40px 1fr 40px 1fr', alignItems: 'center', maxWidth: 900, margin: '0 auto' }}>
            {[steps[0], null, steps[1], null, steps[2]].map((s, i) =>
              s === null ? (
                <div key={`arrow-${i}`} style={{ textAlign: 'center', fontSize: '1.6rem', color: '#C7D2FE' }}>→</div>
              ) : (
                <div key={s.n} style={{ background: '#fff', border: '1.5px solid #E0E7FF', borderRadius: 22, padding: '2.25rem 1.75rem', textAlign: 'center', boxShadow: '0 2px 14px rgba(79,70,229,.05)' }}>
                  <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 58, height: 58, borderRadius: 16, background: 'linear-gradient(135deg,#4F46E5,#8B5CF6)', fontSize: 26, marginBottom: '1.25rem', boxShadow: '0 5px 16px rgba(79,70,229,.3)' }}>{s.icon}</div>
                  <div style={{ fontSize: 10, fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#4F46E5', marginBottom: '0.4rem' }}>{s.n}</div>
                  <div style={{ fontWeight: 800, fontSize: '1.05rem', color: '#1E1B4B', marginBottom: '0.5rem' }}>{s.title}</div>
                  <div style={{ fontSize: '0.88rem', color: '#6B7280', lineHeight: 1.75 }}>{s.desc}</div>
                </div>
              )
            )}
          </div>
        </div>
      </section>

      {/* For Creators & Brands */}
      <section style={{ padding: '5.5rem 2rem', background: '#fff' }}>
        <div style={{ maxWidth: 940, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
            <span style={{ fontSize: 11, fontWeight: 800, letterSpacing: '0.15em', textTransform: 'uppercase', color: '#4F46E5', display: 'block', marginBottom: '0.55rem' }}>Built for both sides</span>
            <h2 style={{ fontFamily: 'Inter,sans-serif', fontSize: 'clamp(2rem,4vw,2.9rem)', fontWeight: 800, color: '#1E1B4B', letterSpacing: '-0.03em', margin: '0 auto', maxWidth: 640 }}>One platform, two superpowers</h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, maxWidth: 940, margin: '0 auto' }}>
            {/* Creator card — LEFT, primary visual position */}
            <div style={{ borderRadius: 22, padding: '2.5rem 2.25rem', border: '1.5px solid #DDD6FE', background: 'linear-gradient(155deg,#F3F0FF,#EDE9FE)' }}>
              <div style={{ fontSize: '1.12rem', fontWeight: 800, color: '#1E1B4B', display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1.5rem' }}>
                <span style={{ fontSize: 22 }}>🎤</span> For Creators
              </div>
              {[
                { icon: '🌟', title: 'Get discovered', desc: 'Brands actively search for creators like you — no cold DMs required.' },
                { icon: '🤖', title: 'AI Career Manager', desc: 'A personal advisor that pitches your strengths and flags every new opportunity.' },
                { icon: '📈', title: 'Know your worth', desc: 'See how your engagement and authenticity score stack up in your niche and city.' },
                { icon: '🤝', title: 'Every brand DM, one inbox', desc: 'Track collab inquiries, briefs, and payments without losing threads in Instagram.' },
              ].map(f => (
                <div key={f.title} style={{ display: 'flex', alignItems: 'flex-start', gap: 13, marginBottom: '1.1rem' }}>
                  <div style={{ flexShrink: 0, width: 34, height: 34, borderRadius: 9, marginTop: 1, background: 'linear-gradient(135deg,#7C3AED,#8B5CF6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 15 }}>{f.icon}</div>
                  <div>
                    <b style={{ display: 'block', fontSize: '0.9rem', fontWeight: 700, color: '#1E1B4B', marginBottom: 1 }}>{f.title}</b>
                    <small style={{ fontSize: '0.82rem', color: '#6B7280', lineHeight: 1.6 }}>{f.desc}</small>
                  </div>
                </div>
              ))}
              <Link href="/creator/onboarding" style={{ display: 'inline-flex', alignItems: 'center', marginTop: '1rem', background: 'linear-gradient(135deg,#7C3AED,#4F46E5)', color: '#fff', fontWeight: 800, fontSize: 14, padding: '11px 24px', borderRadius: 999, textDecoration: 'none', boxShadow: '0 4px 16px rgba(124,58,237,.3)' }}>
                Claim Your Profile →
              </Link>
            </div>

            {/* Brand card — RIGHT */}
            <div style={{ borderRadius: 22, padding: '2.5rem 2.25rem', border: '1.5px solid #E0E7FF', background: 'linear-gradient(155deg,#EEF2FF,#F5F3FF)' }}>
              <div style={{ fontSize: '1.12rem', fontWeight: 800, color: '#1E1B4B', display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1.5rem' }}>
                <span style={{ fontSize: 22 }}>💼</span> For Brands & Agencies
              </div>
              {[
                { icon: '🔍', title: 'Skip the agency', desc: 'Find creators by describing your campaign — no $5K retainer required.' },
                { icon: '🎯', title: 'Smart filtering', desc: 'Filter by platform, follower range, engagement, location, and niche.' },
                { icon: '✉️', title: 'AI outreach', desc: 'Personalized DMs and emails drafted for every creator you shortlist.' },
                { icon: '📊', title: 'Campaign tracker', desc: 'Pipeline, replies, deliverables, and ROI in one dashboard.' },
              ].map(f => (
                <div key={f.title} style={{ display: 'flex', alignItems: 'flex-start', gap: 13, marginBottom: '1.1rem' }}>
                  <div style={{ flexShrink: 0, width: 34, height: 34, borderRadius: 9, marginTop: 1, background: 'linear-gradient(135deg,#4F46E5,#8B5CF6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 15 }}>{f.icon}</div>
                  <div>
                    <b style={{ display: 'block', fontSize: '0.9rem', fontWeight: 700, color: '#1E1B4B', marginBottom: 1 }}>{f.title}</b>
                    <small style={{ fontSize: '0.82rem', color: '#6B7280', lineHeight: 1.6 }}>{f.desc}</small>
                  </div>
                </div>
              ))}
              <Link href="/business/onboarding" style={{ display: 'inline-flex', alignItems: 'center', marginTop: '1rem', background: '#fff', color: '#4F46E5', border: '1.5px solid #C7D2FE', fontWeight: 800, fontSize: 14, padding: '11px 24px', borderRadius: 999, textDecoration: 'none' }}>
                Start a Search →
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Waitlist / CTA */}
      <section style={{ padding: '5.5rem 2rem', background: '#EEF2FF' }}>
        <div style={{ maxWidth: 520, margin: '0 auto', background: 'linear-gradient(145deg,#EDE9FE 0%,#DDD6FE 100%)', borderRadius: 24, padding: '3rem 2.5rem 2.5rem', boxShadow: '0 8px 32px rgba(109,40,217,.12)', border: '1.5px solid #C4B5FD', textAlign: 'center' }}>
          <div style={{ fontSize: 11, fontWeight: 800, letterSpacing: '0.15em', textTransform: 'uppercase', color: '#7C3AED', marginBottom: '0.75rem' }}>Early Access</div>
          <h2 style={{ fontFamily: 'Inter,sans-serif', fontSize: '1.8rem', fontWeight: 900, color: '#1E1B4B', letterSpacing: '-0.03em', margin: '0 0 0.75rem' }}>
            Get on the list. Local brands are watching.
          </h2>
          <p style={{ fontSize: '0.95rem', color: '#6B7280', lineHeight: 1.75, marginBottom: '2rem' }}>
            We’re onboarding the first 100 creators with brands in their city. Drop your email — we’ll text you when it’s your turn.
          </p>
          <div style={{ display: 'flex', gap: 10, maxWidth: 380, margin: '0 auto' }}>
            <input
              type="email"
              placeholder="your@email.com"
              style={{ flex: 1, padding: '11px 16px', borderRadius: 12, border: '1.5px solid #C4B5FD', background: '#fff', fontSize: 14, color: '#1E1B4B', outline: 'none', fontFamily: 'Inter,sans-serif' }}
            />
            <button style={{ padding: '11px 20px', borderRadius: 12, background: 'linear-gradient(135deg,#7C3AED,#4F46E5)', color: '#fff', fontWeight: 800, fontSize: 14, border: 'none', cursor: 'pointer', whiteSpace: 'nowrap' }}>
              Join
            </button>
          </div>
          <p style={{ fontSize: 12, color: '#9CA3AF', marginTop: '1rem' }}>No spam. Unsubscribe anytime.</p>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '2px solid #E2E8F0', padding: '1.5rem 1.75rem 1rem', background: '#fff' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <Image src="/skout-logo.png" alt="Skout" width={100} height={32} style={{ height: 32, width: 'auto', marginBottom: 8 }} />
            <p style={{ fontSize: 12.5, color: '#6B7280', lineHeight: 1.6, maxWidth: 240, margin: 0 }}>
              The fair-deal marketplace for micro-creators and local brands.
            </p>
          </div>
          <div style={{ display: 'flex', gap: 24 }}>
            <div>
              <span style={{ fontSize: 9.5, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#9CA3AF', display: 'block', marginBottom: 8 }}>Platform</span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <Link href="/creator/onboarding" style={{ fontSize: 13, color: '#6B7280', textDecoration: 'none' }}>For Creators</Link>
                <Link href="/business/onboarding" style={{ fontSize: 13, color: '#6B7280', textDecoration: 'none' }}>For Brands</Link>
                <Link href="/login" style={{ fontSize: 13, color: '#6B7280', textDecoration: 'none' }}>Log in</Link>
              </div>
            </div>
          </div>
        </div>
        <div style={{ borderTop: '1px solid #E2E8F0', marginTop: '1rem', paddingTop: '0.75rem', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8, fontSize: 11.5, color: '#9CA3AF' }}>
          <span>© 2026 Skout Marketplace</span>
          <span style={{ color: '#4F46E5', fontWeight: 700 }}>skoutmarketplace.com</span>
        </div>
      </footer>
    </div>
  )
}
