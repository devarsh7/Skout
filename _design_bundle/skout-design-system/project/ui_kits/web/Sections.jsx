/* global React, Eyebrow, Button, StatusDot, WordReveal */
const { useState, useEffect } = React;

const HERO_CREATORS = [
  { handle: '@priyastyles', niche: 'Beauty · Mumbai', followers: '124K', er: '4.8%', hue: 340, emoji: '💄', score: '0.91' },
  { handle: '@berlinbytes', niche: 'Tech · Berlin',   followers: '58K',  er: '6.2%', hue: 260, emoji: '💻', score: '0.86' },
  { handle: '@maya.cooks',  niche: 'Food · Austin',   followers: '215K', er: '4.1%', hue: 30,  emoji: '🍳', score: '0.82' },
  { handle: '@okanodog',    niche: 'Pets · Toronto',  followers: '42K',  er: '7.0%', hue: 150, emoji: '🐕', score: '0.78' },
];

const HERO_PROMPTS = [
  'vegan skincare micro-influencers in Berlin',
  'tech reviewers in India, 50k+ YouTube subs',
  'dog creators on TikTok, 10k–100k followers',
  'sustainable fashion, engagement above 5%',
];

function TypingPrompt() {
  const [idx, setIdx] = useState(0);
  const [sub, setSub] = useState(0);
  useEffect(() => {
    const txt = HERO_PROMPTS[idx];
    if (sub < txt.length) {
      const t = setTimeout(() => setSub(sub + 1), 45);
      return () => clearTimeout(t);
    }
    const t = setTimeout(() => { setSub(0); setIdx((idx + 1) % HERO_PROMPTS.length); }, 2400);
    return () => clearTimeout(t);
  }, [idx, sub]);
  return (
    <span className="sk-typing">
      {HERO_PROMPTS[idx].slice(0, sub)}
      <span className="sk-caret">▎</span>
    </span>
  );
}

function HeroCollage() {
  const [hovered, setHovered] = useState(1);
  return (
    <div className="sk-hero-right" aria-hidden>
      <div className="sk-hero-search">
        <span className="sk-hero-search-icn">🔍</span>
        <TypingPrompt />
      </div>
      <div className="sk-hero-pulse" />
      <div className="sk-hero-stack">
        {HERO_CREATORS.map((c, i) => {
          const isUp = hovered === i;
          return (
            <div
              key={c.handle}
              className={`sk-hc ${isUp ? 'is-up' : ''}`}
              style={{
                '--hue': c.hue,
                top: i * 78 + 'px',
                transform: `rotate(${(i - 1.5) * 1.5}deg) translateY(${isUp ? -6 : 0}px)`,
                zIndex: isUp ? 10 : 4 - i,
              }}
              onMouseEnter={() => setHovered(i)}
            >
              <div className="sk-hc-avatar">{c.emoji}</div>
              <div className="sk-hc-meta">
                <div className="sk-hc-handle">{c.handle}</div>
                <div className="sk-hc-niche">{c.niche}</div>
              </div>
              <div className="sk-hc-score">{c.score}</div>
            </div>
          );
        })}
      </div>
      <div className="sk-hero-chip sk-chip-float-1">✨ semantic match</div>
      <div className="sk-hero-chip sk-chip-float-2">Pinecone ranked</div>
    </div>
  );
}

function Hero({ onNavigate }) {
  return (
    <section id="home" className="sk-hero">
      <div className="sk-hero-inner sk-hero-grid">
        <div className="sk-hero-left">
          <div className="sk-hero-badge"><Eyebrow>AI-Powered Creator Discovery</Eyebrow></div>
          <h1 className="sk-display sk-hero-title">
            Find the right creators.<br />
            <span className="sk-accent">In plain English.</span>
          </h1>
          <p className="sk-lead sk-hero-sub">
            Skout connects brands with creators through semantic search and multi-agent AI —
            no scraping, no third-party APIs, just your own data working for you.
          </p>
          <div className="sk-hero-status"><StatusDot online /></div>
          <div className="sk-hero-actions">
            <Button variant="primary" icon="mic" onClick={() => onNavigate('onboarding')}>Join as Creator</Button>
            <Button variant="outline" icon="search" onClick={() => onNavigate('discover')}>Discover Creators</Button>
          </div>
        </div>
        <HeroCollage />
      </div>
    </section>
  );
}

function SectionHeader({ eyebrow, title, titleAccent, sub, center }) {
  return (
    <div className={`sk-section-header ${center ? 'is-center' : ''}`}>
      <p className="sk-label">{eyebrow}</p>
      <h2 className="sk-title">{title} {titleAccent && <span className="sk-grad">{titleAccent}</span>}</h2>
      {sub && <p className="sk-sub">{sub}</p>}
    </div>
  );
}

function FeatureCard({ icon, title, desc, delay = 0 }) {
  return (
    <div className="sk-card sk-feature" style={{ animationDelay: `${delay}ms` }}>
      <span className="sk-feature-icon">{icon}</span>
      <div className="sk-feature-title">{title}</div>
      <p className="sk-feature-desc">{desc}</p>
    </div>
  );
}

function MissionQuote({ children }) {
  return <div className="sk-mission"><p className="sk-mission-quote">{children}</p></div>;
}

function PageHeader({ icon, title, sub }) {
  return (
    <div className="sk-page-hdr">
      <div className="sk-page-hdr-row">
        {icon && <span className="sk-page-hdr-icon">{icon}</span>}
        <h1 className="sk-page-hdr-title">{title}</h1>
      </div>
      <p className="sk-page-hdr-sub">{sub}</p>
    </div>
  );
}

Object.assign(window, { Hero, SectionHeader, FeatureCard, MissionQuote, PageHeader });
