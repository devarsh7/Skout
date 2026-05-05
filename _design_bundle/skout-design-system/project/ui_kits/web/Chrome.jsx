/* global React, Logo, Button */
const { useState } = React;

function Navbar({ current, onNavigate }) {
  const items = [
    { id: 'home', label: 'Home' },
    { id: 'mission', label: 'Our Mission' },
    { id: 'business', label: 'Join as Business' },
  ];
  return (
    <nav className="sk-navbar">
      <Logo />
      <div className="sk-nav-links">
        {items.map((it, i) =>
          it.sep ? (
            <span key={i} className="sk-nav-sep" />
          ) : (
            <a
              key={it.id}
              className={`sk-nav-link ${current === it.id ? 'is-active' : ''}`}
              onClick={(e) => { e.preventDefault(); onNavigate(it.id); }}
              href={`#${it.id}`}
            >
              {it.label}
            </a>
          )
        )}
        <a className="sk-nav-cta" onClick={(e) => { e.preventDefault(); onNavigate('onboarding'); }} href="#onboarding">
          Join as Creator
        </a>
      </div>
    </nav>
  );
}

function Footer({ onNavigate }) {
  return (
    <footer className="sk-footer">
      <div className="sk-footer-grid">
        <div>
          <div className="sk-footer-logo">
            <img src="../../assets/logo-skout-owl.svg" alt="" width="22" height="22" />
            <span>Skout<span className="sk-logo-dot">.</span></span>
          </div>
          <p className="sk-footer-tagline">
            AI-powered influencer discovery &amp; outreach. Find the right creators in plain English.
          </p>
        </div>
        <div>
          <span className="sk-footer-label">Pages</span>
          <a onClick={(e) => { e.preventDefault(); onNavigate('onboarding'); }} href="#">Creator Onboarding</a>
          <a onClick={(e) => { e.preventDefault(); onNavigate('discover'); }} href="#">Discover Influencers</a>
          <a onClick={(e) => { e.preventDefault(); onNavigate('filter'); }} href="#">Filter &amp; Refine</a>
        </div>
        <div>
          <span className="sk-footer-label">Tools</span>
          <a onClick={(e) => { e.preventDefault(); onNavigate('outreach'); }} href="#">AI Outreach</a>
          <a onClick={(e) => { e.preventDefault(); onNavigate('campaigns'); }} href="#">Campaigns</a>
        </div>
      </div>
      <div className="sk-footer-bottom">
        <span>© 2025 Skout</span>
        <span>LangChain · Pinecone · FastAPI · Streamlit</span>
      </div>
    </footer>
  );
}

Object.assign(window, { Navbar, Footer });
