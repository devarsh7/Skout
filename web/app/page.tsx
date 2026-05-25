import Link from 'next/link'
import Image from 'next/image'
import Navbar from '@/components/layout/Navbar'

export default function LandingPage() {
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
            AI-Powered Influencer Marketing
          </div>

          <h1 style={{ fontFamily: 'Inter, sans-serif', fontSize: 'clamp(2.8rem,6.5vw,5.2rem)', fontWeight: 900, lineHeight: 1.04, letterSpacing: '-0.045em', color: '#1E1B4B', margin: '0 auto 0.9rem', maxWidth: 840 }}>
            Find the Right Creators.{' '}
            <span style={{ background: 'linear-gradient(135deg,#4F46E5 20%,#8B5CF6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              Every Time.
            </span>
          </h1>

          <p style={{ fontSize: 'clamp(1rem,2vw,1.18rem)', color: '#6B7280', lineHeight: 1.82, maxWidth: 560, margin: '0 auto 1.25rem' }}>
            Skout uses AI to match your brand with the perfect influencers — by audience, location, engagement, and authenticity. No spreadsheets. Just results.
          </p>

          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap', paddingTop: '1.5rem' }}>
            <Link href="/business/onboarding"
              style={{ display: 'inline-flex', alignItems: 'center', background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', color: '#fff', fontWeight: 800, fontSize: 15, padding: '13px 30px', borderRadius: 999, border: 'none', boxShadow: '0 6px 22px rgba(79,70,229,.38)', textDecoration: 'none', transition: 'all .24s' }}>
              Start for Free — Brands
            </Link>
            <Link href="/creator/onboarding"
              style={{ display: 'inline-flex', alignItems: 'center', background: '#fff', color: '#4F46E5', border: '1.5px solid #C7D2FE', fontWeight: 700, fontSize: 14.5, padding: '12px 28px', borderRadius: 999, textDecoration: 'none', boxShadow: '0 2px 8px rgba(79,70,229,.08)' }}>
              Join as Creator →
            </Link>
          </div>

          <p style={{ fontSize: 13.5, color: '#9CA3AF', fontWeight: 500, marginTop: '2rem' }}>
            ✓ No credit card required &nbsp;·&nbsp; ✓ Free discovery searches included
          </p>
        </div>
      </section>

      {/* Stats strip */}
      <section style={{ padding: '3.5rem 2rem', background: '#fff', borderTop: '1px solid #E2E8F0', borderBottom: '1px solid #E2E8F0' }}>
        <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', background: 'linear-gradient(135deg,#4338CA,#7C3AED)', borderRadius: 22, padding: '3rem 1.5rem', maxWidth: 840, margin: '0 auto', boxShadow: '0 14px 44px rgba(79,70,229,.32)' }}>
          {[
            { value: '50K+', label: 'Verified Creators' },
            { value: '200+', label: 'Brands & Agencies' },
            { value: '94%', label: 'Match Accuracy' },
            { value: '2.1M+', label: 'Outreach Sent' },
          ].map((s, i) => (
            <div key={s.label} style={{ flex: 1, minWidth: 150, textAlign: 'center', padding: '0.5rem 1rem', borderLeft: i > 0 ? '1px solid rgba(255,255,255,.15)' : 'none' }}>
              <div style={{ fontSize: '2.6rem', fontWeight: 900, color: '#fff', lineHeight: 1, letterSpacing: '-0.04em' }}>{s.value}</div>
              <div style={{ fontSize: '0.82rem', color: 'rgba(255,255,255,.68)', marginTop: '0.4rem', fontWeight: 500 }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section style={{ padding: '5.5rem 2rem', background: '#EEF2FF' }}>
        <div style={{ maxWidth: 940, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
            <span style={{ fontSize: 11, fontWeight: 800, letterSpacing: '0.15em', textTransform: 'uppercase', color: '#4F46E5', display: 'block', marginBottom: '0.55rem' }}>How it works</span>
            <h2 style={{ fontFamily: 'Inter,sans-serif', fontSize: 'clamp(2rem,4vw,2.9rem)', fontWeight: 800, color: '#1E1B4B', letterSpacing: '-0.03em', margin: '0 auto 0.75rem', maxWidth: 640 }}>Three steps to your perfect creator</h2>
            <p style={{ fontSize: '1rem', color: '#6B7280', lineHeight: 1.82, maxWidth: 480, margin: '0 auto' }}>From campaign brief to shortlist in minutes, not weeks.</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 40px 1fr 40px 1fr', alignItems: 'center', maxWidth: 900, margin: '0 auto' }}>
            {[
              { icon: '🎯', n: '01', title: 'Describe your campaign', desc: 'Tell Skout your target audience, niche, location, and budget in plain English.' },
              null,
              { icon: '🤖', n: '02', title: 'AI finds your matches', desc: 'Our discovery engine searches 50K+ creators and ranks them by fit score.' },
              null,
              { icon: '✉️', n: '03', title: 'Outreach in one click', desc: 'AI drafts personalized messages. You review, approve, and send.' },
            ].map((s, i) =>
              s === null ? (
                <div key={i} style={{ textAlign: 'center', fontSize: '1.6rem', color: '#C7D2FE' }}>→</div>
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

      {/* For Brands & Creators */}
      <section style={{ padding: '5.5rem 2rem', background: '#fff' }}>
        <div style={{ maxWidth: 940, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
            <span style={{ fontSize: 11, fontWeight: 800, letterSpacing: '0.15em', textTransform: 'uppercase', color: '#4F46E5', display: 'block', marginBottom: '0.55rem' }}>Built for both sides</span>
            <h2 style={{ fontFamily: 'Inter,sans-serif', fontSize: 'clamp(2rem,4vw,2.9rem)', fontWeight: 800, color: '#1E1B4B', letterSpacing: '-0.03em', margin: '0 auto', maxWidth: 640 }}>One platform, two superpowers</h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, maxWidth: 940, margin: '0 auto' }}>
            <div style={{ borderRadius: 22, padding: '2.5rem 2.25rem', border: '1.5px solid #E0E7FF', background: 'linear-gradient(155deg,#EEF2FF,#F5F3FF)' }}>
              <div style={{ fontSize: '1.12rem', fontWeight: 800, color: '#1E1B4B', display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1.5rem' }}>
                <span style={{ fontSize: 22 }}>💼</span> For Brands & Agencies
              </div>
              {[
                { icon: '🔍', title: 'AI Discovery', desc: 'Find creators by describing your campaign in plain English.' },
                { icon: '🎯', title: 'Smart Filtering', desc: 'Filter by platform, followers, engagement, location, and niche.' },
                { icon: '✉️', title: 'AI Outreach', desc: 'Personalized DMs and emails drafted by AI for each creator.' },
                { icon: '📊', title: 'Campaign Tracker', desc: 'Monitor outreach status and campaign ROI in one dashboard.' },
              ].map(f => (
                <div key={f.title} style={{ display: 'flex', alignItems: 'flex-start', gap: 13, marginBottom: '1.1rem' }}>
                  <div style={{ flexShrink: 0, width: 34, height: 34, borderRadius: 9, marginTop: 1, background: 'linear-gradient(135deg,#4F46E5,#8B5CF6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 15 }}>{f.icon}</div>
                  <div>
                    <b style={{ display: 'block', fontSize: '0.9rem', fontWeight: 700, color: '#1E1B4B', marginBottom: 1 }}>{f.title}</b>
                    <small style={{ fontSize: '0.82rem', color: '#6B7280', lineHeight: 1.6 }}>{f.desc}</small>
                  </div>
                </div>
              ))}
              <Link href="/business/onboarding" style={{ display: 'inline-flex', alignItems: 'center', marginTop: '1rem', background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', color: '#fff', fontWeight: 800, fontSize: 14, padding: '11px 24px', borderRadius: 999, textDecoration: 'none', boxShadow: '0 4px 16px rgba(79,70,229,.3)' }}>
                Start for Free →
              </Link>
            </div>

            <div style={{ borderRadius: 22, padding: '2.5rem 2.25rem', border: '1.5px solid #DDD6FE', background: 'linear-gradient(155deg,#F3F0FF,#EDE9FE)' }}>
              <div style={{ fontSize: '1.12rem', fontWeight: 800, color: '#1E1B4B', display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1.5rem' }}>
                <span style={{ fontSize: 22 }}>🎤</span> For Creators
              </div>
              {[
                { icon: '🤖', title: 'AI Career Manager', desc: 'Your personal AI advisor for growing your creator business.' },
                { icon: '🌟', title: 'Get Discovered', desc: 'Brands search our database for creators that match their campaigns.' },
                { icon: '📈', title: 'Performance Insights', desc: 'Benchmark your stats against top creators in your niche.' },
                { icon: '🤝', title: 'Collab Management', desc: 'Track and manage brand collaboration inquiries in one place.' },
              ].map(f => (
                <div key={f.title} style={{ display: 'flex', alignItems: 'flex-start', gap: 13, marginBottom: '1.1rem' }}>
                  <div style={{ flexShrink: 0, width: 34, height: 34, borderRadius: 9, marginTop: 1, background: 'linear-gradient(135deg,#7C3AED,#8B5CF6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 15 }}>{f.icon}</div>
                  <div>
                    <b style={{ display: 'block', fontSize: '0.9rem', fontWeight: 700, color: '#1E1B4B', marginBottom: 1 }}>{f.title}</b>
                    <small style={{ fontSize: '0.82rem', color: '#6B7280', lineHeight: 1.6 }}>{f.desc}</small>
                  </div>
                </div>
              ))}
              <Link href="/creator/onboarding" style={{ display: 'inline-flex', alignItems: 'center', marginTop: '1rem', background: '#fff', color: '#7C3AED', border: '1.5px solid #DDD6FE', fontWeight: 800, fontSize: 14, padding: '11px 24px', borderRadius: 999, textDecoration: 'none' }}>
                Join for Free →
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
            Join the waitlist
          </h2>
          <p style={{ fontSize: '0.95rem', color: '#6B7280', lineHeight: 1.75, marginBottom: '2rem' }}>
            Be the first to access new features, exclusive creator tools, and brand partnerships.
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
            <p style={{ fontSize: 12.5, color: '#6B7280', lineHeight: 1.6, maxWidth: 220, margin: 0 }}>
              AI-powered influencer discovery & outreach.
            </p>
          </div>
          <div style={{ display: 'flex', gap: 24 }}>
            <div>
              <span style={{ fontSize: 9.5, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#9CA3AF', display: 'block', marginBottom: 8 }}>Platform</span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <Link href="/business/onboarding" style={{ fontSize: 13, color: '#6B7280', textDecoration: 'none' }}>For Brands</Link>
                <Link href="/creator/onboarding" style={{ fontSize: 13, color: '#6B7280', textDecoration: 'none' }}>For Creators</Link>
                <Link href="/login" style={{ fontSize: 13, color: '#6B7280', textDecoration: 'none' }}>Log in</Link>
              </div>
            </div>
          </div>
        </div>
        <div style={{ borderTop: '1px solid #E2E8F0', marginTop: '1rem', paddingTop: '0.75rem', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8, fontSize: 11.5, color: '#9CA3AF' }}>
          <span>© 2026 Skout Marketplace — LangChain · Pinecone · FastAPI · Next.js</span>
          <span style={{ color: '#4F46E5', fontWeight: 700 }}>skoutmarketplace.com</span>
        </div>
      </footer>
    </div>
  )
}
