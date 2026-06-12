/* global React, Navbar, Footer, Hero, SectionHeader, FeatureCard, MissionQuote, PageHeader, Button, Input, ChipSelect, Select, NumberField, Checkbox, CreatorCard, Chip, Icon */
const { useState, useEffect } = React;

// --- Mock creator data (shape matches the real API) ---
const CREATORS = [
  {
    id: 'c_001', display_name: '@priyastyles', bio: 'Toronto-based beauty creator focusing on clean, cruelty-free skincare. Community of Gen-Z women interested in sustainable routines.',
    niches: ['beauty', 'sustainability', 'lifestyle'], city: 'Toronto', country: 'CA',
    total_followers: 124000, avg_engagement_rate: 0.0482, email: 'priya@example.com',
    handles: { instagram: 'priyastyles', tiktok: 'priyastyles', youtube: 'https://youtube.com/@priyastyles' },
  },
  {
    id: 'c_002', display_name: '@berlinbytes', bio: 'Tech reviewer covering indie hardware and clean UX. Audience skews 25-34, Berlin + EU-wide.',
    niches: ['tech', 'business'], city: 'Berlin', country: 'DE',
    total_followers: 58000, avg_engagement_rate: 0.0621, email: 'hi@berlinbytes.de',
    handles: { instagram: 'berlinbytes', youtube: 'https://youtube.com/@berlinbytes' },
  },
  {
    id: 'c_003', display_name: '@maya.cooks', bio: 'Food creator. Slow-cooked weeknight meals, pantry-first. Austin, TX.',
    niches: ['food', 'lifestyle'], city: 'Austin', country: 'US',
    total_followers: 215000, avg_engagement_rate: 0.0411, email: 'maya@example.com',
    handles: { instagram: 'maya.cooks', tiktok: 'mayacooks' },
  },
  {
    id: 'c_004', display_name: '@okanodog', bio: 'Dog-parent creator. Training tips, gentle-care product reviews.',
    niches: ['pets', 'lifestyle'], city: 'Toronto', country: 'CA',
    total_followers: 42000, avg_engagement_rate: 0.0702,
    handles: { tiktok: 'okanodog', instagram: 'okano.dog' },
  },
];

function HomePage({ onNavigate }) {
  return (
    <>
      <Hero onNavigate={onNavigate} />
      <div className="sk-line" />
      <section className="sk-section sk-section-white">
        <SectionHeader
          eyebrow="How it works"
          title="Two sides. One seamless workflow."
          sub="Creators onboard themselves — brands search in natural language. AI handles the matching, filtering, and outreach drafting."
        />
        <div className="sk-grid-3">
          <FeatureCard icon="🎤" title="Creator Onboarding" desc="Creators share handles, niches, audience data, and rates in under two minutes. Their profile is instantly indexed for semantic search." delay={0} />
          <FeatureCard icon="🔍" title="AI Discovery" desc="Brands describe what they need in plain English. The Discovery Agent returns semantically ranked creators — no keywords required." delay={80} />
          <FeatureCard icon="🎯" title="Smart Filtering" desc="A LangGraph pipeline layers hard filters on top of semantic search: platform, followers, engagement, location, language, and more." delay={160} />
        </div>
      </section>
      <div className="sk-line" />
      <section id="mission" className="sk-section sk-section-alt">
        <SectionHeader eyebrow="Our Mission" title="Built on trust." titleAccent="Powered by AI." />
        <MissionQuote>
          "Influencer marketing is broken — brands overpay for scraped, stale data while creators lose control of their own profiles. Skout puts creators in the driver's seat: they opt in, they own their data, and they get discovered by brands that actually fit."
        </MissionQuote>
        <div className="sk-grid-2" style={{ marginTop: 40 }}>
          <FeatureCard icon="🔒" title="Owned Data" desc="Every profile is opt-in. No scraping, no ToS violations, no surprise API bills. Creators control what brands see about them." delay={0} />
          <FeatureCard icon="🧠" title="Multi-Agent AI" desc="Discovery, Filtering, and Outreach agents coordinated by LangGraph — each specialized, working in concert to surface the right match." delay={80} />
        </div>
      </section>
      <div className="sk-line" />
      <section className="sk-section sk-section-white">
        <SectionHeader center eyebrow="Get Started" title="Ready to find your next creator?" sub="Whether you're a creator who wants to get discovered or a brand searching for the perfect fit — Skout gets you there in minutes." />
        <div className="sk-hero-actions" style={{ justifyContent: 'center' }}>
          <Button variant="primary" icon="mic" onClick={() => onNavigate('onboarding')}>Onboard as Creator</Button>
          <Button variant="outline" icon="search" onClick={() => onNavigate('discover')}>Start Discovering</Button>
        </div>
      </section>
    </>
  );
}

function DiscoverPage({ onNavigate }) {
  const EXAMPLES = [
    'vegan skincare micro-influencers in Berlin with Gen-Z audience',
    'tech reviewers in India with 50k+ YouTube subs who speak Hindi',
    'dog-parent creators on TikTok, US-based, 10k–100k followers',
    'sustainable fashion creators with engagement rate above 5%',
  ];
  const [query, setQuery] = useState(EXAMPLES[0]);
  const [ran, setRan] = useState(false);

  const run = () => setRan(true);

  return (
    <>
      <PageHeader icon="🔍" title="Discover Influencers" sub="Ask in plain English. The Discovery Agent handles the rest." />
      <div className="sk-page-body">
        <div className="sk-panel">
          <div className="sk-row" style={{ gap: 16 }}>
            <div style={{ flex: 4 }}>
              <Input label="What kind of creators are you looking for?" value={query} onChange={setQuery} type="textarea" />
            </div>
            <div style={{ flex: 1, minWidth: 120 }}>
              <NumberField label="Top K" value={10} min={1} max={50} />
            </div>
          </div>
          <details className="sk-expander">
            <summary>💡 Example briefs</summary>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 10 }}>
              {EXAMPLES.map((e) => (
                <button key={e} className="sk-example-btn" onClick={() => setQuery(e)}>{e}</button>
              ))}
            </div>
          </details>
          <div style={{ marginTop: 16 }}>
            <Button variant="primary" icon="rocket" onClick={run}>Run Discovery Agent</Button>
          </div>
        </div>

        {ran && (
          <>
            <div className="sk-info-banner">
              Returned 4 creators matching <b>"{query}"</b>. Ranked by semantic similarity and re-scored by the LLM.
            </div>
            <div className="sk-creator-list">
              {CREATORS.map((c, i) => (
                <CreatorCard key={c.id}
                  creator={c}
                  score={[0.91, 0.86, 0.82, 0.78][i]}
                  reason={[
                    'Strong Gen-Z audience in IN; clean-beauty niche matches your brief verbatim.',
                    'Consistently engaged tech audience in Berlin; EU delivery-friendly.',
                    'High-retention food reels with on-brief audience demographics.',
                    'Trust-leading pet creator with above-average engagement.',
                  ][i]}
                  onView={() => onNavigate('campaigns')}
                  onOutreach={() => onNavigate('outreach')}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </>
  );
}

function FilterPage({ onNavigate }) {
  const [platforms, setPlatforms] = useState(['instagram']);
  const [niches, setNiches] = useState([]);
  const [ran, setRan] = useState(false);
  return (
    <>
      <PageHeader icon="🎯" title="Filter & Refine" sub="Structured filters backed by Pinecone metadata + a post-filter pass." />
      <div className="sk-page-body">
        <details className="sk-panel" open>
          <summary className="sk-panel-title">🎛️ Filters</summary>
          <Input label="Natural-language hint (optional)" placeholder="e.g. 'engaged foodie creators with strong storytelling'" type="textarea" />
          <div className="sk-grid-3">
            <ChipSelect label="Platforms" options={['instagram','tiktok','youtube','facebook','twitter']} value={platforms} onChange={setPlatforms} />
            <ChipSelect label="Niches" options={['beauty','fashion','fitness','food','travel','tech','lifestyle','pets']} value={niches} onChange={setNiches} />
            <ChipSelect label="Languages" options={['en','hi','es','fr','de']} value={[]} onChange={() => {}} />
          </div>
          <div className="sk-grid-3">
            <NumberField label="Min followers" value={1000} step={1000} />
            <NumberField label="Max followers" value={500000} step={1000} />
            <NumberField label="Min engagement" value={0.0} step={0.005} />
          </div>
          <div className="sk-row" style={{ gap: 20, marginTop: 10 }}>
            <Checkbox label="Verified only" />
            <Checkbox label="Open to collabs only" checked />
          </div>
          <div style={{ marginTop: 16 }}>
            <Button variant="primary" icon="target" onClick={() => setRan(true)}>Run Filtering Agent</Button>
          </div>
        </details>

        {ran ? (
          <div className="sk-creator-list">
            {CREATORS.slice(0, 3).map((c, i) => (
              <CreatorCard key={c.id} creator={c} score={[0.88, 0.83, 0.79][i]}
                reason="Passes all hard filters; boosted by semantic match against the brief."
                onView={() => onNavigate('campaigns')} onOutreach={() => onNavigate('outreach')} />
            ))}
          </div>
        ) : (
          <div className="sk-info-banner">Set your filters above, then click <b>Run Filtering Agent</b>.</div>
        )}
      </div>
    </>
  );
}

function OutreachPage() {
  const [creatorId, setCreatorId] = useState('c_001');
  const [brand, setBrand] = useState('AuraGlow');
  const [brief, setBrief] = useState("We're launching a new clean-beauty serum targeting Gen-Z. Looking for a creator to film 1 reel + 3 stories within 2 weeks. Budget flexible, open to usage-rights add-on.");
  const [draft, setDraft] = useState(null);
  const creator = CREATORS.find((c) => c.id === creatorId);
  const generate = () => setDraft({
    subject: `A clean-beauty collab with ${brand} — built for your audience`,
    body: `Hi ${creator?.display_name?.replace('@','') || 'there'},\n\nI've been following your work on ${creator?.niches?.[0] || 'beauty'} content and your take on cruelty-free skincare resonates hard with what we're launching at ${brand}. \n\nWe're rolling out a new clean-beauty serum for Gen-Z and would love to have you film 1 reel + 3 stories within 2 weeks. Budget is flexible, and we're open to a usage-rights add-on if that fits your model.\n\nWould love to hear if this lands — happy to share more specifics.\n\n— ${brand} team`
  });

  return (
    <>
      <PageHeader icon="✉️" title="AI Outreach" sub="Draft a personalized first-touch message in 5 seconds." />
      <div className="sk-page-body">
        <div className="sk-panel">
          <Input label="Creator ID" value={creatorId} onChange={setCreatorId} hint="Grab this from any creator card in Discovery or Filter & Refine." />
          {creator && (
            <div className="sk-creator-preview">
              <b>{creator.display_name}</b> · {creator.country}
              <div className="sk-caption">{creator.bio}</div>
            </div>
          )}
          <Input label="Brand name" value={brand} onChange={setBrand} />
          <Input label="Campaign brief" type="textarea" value={brief} onChange={setBrief} />
          <div className="sk-grid-2">
            <Select label="Tone" options={['friendly-professional','casual','formal']} value="friendly-professional" />
            <Select label="Channel" options={['email','instagram_dm','tiktok_dm']} value="email" />
          </div>
          <div style={{ marginTop: 14 }}>
            <Button variant="primary" icon="sparkles" onClick={generate}>Draft message</Button>
          </div>
        </div>
        {draft && (
          <div className="sk-panel" style={{ background: 'var(--bg-alt)' }}>
            <div className="sk-success">✨ Draft ready</div>
            <div className="sk-label-field">Subject</div>
            <div className="sk-draft-subject">{draft.subject}</div>
            <div className="sk-label-field">Body</div>
            <pre className="sk-draft-body">{draft.body}</pre>
            <div className="sk-caption">Tip: Edit before sending, and always A/B test subject lines.</div>
          </div>
        )}
      </div>
    </>
  );
}

function CampaignsPage() {
  const [selected, setSelected] = useState(null);
  return (
    <>
      <PageHeader icon="📊" title="Campaigns & Creator Directory" sub="Browse onboarded creators, grab their contact info, plan outreach." />
      <div className="sk-page-body">
        <div className="sk-tabs">
          <div className="sk-tab is-active">Directory</div>
          <div className="sk-tab">Campaign tracker (coming soon)</div>
        </div>
        <div className="sk-panel" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="sk-table">
            <thead><tr><th>Name</th><th>Country</th><th>Niches</th><th>Followers</th><th>Engagement</th><th>IG</th></tr></thead>
            <tbody>
              {CREATORS.map((c) => (
                <tr key={c.id} onClick={() => setSelected(c)} className={selected?.id === c.id ? 'is-selected' : ''}>
                  <td><b>{c.display_name}</b></td>
                  <td>{c.country}</td>
                  <td>{c.niches.join(', ')}</td>
                  <td>{c.total_followers.toLocaleString()}</td>
                  <td>{(c.avg_engagement_rate*100).toFixed(2)}%</td>
                  <td>{c.handles.instagram || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {selected && (
          <div className="sk-panel">
            <h3>{selected.display_name}</h3>
            <div><b>Email:</b> {selected.email || '—'}</div>
            <div style={{ marginTop: 8 }}><b>Handles:</b></div>
            <pre className="sk-code">{JSON.stringify(selected.handles, null, 2)}</pre>
            <Button variant="primary" icon="mail" onClick={() => window.__nav('outreach')}>Draft outreach to this creator</Button>
          </div>
        )}
      </div>
    </>
  );
}

function OnboardingPage() {
  const [niches, setNiches] = useState([]);
  const [consent, setConsent] = useState(false);
  const [done, setDone] = useState(false);
  return (
    <>
      <PageHeader icon="🎤" title="Join Skout as a Creator" sub="Share where brands can find you. Your profile becomes discoverable to vetted brands looking for collaborations." />
      <div className="sk-page-body">
        <div className="sk-panel">
          <h3>Basics</h3>
          <div className="sk-grid-3">
            <Input label="Full name" required placeholder="Priya Sharma" />
            <Input label="Display name" placeholder="@priyastyles" />
            <Input label="Email" required placeholder="priya@example.com" />
          </div>
          <h3 style={{ marginTop: 18 }}>Your socials <span className="sk-caption" style={{ fontWeight: 400 }}>At least one is required.</span></h3>
          <div className="sk-grid-2">
            <Input label="Instagram handle" placeholder="priyastyles" />
            <NumberField label="Instagram followers" value={0} step={1000} />
            <Input label="TikTok handle" />
            <NumberField label="TikTok followers" value={0} step={1000} />
          </div>
          <h3 style={{ marginTop: 18 }}>Niche & audience</h3>
          <ChipSelect label="Niches *" value={niches} onChange={setNiches}
            options={['beauty','fashion','fitness','food','travel','tech','parenting','education','business','lifestyle','sustainability','pets']} />
          <h3 style={{ marginTop: 18 }}>Engagement & rates</h3>
          <div className="sk-grid-3">
            <NumberField label="Avg engagement (0–1)" value={0.035} step={0.001} />
            <NumberField label="Avg views per post" value={0} step={100} />
            <NumberField label="Min rate (USD)" value={0} step={50} />
          </div>
          <Input type="textarea" label="Short bio" placeholder="Toronto-based beauty creator focusing on clean, cruelty-free skincare." />
          <div style={{ marginTop: 14 }}>
            <Checkbox label="I consent to Skout storing this profile and making it discoverable to brands." checked={consent} onChange={setConsent} />
          </div>
          <div style={{ marginTop: 18 }}>
            <Button variant="primary" icon="sparkles" onClick={() => setDone(true)}>Create my creator profile</Button>
          </div>
        </div>
        {done && (
          <div className="sk-success-panel">
            ✨ Profile created! Your creator ID: <code>c_new_891</code>
          </div>
        )}
      </div>
    </>
  );
}

// --- App shell ---
function App() {
  const [page, setPage] = useState(() => location.hash.replace('#', '') || 'home');
  useEffect(() => {
    window.__nav = (p) => { setPage(p); location.hash = p; window.scrollTo({ top: 0, behavior: 'smooth' }); };
    const h = () => setPage(location.hash.replace('#', '') || 'home');
    addEventListener('hashchange', h);
    return () => removeEventListener('hashchange', h);
  }, []);
  const nav = (p) => window.__nav(p);
  const pages = {
    home: <HomePage onNavigate={nav} />,
    mission: <HomePage onNavigate={nav} />,
    discover: <DiscoverPage onNavigate={nav} />,
    filter: <FilterPage onNavigate={nav} />,
    outreach: <OutreachPage />,
    campaigns: <CampaignsPage />,
    onboarding: <OnboardingPage />,
  };
  return (
    <div data-screen-label={page}>
      <Navbar current={page} onNavigate={nav} />
      {pages[page] || pages.home}
      <Footer onNavigate={nav} />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
