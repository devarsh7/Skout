"""Skout Home — marketing site. Redirects logged-in users to their dashboard."""
from __future__ import annotations
import streamlit as st
from frontend.utils.session import restore_session
from frontend.utils.styles import (
    _P_CREATOR, _P_BUSINESS, _P_LOGIN, _P_CREATOR_DASHBOARD,
    inject_css, render_navbar,
)

inject_css()
restore_session()

user = st.session_state.get("user")
role = user.get("role") if user else None

if role == "creator":
    st.switch_page(_P_CREATOR_DASHBOARD)
    st.stop()
elif role == "business":
    st.switch_page("pages/Business_Dashboard.py")
    st.stop()

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
:root{--ind-50:#EEF2FF;--ind-100:#E0E7FF;--ind-200:#C7D2FE;--ind-600:#4F46E5;--ind-700:#4338CA;--vio-500:#8B5CF6;--vio-600:#7C3AED;--mk-navy:#1E1B4B;--mk-muted:#6B7280;--mk-sub:#9CA3AF;}
body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#FAFAFE !important;font-family:'Inter',sans-serif !important;}
[data-testid="stVerticalBlock"]{gap:0 !important;}
.stMarkdown{margin:0 !important;padding:0 !important;}
.mk-hero{padding:8rem 2rem 4rem;text-align:center;position:relative;overflow:hidden;background:linear-gradient(165deg,#F0EFFF 0%,#EEF0FF 45%,#F5F3FF 100%);}
.blob{position:absolute;border-radius:50%;pointer-events:none;filter:blur(50px);}
.blob-1{width:650px;height:650px;top:-200px;right:-130px;background:rgba(99,102,241,.2);}
.blob-2{width:500px;height:500px;bottom:-160px;left:-100px;background:rgba(139,92,246,.15);}
.blob-3{width:280px;height:280px;top:35%;left:18%;background:rgba(167,139,250,.1);}
.mk-badge{display:inline-flex;align-items:center;gap:8px;background:#fff;border:1.5px solid var(--ind-200);color:var(--ind-600);font-weight:700;font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;padding:7px 18px;border-radius:999px;margin-bottom:1.75rem;box-shadow:0 3px 10px rgba(79,70,229,.12);}
.mk-h1{font-family:'Inter',sans-serif;font-size:clamp(2.8rem,6.5vw,5.2rem);font-weight:900;line-height:1.04;letter-spacing:-.045em;color:var(--mk-navy);margin:0 auto .9rem;max-width:840px;}
.mk-grad{background:linear-gradient(135deg,var(--ind-600) 20%,var(--vio-500) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.mk-sub{font-size:clamp(1rem,2vw,1.18rem);color:var(--mk-muted);line-height:1.82;max-width:560px;margin:0 auto 1.25rem;}
.mk-trust{font-size:13.5px;color:var(--mk-sub);font-weight:500;margin-top:2rem;display:flex;align-items:center;justify-content:center;gap:8px;}
[data-testid="stHorizontalBlock"]:has(.mk-hero-ctas){background:transparent !important;border:none !important;padding:2rem 0 0 !important;justify-content:center !important;gap:12px !important;max-width:480px;margin:0 auto !important;}
[data-testid="stHorizontalBlock"]:has(.mk-hero-ctas) [data-testid="stColumn"]{padding:0 6px !important;flex:0 0 auto !important;}
.mk-cta-pri a[data-testid="stPageLink-NavLink"]{display:inline-flex !important;align-items:center !important;width:fit-content !important;background:linear-gradient(135deg,var(--ind-600),var(--vio-600)) !important;color:#fff !important;font-weight:800 !important;font-size:15px !important;padding:13px 30px !important;border-radius:999px !important;border:none !important;box-shadow:0 6px 22px rgba(79,70,229,.38) !important;transition:all .24s cubic-bezier(.34,1.56,.64,1) !important;white-space:nowrap !important;}
.mk-cta-pri a[data-testid="stPageLink-NavLink"]:hover{transform:scale(1.05) translateY(-2px) !important;box-shadow:0 12px 32px rgba(79,70,229,.48) !important;}
.mk-cta-sec a[data-testid="stPageLink-NavLink"]{display:inline-flex !important;align-items:center !important;width:fit-content !important;background:#fff !important;color:var(--ind-600) !important;border:1.5px solid var(--ind-200) !important;font-weight:700 !important;font-size:14.5px !important;padding:12px 28px !important;border-radius:999px !important;box-shadow:0 2px 8px rgba(79,70,229,.08) !important;transition:all .24s cubic-bezier(.34,1.56,.64,1) !important;white-space:nowrap !important;}
.mk-cta-sec a[data-testid="stPageLink-NavLink"]:hover{border-color:var(--ind-600) !important;transform:scale(1.04) !important;box-shadow:0 6px 18px rgba(79,70,229,.18) !important;}
.mk-section{padding:5.5rem 2rem;}
.mk-section-tint{padding:5.5rem 2rem;background:var(--ind-50);}
.mk-lbl{font-size:11px;font-weight:800;letter-spacing:.15em;text-transform:uppercase;color:var(--ind-600);display:block;text-align:center;margin-bottom:.55rem;}
.mk-h2{font-family:'Inter',sans-serif;font-size:clamp(2rem,4vw,2.9rem);font-weight:800;color:var(--mk-navy);text-align:center;letter-spacing:-.03em;margin:0 auto .75rem;max-width:640px;}
.mk-h2-sub{font-size:1rem;color:var(--mk-muted);line-height:1.82;text-align:center;max-width:520px;margin:0 auto 3.5rem;}
.mk-steps{display:grid;grid-template-columns:1fr 40px 1fr 40px 1fr;align-items:center;max-width:900px;margin:0 auto;}
.mk-step{background:#fff;border:1.5px solid var(--ind-100);border-radius:22px;padding:2.25rem 1.75rem;text-align:center;box-shadow:0 2px 14px rgba(79,70,229,.05);transition:transform .28s ease,box-shadow .28s ease;}
.mk-step:hover{transform:translateY(-7px);box-shadow:0 16px 44px rgba(79,70,229,.14);}
.mk-step-icon{display:inline-flex;align-items:center;justify-content:center;width:58px;height:58px;border-radius:16px;background:linear-gradient(135deg,var(--ind-600),var(--vio-500));font-size:26px;margin-bottom:1.25rem;box-shadow:0 5px 16px rgba(79,70,229,.3);}
.mk-step-n{font-size:10px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--ind-600);margin-bottom:.4rem;}
.mk-step-title{font-weight:800;font-size:1.05rem;color:var(--mk-navy);margin-bottom:.5rem;}
.mk-step-desc{font-size:.88rem;color:var(--mk-muted);line-height:1.75;}
.mk-arrow{text-align:center;font-size:1.6rem;color:var(--ind-200);}
.mk-feat-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:940px;margin:0 auto;}
.mk-feat-panel{border-radius:22px;padding:2.5rem 2.25rem;border:1.5px solid var(--ind-100);}
.mk-feat-panel.cr{background:linear-gradient(155deg,#EEF2FF,#F5F3FF);}
.mk-feat-panel.biz{background:linear-gradient(155deg,#F3F0FF,#EDE9FE);border-color:#DDD6FE;}
.mk-feat-head{font-size:1.12rem;font-weight:800;color:var(--mk-navy);display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;}
.mk-fi{display:flex;align-items:flex-start;gap:13px;margin-bottom:1.1rem;}
.mk-fi-icon{flex-shrink:0;width:34px;height:34px;border-radius:9px;margin-top:1px;background:linear-gradient(135deg,var(--ind-600),var(--vio-500));display:flex;align-items:center;justify-content:center;font-size:15px;}
.mk-fi b{display:block;font-size:.9rem;font-weight:700;color:var(--mk-navy);margin-bottom:1px;}
.mk-fi small{font-size:.82rem;color:var(--mk-muted);line-height:1.6;}
.mk-stats-strip{display:flex;justify-content:center;flex-wrap:wrap;background:linear-gradient(135deg,var(--ind-700),var(--vio-600));border-radius:22px;padding:3rem 1.5rem;max-width:840px;margin:0 auto 4.5rem;box-shadow:0 14px 44px rgba(79,70,229,.32);}
.mk-stat{flex:1;min-width:150px;text-align:center;padding:.5rem 1rem;}
.mk-stat+.mk-stat{border-left:1px solid rgba(255,255,255,.15);}
.mk-stat-v{font-size:2.6rem;font-weight:900;color:#fff;line-height:1;display:block;letter-spacing:-.04em;}
.mk-stat-l{font-size:.82rem;color:rgba(255,255,255,.68);margin-top:.4rem;font-weight:500;}
.mk-tgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;max-width:940px;margin:0 auto;}
.mk-tc{background:#fff;border:1.5px solid var(--ind-100);border-radius:18px;padding:1.75rem;box-shadow:0 2px 10px rgba(79,70,229,.05);transition:transform .2s;}
.mk-tc:hover{transform:translateY(-4px);}
.mk-t-stars{color:#FBBF24;margin-bottom:.7rem;font-size:14px;letter-spacing:1px;}
.mk-t-q{font-size:.88rem;color:#4B5563;line-height:1.78;margin-bottom:1.2rem;font-style:italic;}
.mk-t-auth{display:flex;align-items:center;gap:10px;}
.mk-t-av{width:40px;height:40px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:18px;}
.mk-t-name{font-weight:700;font-size:.88rem;color:var(--mk-navy);}
.mk-t-role{font-size:.78rem;color:var(--mk-sub);}
.mk-as-seen{text-align:center;font-size:.75rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#D1D5DB;margin:3.5rem 0 1.25rem;}
.mk-logos{display:flex;justify-content:center;flex-wrap:wrap;gap:2.5rem;opacity:.28;}
.mk-logo-pl{font-weight:800;font-size:1.1rem;color:#6B7280;letter-spacing:-.02em;}
.mk-faq-wrap{max-width:700px;margin:0 auto;}
details.mk-faq{background:#fff;border:1.5px solid var(--ind-100);border-radius:14px;margin-bottom:10px;transition:box-shadow .2s;}
details.mk-faq:hover,details.mk-faq[open]{box-shadow:0 4px 18px rgba(79,70,229,.08);}
details.mk-faq summary{padding:1.1rem 1.5rem;font-weight:700;font-size:.94rem;color:var(--mk-navy);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;}
details.mk-faq summary::-webkit-details-marker{display:none;}
details.mk-faq summary::after{content:'＋';font-size:1.1rem;color:var(--ind-600);flex-shrink:0;margin-left:.75rem;}
details.mk-faq[open] summary::after{content:'−';}
details.mk-faq[open] summary{color:var(--ind-600);border-bottom:1px solid var(--ind-100);padding-bottom:1rem;}
.mk-faq-body{padding:.9rem 1.5rem 1.1rem;font-size:.88rem;color:var(--mk-muted);line-height:1.82;}
/* ── CTA WAITLIST CARD ── */
[data-testid="stHorizontalBlock"]:has(.wl-anchor){
  background:linear-gradient(145deg,#EDE9FE 0%,#DDD6FE 100%) !important;
  border-radius:24px !important;max-width:520px !important;
  margin:5rem auto !important;padding:3rem 2.5rem 2.5rem !important;
  box-shadow:0 8px 32px rgba(109,40,217,.12) !important;border:1.5px solid #C4B5FD !important;
}
[data-testid="stHorizontalBlock"]:has(.wl-anchor) [data-testid="stColumn"]{background:transparent !important;padding:0 !important;}
[data-testid="stHorizontalBlock"]:has(.wl-anchor) [data-testid="stVerticalBlock"]{gap:.8rem !important;background:transparent !important;}
[data-testid="stHorizontalBlock"]:has(.wl-anchor) [data-testid="stForm"]{background:transparent !important;border:none !important;padding:0 !important;box-shadow:none !important;}
.wl-headline{font-family:'Inter',sans-serif;font-size:clamp(1.7rem,3.5vw,2.4rem);font-weight:900;color:#1E1B4B;line-height:1.12;text-align:center;margin-bottom:.4rem;}
.wl-sub{font-size:.95rem;color:#6B7280;line-height:1.65;text-align:center;}
.wl-footnote{font-size:11.5px;color:#9CA3AF;text-align:center;font-style:italic;}
/* Pill role toggle */
[data-testid="stHorizontalBlock"]:has(.wl-anchor) .stRadio>label{display:none !important;}
[data-testid="stHorizontalBlock"]:has(.wl-anchor) .stRadio [data-baseweb="radio-group"],
[data-testid="stHorizontalBlock"]:has(.wl-anchor) .stRadio [data-testid="stHorizontalRadioOptions"]{
  background:#C4B5FD !important;border-radius:999px !important;
  padding:5px !important;width:100% !important;display:flex !important;gap:0 !important;
}
[data-testid="stHorizontalBlock"]:has(.wl-anchor) .stRadio [data-baseweb="radio-group"] label,
[data-testid="stHorizontalBlock"]:has(.wl-anchor) .stRadio [data-testid="stHorizontalRadioOptions"] label{
  flex:1 !important;justify-content:center !important;border-radius:999px !important;
  padding:10px 16px !important;cursor:pointer !important;transition:background .18s !important;
}
[data-testid="stHorizontalBlock"]:has(.wl-anchor) .stRadio [data-baseweb="radio-group"] label:has(input:checked),
[data-testid="stHorizontalBlock"]:has(.wl-anchor) .stRadio [data-testid="stHorizontalRadioOptions"] label:has(input:checked){background:#fff !important;box-shadow:0 2px 8px rgba(109,40,217,.15) !important;}
[data-testid="stHorizontalBlock"]:has(.wl-anchor) .stRadio [data-baseweb="radio"]{display:none !important;}
[data-testid="stHorizontalBlock"]:has(.wl-anchor) .stRadio [data-testid="stMarkdownContainer"] p,
[data-testid="stHorizontalBlock"]:has(.wl-anchor) .stRadio [data-testid="stMarkdownContainer"] span,
[data-testid="stHorizontalBlock"]:has(.wl-anchor) .stRadio [data-testid="stMarkdownContainer"]{
  color:#1E1B4B !important;font-weight:700 !important;font-size:14px !important;
}
/* Email input */
[data-testid="stHorizontalBlock"]:has(.wl-anchor) input{
  background:rgba(255,255,255,.96) !important;border:none !important;
  border-radius:999px !important;color:#1E1B4B !important;
  font-size:15px !important;padding-left:22px !important;
}
[data-testid="stHorizontalBlock"]:has(.wl-anchor) input::placeholder{color:#9CA3AF !important;}
/* Join button */
[data-testid="stHorizontalBlock"]:has(.wl-anchor) .stButton>button{
  background:#111827 !important;color:#fff !important;border:none !important;
  border-radius:999px !important;font-weight:700 !important;font-size:15px !important;
  box-shadow:none !important;transition:all .18s !important;
}
[data-testid="stHorizontalBlock"]:has(.wl-anchor) .stButton>button:hover{background:#000 !important;transform:translateY(-1px) !important;}
/* Success/warning inside the card */
[data-testid="stHorizontalBlock"]:has(.wl-anchor) .stAlert{border-radius:12px !important;}
/* ── FOOTER ── */
.mk-footer{background:#F5F4FF;border-top:1.5px solid var(--ind-100);padding:4rem 2rem 2rem;}
.mk-footer-inner{max-width:960px;margin:0;}
.mk-footer-grid{display:grid;grid-template-columns:2fr 1fr;gap:3rem;margin-bottom:2.5rem;}
.mk-footer-tagline{font-size:.84rem;color:var(--mk-muted);line-height:1.75;margin-top:.5rem;max-width:230px;}
.mk-fcol-title{font-weight:700;font-size:.8rem;color:var(--mk-navy);margin-bottom:.85rem;letter-spacing:.05em;text-transform:uppercase;}
.mk-flink{display:block;font-size:.82rem;color:var(--mk-muted);margin-bottom:.5rem;transition:color .15s;text-decoration:none;}
.mk-flink:hover{color:var(--ind-600);}
.mk-footer-hr{border:none;border-top:1px solid var(--ind-100);margin:0 0 1.5rem;}
.mk-footer-btm{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;font-size:12px;color:var(--mk-sub);}
.mk-socials{display:flex;gap:14px;}
.mk-soc{font-size:16px;cursor:pointer;opacity:.5;transition:opacity .15s;display:inline-block;color:var(--mk-muted);}
.mk-soc:hover{opacity:1;color:var(--ind-600);}
</style>""", unsafe_allow_html=True)

render_navbar()

st.markdown("""
<div class="mk-hero">
  <div class="blob blob-1"></div><div class="blob blob-2"></div><div class="blob blob-3"></div>
  <span class="mk-badge">🦉 Early Access &nbsp;·&nbsp; Launching 2026</span>
  <h1 class="mk-h1">Be found <span class="mk-grad">before</span><br>you're famous.</h1>
  <p class="mk-sub">Skout connects local micro-creators (500–50K followers) with small businesses across Canada &amp; the USA — no follower gatekeeping, no big-agency fees.</p>
</div>""", unsafe_allow_html=True)


st.markdown("""
<div class="mk-section">
  <span class="mk-lbl">How it works</span>
  <h2 class="mk-h2">From sign-up to real gigs in 3 steps.</h2>
  <p class="mk-h2-sub">No agencies, no cold DMs. Just a platform that gets out of your way.</p>
  <div class="mk-steps">
    <div class="mk-step"><div class="mk-step-icon">✍️</div><div class="mk-step-n">Step 01</div><div class="mk-step-title">Create your profile</div><p class="mk-step-desc">Share your handles, niche, audience data and rates. Takes under two minutes — instantly indexed.</p></div>
    <div class="mk-arrow">→</div>
    <div class="mk-step"><div class="mk-step-icon">📍</div><div class="mk-step-n">Step 02</div><div class="mk-step-title">Get discovered locally</div><p class="mk-step-desc">Businesses search in plain English. Our AI surfaces the right creators — you included.</p></div>
    <div class="mk-arrow">→</div>
    <div class="mk-step"><div class="mk-step-icon">💸</div><div class="mk-step-n">Step 03</div><div class="mk-step-title">Collaborate &amp; get paid</div><p class="mk-step-desc">Receive briefs, negotiate terms, deliver content, and get paid — all inside Skout.</p></div>
  </div>
</div>""", unsafe_allow_html=True)

st.markdown("""
<div class="mk-section-tint">
  <span class="mk-lbl">Why Skout</span>
  <h2 class="mk-h2">Built for both sides of the deal.</h2>
  <p class="mk-h2-sub">Whether you're posting or paying, Skout removes the friction.</p>
  <div class="mk-feat-grid">
    <div class="mk-feat-panel cr">
      <div class="mk-feat-head"><span>🎤</span> For Creators</div>
      <div class="mk-fi"><div class="mk-fi-icon">📍</div><div><b>Local visibility</b><small>Get discovered by businesses in your city — not just global brands chasing millions of followers.</small></div></div>
      <div class="mk-fi"><div class="mk-fi-icon">💰</div><div><b>Paid gigs, not gifting</b><small>Skout promotes cash-first campaigns. Know your worth and get compensated for it.</small></div></div>
      <div class="mk-fi"><div class="mk-fi-icon">🚫</div><div><b>No follower gatekeeping</b><small>500 followers or 50K — engagement and niche fit matter more than vanity numbers.</small></div></div>
      <div class="mk-fi"><div class="mk-fi-icon">🗂️</div><div><b>Portfolio building</b><small>Every campaign becomes a verified case study on your Skout profile.</small></div></div>
    </div>
    <div class="mk-feat-panel biz">
      <div class="mk-feat-head"><span>💼</span> For Businesses</div>
      <div class="mk-fi"><div class="mk-fi-icon">🎯</div><div><b>Authentic local voices</b><small>Find creators who genuinely live in your city and resonate with your target customers.</small></div></div>
      <div class="mk-fi"><div class="mk-fi-icon">💵</div><div><b>Affordable campaigns</b><small>Micro-creator rates are a fraction of macro costs — with higher engagement ROI.</small></div></div>
      <div class="mk-fi"><div class="mk-fi-icon">✅</div><div><b>Vetted creators</b><small>Browse real audience stats, past work, and engagement rates before reaching out.</small></div></div>
      <div class="mk-fi"><div class="mk-fi-icon">📦</div><div><b>Simple booking</b><small>Post a brief, review applicants, approve, pay. One clean dashboard — no spreadsheets.</small></div></div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ── SOCIAL PROOF — commented out until we have real data ─────────────────────
# st.markdown("""
# <div class="mk-section">
#   <span class="mk-lbl">Social proof</span>
#   <h2 class="mk-h2">Creators and businesses are already waiting.</h2>
#   <p class="mk-h2-sub">Join thousands who signed up before launch day.</p>
#   <div class="mk-stats-strip">
#     <div class="mk-stat"><span class="mk-stat-v">10K+</span><div class="mk-stat-l">Creators on waitlist</div></div>
#     <div class="mk-stat"><span class="mk-stat-v">500+</span><div class="mk-stat-l">SMBs registered</div></div>
#     <div class="mk-stat"><span class="mk-stat-v">50+</span><div class="mk-stat-l">Cities covered</div></div>
#     <div class="mk-stat"><span class="mk-stat-v">2</span><div class="mk-stat-l">Countries 🇨🇦 🇺🇸</div></div>
#   </div>
#   <div class="mk-tgrid">
#     <div class="mk-tc">...testimonial 1...</div>
#     <div class="mk-tc">...testimonial 2...</div>
#     <div class="mk-tc">...testimonial 3...</div>
#   </div>
# </div>""", unsafe_allow_html=True)

st.markdown("""
<div class="mk-section-tint">
  <span class="mk-lbl">FAQ</span>
  <h2 class="mk-h2">Answers to the obvious questions.</h2>
  <p class="mk-h2-sub">Still curious? Reach us at hello@skout.ai</p>
  <div class="mk-faq-wrap">
    <details class="mk-faq"><summary>Who is Skout for?</summary><div class="mk-faq-body">Skout is built for <strong>micro-creators</strong> with 500–50K followers on any platform and <strong>small-to-medium businesses</strong> looking for authentic local partnerships without agency overhead.</div></details>
    <details class="mk-faq"><summary>Is there a minimum follower count?</summary><div class="mk-faq-body">Nope. A hyper-engaged local creator with 800 followers can outperform a disengaged macro with 200K. Skout evaluates engagement rate, niche relevance, and audience quality — not raw follower counts.</div></details>
    <details class="mk-faq"><summary>How much does Skout cost?</summary><div class="mk-faq-body">Creator profiles are <strong>always free</strong>. Business accounts will have a freemium tier at launch. Premium plans will be priced affordably for SMBs.</div></details>
    <details class="mk-faq"><summary>When are you launching and which cities?</summary><div class="mk-faq-body">We're targeting a <strong>2026 public launch</strong>. Early access rolls out city by city across Canada (Toronto, Vancouver, Montreal, Calgary) and the USA (New York, LA, Chicago, Austin).</div></details>
    <!-- <details class="mk-faq"><summary>How do payments work?</summary><div class="mk-faq-body">Businesses post campaign budgets upfront. Once a creator delivers approved content, payment is released via Skout's secure escrow. Creators get paid via Stripe — no net-60 invoicing nightmares.</div></details> -->
    <details class="mk-faq"><summary>Which platforms are supported?</summary><div class="mk-faq-body">At launch: Instagram, TikTok, YouTube, and Twitter/X. Pinterest, Twitch, and LinkedIn are on the roadmap.</div></details>
    <details class="mk-faq"><summary>How are creators vetted?</summary><div class="mk-faq-body">Creators connect social accounts via OAuth so we verify real follower counts and engagement. We also run basic identity verification and review all profiles before they appear in search.</div></details>
    <details class="mk-faq"><summary>How does the AI search work?</summary><div class="mk-faq-body">Businesses describe what they need in plain English — e.g. <em>"Toronto fitness creator, female, 5K–30K followers, posts about running."</em> Skout uses semantic embeddings to match profiles by relevance score, not keyword overlap.</div></details>
  </div>
</div>""", unsafe_allow_html=True)

with st.columns([1])[0]:
    st.markdown('<div class="wl-anchor"></div>', unsafe_allow_html=True)
    st.markdown('<p class="wl-headline">Get early access to Skout.</p>', unsafe_allow_html=True)
    st.markdown('<p class="wl-sub">Be first in line when we launch in your city. No spam, ever.</p>', unsafe_allow_html=True)
    with st.form("waitlist_form", clear_on_submit=True):
        wl_role  = st.radio("", ["I'm a Creator", "I'm a Business"], horizontal=True, label_visibility="collapsed")
        wl_email = st.text_input("", placeholder="you@email.com", label_visibility="collapsed")
        if st.form_submit_button("Join →", use_container_width=True):
            if wl_email:
                st.success("🎉 You're on the list! We'll reach out before launch.")
            else:
                st.warning("Please enter your email address.")
    st.markdown('<p class="wl-footnote">Launching city by city across CA &amp; US in 2026.</p>', unsafe_allow_html=True)

st.markdown("""
<div class="mk-footer">
  <div class="mk-footer-inner">
    <div class="mk-footer-grid">
      <div style="text-align:left">
        <img src="app/static/skout-logo.png" style="height:34px;width:auto;display:block;margin-left:0">
        <p class="mk-footer-tagline" style="text-align:left;margin-left:0">AI-powered influencer discovery for creators and businesses across 🇨🇦 &amp; 🇺🇸.</p>
      </div>
      <div>
        <div class="mk-fcol-title">Company</div>
        <a class="mk-flink" href="#">About</a>
        <a class="mk-flink" href="#">Blog</a>
        <a class="mk-flink" href="#">hello@skout.ai</a>
      </div>
    </div>
    <hr class="mk-footer-hr">
    <div class="mk-footer-btm">
      <span>© 2026 Skout Inc.</span>
      <div class="mk-socials"><span class="mk-soc">𝕏</span><span class="mk-soc">📸</span><span class="mk-soc">▶</span><span class="mk-soc">in</span></div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)
