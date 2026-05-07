"""
Shared styles, navbar, and footer helpers for Skout frontend.
Navigation: st.page_link() ONLY — guaranteed same-tab navigation.
Context CSS: :has() selectors scope topbar/footer styles without wrapper divs.
"""
from __future__ import annotations
import streamlit as st

_P_HOME               = "pages/Home.py"
_P_BUSINESS_DASHBOARD = "pages/Business_Dashboard.py"
_P_CREATOR   = "pages/1_\U0001f3a4_Creator_Onboarding.py"
_P_DISCOVER  = "pages/2_\U0001f50d_Discover_Influencers.py"
_P_FILTER    = "pages/3_\U0001f3af_Filter_and_Refine.py"
_P_OUTREACH  = "pages/4_✉️_AI_Outreach.py"
_P_CAMPAIGNS = "pages/5_\U0001f4ca_Campaigns.py"
_P_BUSINESS  = "pages/6_\U0001f4bc_Business_Onboarding.py"
_P_LOGIN          = "pages/7_\U0001f510_Login.py"
_P_SIGNUP         = "pages/8_\U0001f4dd_Sign_Up.py"
_P_MAP            = "pages/9_Creator_Map.py"
_P_AI_AGENT       = "pages/10_AI_Agent.py"
_P_CREATOR_MATCH  = "pages/11_Creator_Match.py"
_P_LOCAL_MARKET   = "pages/12_Local_Market.py"
_P_CREATOR_DASHBOARD  = "pages/creator/Dashboard.py"
_P_UPDATE_PROFILE     = "pages/creator/Update_Profile.py"

_NAV_CORE = [
    ("discover",  _P_DISCOVER,  "🔍 Discover"),
    ("filter",    _P_FILTER,    "🎯 Filter"),
    ("outreach",  _P_OUTREACH,  "✉️ Outreach"),
    ("campaigns", _P_CAMPAIGNS, "📊 Campaigns"),
]
_NAV_GUEST_EXTRA = [
    ("creator",  _P_CREATOR,  "🎤 Creator"),
    ("business", _P_BUSINESS, "💼 Business"),
]


def inject_css() -> None:
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&family=Open+Sans:wght@400;500;600;700&display=swap');

:root {
  --bg-page:#fff; --bg-alt:#F8FAFD;
  --blue-50:#EFF6FF; --blue-100:#DBEAFE;
  --blue-600:#2563EB; --blue-700:#1D4ED8;
  --green-600:#16a34a; --green-50:#f0fdf4;
  --navy:#0F172A; --muted:#64748B; --subtle:#94A3B8; --border:#E2E8F0;
  --shadow-sm:0 1px 3px rgba(15,23,42,.08);
  --shadow-blue:0 4px 16px rgba(37,99,235,.22);
  --shadow-blue-lg:0 8px 28px rgba(37,99,235,.32);
  --ring-blue:0 0 0 3px rgba(37,99,235,.15);
  --fd:'Poppins',-apple-system,sans-serif;
  --fb:'Open Sans',-apple-system,sans-serif;
}
*,*::before,*::after{box-sizing:border-box}
html,body{scroll-behavior:smooth}
a{text-decoration:none !important}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu,footer,
[data-testid="stHeader"],[data-testid="stDecoration"],
[data-testid="stSidebar"],[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],.stDeployButton,
section[data-testid="stSidebar"],div[data-testid="stSidebarContent"],
button[data-testid="baseButton-header"]{display:none !important;}

/* ── FULL-WIDTH ZERO-PADDING ── */
[data-testid="stAppViewContainer"]{padding:0 !important;margin:0 !important;background:var(--bg-page) !important;}
[data-testid="stMain"]{padding:0 !important;margin:0 !important;background:var(--bg-page) !important;}
.main .block-container,[data-testid="stMainBlockContainer"]{
  padding:0 !important;margin:0 !important;max-width:100% !important;padding-bottom:0 !important;
}
section[data-testid="stMain"]>div:first-child{padding-top:0 !important;}
div[data-testid="stAppViewBlockContainer"]{padding-top:0 !important;padding-bottom:0 !important;}

/* allow sticky to escape */
[data-testid="stAppViewContainer"],[data-testid="stMain"],
[data-testid="stMainBlockContainer"]{overflow:visible !important;}

/* ── FONTS ── */
body{font-family:var(--fb) !important;-webkit-font-smoothing:antialiased;color:var(--navy);}
h1,h2,h3,h4,h5,h6{font-family:var(--fd) !important;color:var(--navy) !important;font-weight:800;margin:0;letter-spacing:-.02em;}

/* ── REDUCE ELEMENT SPACING ── */
[data-testid="stVerticalBlock"]{gap:.35rem !important;}
.stMarkdown{margin-top:0 !important;margin-bottom:0 !important;}

/* ── STREAMLIT WIDGETS ── */
.stButton>button{
  background:var(--blue-600) !important;color:#fff !important;border:none !important;
  border-radius:8px !important;font-family:var(--fb) !important;font-weight:700 !important;
  font-size:.875rem !important;box-shadow:var(--shadow-blue) !important;
  transition:all .2s !important;cursor:pointer !important;
}
.stButton>button:hover{background:var(--blue-700) !important;box-shadow:var(--shadow-blue-lg) !important;transform:translateY(-1px) !important;}
.stTextInput input,.stTextArea textarea,.stNumberInput input{
  background:#fff !important;border:1.5px solid var(--border) !important;
  color:var(--navy) !important;border-radius:8px !important;font-family:var(--fb) !important;font-size:.875rem !important;
}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:var(--blue-600) !important;box-shadow:var(--ring-blue) !important;}
.stTextInput label,.stTextArea label,.stNumberInput label,
.stSelectbox label,.stMultiSelect label,.stCheckbox label,.stSlider label{
  font-family:var(--fb) !important;color:var(--navy) !important;font-weight:600 !important;font-size:.8rem !important;
}
.stSelectbox>div>div,.stMultiSelect>div>div{
  background:#fff !important;border:1.5px solid var(--border) !important;
  color:var(--navy) !important;border-radius:8px !important;font-family:var(--fb) !important;
}
[data-testid="stForm"]{
  background:#fff !important;border:1px solid var(--border) !important;
  border-radius:12px !important;padding:1.25rem !important;box-shadow:var(--shadow-sm) !important;
}
.stTabs [data-baseweb="tab-list"]{background:transparent !important;border-bottom:1px solid var(--border) !important;}
.stTabs [data-baseweb="tab"]{color:var(--muted) !important;font-family:var(--fb) !important;font-weight:500 !important;font-size:.875rem !important;}
.stTabs [aria-selected="true"]{color:var(--blue-600) !important;border-bottom:2px solid var(--blue-600) !important;background:var(--blue-50) !important;}
.streamlit-expanderHeader{background:var(--bg-alt) !important;border:1px solid var(--border) !important;border-radius:9px !important;font-family:var(--fb) !important;font-weight:600 !important;}
.stAlert{border-radius:10px !important;}

/* ── FOOTER — shared across all pages including home ── */
[data-testid="stHorizontalBlock"]:has(.footer-brand-marker){
  background:#fff !important;border-top:2px solid var(--border) !important;
  padding:1.5rem 1.75rem 1rem !important;margin-top:1rem !important;margin-bottom:0 !important;
}
[data-testid="stHorizontalBlock"]:has(.footer-brand-marker) [data-testid="stColumn"]{padding-right:1rem !important;}
[data-testid="stHorizontalBlock"]:has(.footer-brand-marker) a[data-testid="stPageLink-NavLink"]{
  font-family:var(--fb) !important;font-size:13px !important;font-weight:400 !important;
  color:var(--muted) !important;padding:2px 0 !important;
  background:none !important;border-radius:0 !important;display:block !important;transition:color .15s !important;
}
[data-testid="stHorizontalBlock"]:has(.footer-brand-marker) a[data-testid="stPageLink-NavLink"]:hover{color:var(--blue-600) !important;background:none !important;}
.footer-bottom-bar{background:#fff;border-top:1px solid var(--border);padding:.75rem 1.75rem .9rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;font-size:11.5px;color:var(--subtle);}
.footer-brand-name{font-family:var(--fd);font-weight:800;font-size:15px;color:var(--navy);margin-bottom:.3rem;}
.footer-tagline{font-size:12.5px;color:var(--muted);line-height:1.6;max-width:220px;margin:0;}
.footer-col-label{font-family:var(--fd);font-size:9.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--subtle);display:block;margin-bottom:.4rem;}

/* ── USER PILL (navbar / topbar) ── */
.sk-user-pill{
  display:inline-flex;align-items:center;gap:6px;
  background:var(--blue-50);border:1.5px solid var(--blue-100);color:var(--blue-700);
  font-family:var(--fb);font-size:13px;font-weight:700;
  padding:6px 14px;border-radius:999px;white-space:nowrap;
}
/* logout button — ghost style overriding global blue */
.sk-logout-wrap .stButton>button{
  background:transparent !important;color:var(--navy) !important;
  border:1.5px solid var(--border) !important;box-shadow:none !important;
  font-size:13px !important;font-weight:600 !important;padding:6px 14px !important;
}
.sk-logout-wrap .stButton>button:hover{
  background:var(--bg-alt) !important;border-color:var(--navy) !important;
  transform:none !important;box-shadow:none !important;
}
</style>
""", unsafe_allow_html=True)


def _logout() -> None:
    for k in ["user", "user_token"]:
        st.session_state.pop(k, None)
    st.rerun()


def render_navbar() -> None:
    """Home-page navbar — personalised when user is logged in."""
    user = st.session_state.get("user")

    if user:
        role     = user.get("role", "creator")
        username = user.get("username", "")
        icon     = "🎤" if role == "creator" else "💼"
        logo_col, spacer, action_col, pill_col, logout_col = st.columns([3, 2, 1.8, 2.2, 1.4])
        with logo_col:
            st.markdown('<div class="sk-home-logo"><img src="app/static/skout-logo.png" style="height:46px;width:auto;display:block;max-height:52px"></div>', unsafe_allow_html=True)
        with spacer:
            pass
        with action_col:
            st.markdown('<div class="sk-nav-discover">', unsafe_allow_html=True)
            if role == "creator":
                st.page_link(_P_DISCOVER, label="🔍 Discover")
            else:
                st.page_link(_P_CAMPAIGNS, label="📊 Campaigns")
            st.markdown('</div>', unsafe_allow_html=True)
        with pill_col:
            st.markdown(f'<div class="sk-user-pill">{icon} @{username}</div>', unsafe_allow_html=True)
        with logout_col:
            st.markdown('<div class="sk-logout-wrap">', unsafe_allow_html=True)
            if st.button("Log out", key="home_logout"):
                _logout()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
<style>
.sk-navbar{
  position:sticky;top:0;z-index:1000;
  background:rgba(255,255,255,.97);
  border-bottom:1px solid #E2E8F0;
  box-shadow:0 1px 8px rgba(15,23,42,.06);
  display:flex;align-items:center;
  padding:0 clamp(1.5rem,5vw,4rem);min-height:64px;
  font-family:'Inter','Open Sans',sans-serif;
}
.sk-navbar-spacer{flex:1;}
.sk-navbar-btns{display:flex;align-items:center;gap:8px;}
.sk-nb-creator{
  display:inline-flex;align-items:center;
  background:linear-gradient(135deg,rgba(99,102,241,.11),rgba(139,92,246,.14));
  color:#4F46E5 !important;text-decoration:none !important;
  border:1.5px solid rgba(99,102,241,.25);border-radius:999px;
  padding:8px 22px;font-size:13.5px;font-weight:700;
  box-shadow:0 4px 16px rgba(99,102,241,.12);
  transition:all .22s cubic-bezier(.34,1.56,.64,1);
  white-space:nowrap;letter-spacing:.01em;
}
.sk-nb-creator:hover{
  background:linear-gradient(135deg,rgba(99,102,241,.2),rgba(139,92,246,.26)) !important;
  border-color:rgba(99,102,241,.42) !important;
  box-shadow:0 8px 26px rgba(99,102,241,.2) !important;
  transform:scale(1.05) translateY(-1px);color:#4F46E5 !important;
}
.sk-nb-business{
  display:inline-flex;align-items:center;
  background:#fff;color:#4F46E5 !important;text-decoration:none !important;
  border:1.5px solid #E0E7FF;border-radius:999px;
  padding:8px 22px;font-size:13.5px;font-weight:700;
  box-shadow:0 2px 8px rgba(99,102,241,.06);
  transition:all .22s cubic-bezier(.34,1.56,.64,1);
  white-space:nowrap;letter-spacing:.01em;
}
.sk-nb-business:hover{
  border-color:#C7D2FE !important;
  box-shadow:0 6px 20px rgba(99,102,241,.13) !important;
  transform:scale(1.04) translateY(-1px);color:#4F46E5 !important;
}
.sk-nb-login{
  display:inline-flex;align-items:center;
  background:transparent;color:#9CA3AF !important;text-decoration:none !important;
  border:none;border-radius:999px;
  padding:8px 12px;font-size:13.5px;font-weight:600;
  transition:color .18s;white-space:nowrap;
}
.sk-nb-login:hover{color:#4F46E5 !important;}
</style>
<div class="sk-navbar">
  <img src="app/static/skout-logo.png" style="height:46px;width:auto;display:block">
  <div class="sk-navbar-spacer"></div>
  <div class="sk-navbar-btns">
    <a class="sk-nb-creator" href="/Creator_Onboarding" target="_self">Join as Creator</a>
    <a class="sk-nb-business" href="/Business_Onboarding" target="_self">Join as Business</a>
    <a class="sk-nb-login" href="/Login" target="_self">Login</a>
  </div>
</div>
""", unsafe_allow_html=True)


def inject_app_css() -> None:
    """App-shell CSS for inner pages."""
    st.markdown("""
<style>
/* ── ZERO TOP SPACE ── */
[data-testid="stMain"]{background:var(--bg-alt) !important;}
[data-testid="stMainBlockContainer"]{padding-top:0 !important;padding-bottom:0 !important;}
.block-container{padding-top:0 !important;padding-bottom:0 !important;max-width:100% !important;}
section[data-testid="stMain"]>div:first-child{padding-top:0 !important;}

/* ── TOPBAR via :has() ── */
[data-testid="stHorizontalBlock"]:has(.tb-logo-marker){
  background:#fff !important;
  border-bottom:1px solid var(--border) !important;
  padding:4px 1.75rem !important;
  min-height:52px !important;
  align-items:center !important;
  position:sticky !important;top:0 !important;z-index:999 !important;
  box-shadow:0 1px 6px rgba(15,23,42,.05) !important;
}
[data-testid="stHorizontalBlock"]:has(.tb-logo-marker) [data-testid="stColumn"]{
  display:flex !important;flex-direction:row !important;
  align-items:center !important;padding:0 2px !important;
}
[data-testid="stHorizontalBlock"]:has(.tb-logo-marker) .stMarkdown,
[data-testid="stHorizontalBlock"]:has(.tb-logo-marker) [data-testid="stMarkdownContainer"]{
  display:flex !important;align-items:center !important;
}
/* Logo */
.tb-logo-marker{
  display:flex !important;align-items:center !important;justify-content:flex-start !important;
  font-family:var(--fd);font-weight:800;font-size:15px;color:var(--navy);
  white-space:nowrap;padding-right:1rem;border-right:1px solid var(--border);
  margin-right:4px;letter-spacing:-.03em;
}
/* Page title area */
.tb-title-cell{
  font-family:var(--fd);font-weight:700;font-size:12.5px;color:var(--navy);
  display:flex;flex-direction:column;align-items:flex-end;line-height:1.3;
  border-left:1px solid var(--border);padding-left:1rem;width:100%;
}
.tb-title-sub{font-size:10px;color:var(--muted);font-weight:400;margin-top:1px;}
/* User badge inside topbar */
.tb-user-badge{
  font-family:var(--fb);font-size:12px;font-weight:700;color:var(--blue-700);
  background:var(--blue-50);border:1px solid var(--blue-100);
  border-radius:999px;padding:3px 10px;white-space:nowrap;
}

/* Nav links inside topbar */
[data-testid="stHorizontalBlock"]:has(.tb-logo-marker) a[data-testid="stPageLink-NavLink"]{
  font-family:var(--fb) !important;font-size:12px !important;font-weight:500 !important;
  color:var(--muted) !important;padding:5px 9px !important;border-radius:6px !important;
  white-space:nowrap !important;transition:all .15s !important;background:none !important;
}
[data-testid="stHorizontalBlock"]:has(.tb-logo-marker) a[data-testid="stPageLink-NavLink"]:hover{
  color:var(--navy) !important;background:var(--bg-alt) !important;
}
/* Active link */
[data-testid="stColumn"]:has(.tb-active-marker) a[data-testid="stPageLink-NavLink"]{
  color:var(--blue-600) !important;background:var(--blue-50) !important;font-weight:600 !important;
}

/* ── PAGE HERO ── */
.page-hero{
  background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 55%,#3b82f6 100%);
  padding:1.85rem 1.75rem 1.6rem;
}
.page-hero-badge{
  display:inline-flex;align-items:center;gap:5px;
  background:rgba(255,255,255,.15);color:rgba(255,255,255,.92);
  font-family:var(--fb);font-size:10.5px;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;
  padding:3px 10px;border-radius:99px;margin-bottom:.6rem;
}
.page-hero-title{
  font-family:var(--fd) !important;font-size:1.85rem !important;font-weight:800 !important;
  color:#fff !important;margin:0 0 .35rem !important;letter-spacing:-.03em !important;line-height:1.1 !important;
}
.page-hero-desc{
  font-size:13.5px;color:rgba(255,255,255,.72);line-height:1.6;margin:0;max-width:520px;
}

/* ── CONTENT ── */
.app-body{padding:1.25rem 1.75rem;}

/* ── CARDS ── */
.app-card{
  background:#fff;border:1px solid var(--border);border-radius:12px;
  padding:1.25rem;box-shadow:0 1px 4px rgba(15,23,42,.04);
}
.app-section-label{
  font-family:var(--fd) !important;font-size:10px;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;color:var(--subtle);
  display:block;margin-bottom:.75rem;padding-bottom:.5rem;border-bottom:1px solid var(--border);
}
.app-stat{
  display:inline-flex;align-items:center;gap:5px;background:var(--blue-50);
  border:1px solid var(--blue-100);color:#1d4ed8;border-radius:6px;
  font-family:var(--fd) !important;font-size:12px;font-weight:700;padding:3px 9px;white-space:nowrap;
}
.ex-pills{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;}

/* ── DRAFT ── */
.draft-card{
  background:#fff;border:1.5px solid var(--blue-100);border-radius:12px;
  padding:1.5rem;font-family:var(--fb) !important;line-height:1.75;
  font-size:14px;color:var(--navy);white-space:pre-wrap;
  box-shadow:0 4px 16px rgba(37,99,235,.06);
}
.draft-subject{
  font-family:var(--fd) !important;font-size:11px;font-weight:700;
  color:var(--muted);letter-spacing:.06em;text-transform:uppercase;margin-bottom:.4rem;
}
.draft-subject span{color:var(--navy);text-transform:none;letter-spacing:0;font-weight:500;font-size:14px;}

/* ── METRICS ── */
.metric-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:1.25rem;}
.metric-box{background:#fff;border:1px solid var(--border);border-radius:10px;padding:.9rem 1.1rem;box-shadow:0 1px 4px rgba(15,23,42,.04);}
.metric-label{font-size:10.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--subtle);margin-bottom:3px;}
.metric-value{font-family:var(--fd) !important;font-size:22px;font-weight:800;color:var(--navy);}
.metric-sub{font-size:11px;color:var(--muted);margin-top:2px;}

/* ── FORM OVERRIDES ── */
.stButton>button{
  background:var(--blue-600) !important;color:#fff !important;border:none !important;
  border-radius:8px !important;font-family:var(--fb) !important;font-weight:700 !important;
  font-size:.875rem !important;box-shadow:0 2px 8px rgba(37,99,235,.2) !important;transition:all .18s !important;
}
.stButton>button:hover{background:var(--blue-700) !important;transform:translateY(-1px) !important;}
[data-testid="stForm"]{background:#fff !important;border:1px solid var(--border) !important;border-radius:12px !important;padding:1.25rem !important;box-shadow:none !important;}
</style>
""", unsafe_allow_html=True)


def _app_topbar(title: str, subtitle: str, active: str = "") -> None:
    """Sticky topbar — personalised nav when logged in."""
    user = st.session_state.get("user")

    if user:
        # Logged-in: core nav + user badge + title
        cols = st.columns([1.4, 0.9, 0.8, 0.9, 1.0, 1.6, 2.1])
        with cols[0]:
            st.markdown('<div class="tb-logo-marker"><img src="app/static/skout-logo.png" style="height:26px;width:auto;display:block"></div>', unsafe_allow_html=True)
        for i, (key, path, label) in enumerate(_NAV_CORE):
            with cols[i + 1]:
                if active == key:
                    st.markdown('<div class="tb-active-marker"></div>', unsafe_allow_html=True)
                st.page_link(path, label=label)
        with cols[5]:
            role     = user.get("role", "creator")
            username = user.get("username", "")
            icon     = "🎤" if role == "creator" else "💼"
            st.markdown(f'<div class="tb-user-badge">{icon} @{username}</div>', unsafe_allow_html=True)
        with cols[6]:
            st.markdown(
                f'<div class="tb-title-cell"><span>{title}</span><span class="tb-title-sub">{subtitle}</span></div>',
                unsafe_allow_html=True,
            )
    else:
        # Guest: full nav including creator + business onboarding links
        _NAV_FULL = _NAV_CORE + _NAV_GUEST_EXTRA
        cols = st.columns([1.4, 0.9, 0.8, 0.9, 1.0, 0.85, 0.95, 2.1])
        with cols[0]:
            st.markdown('<div class="tb-logo-marker"><img src="app/static/skout-logo.png" style="height:26px;width:auto;display:block"></div>', unsafe_allow_html=True)
        for i, (key, path, label) in enumerate(_NAV_FULL):
            with cols[i + 1]:
                if active == key:
                    st.markdown('<div class="tb-active-marker"></div>', unsafe_allow_html=True)
                st.page_link(path, label=label)
        with cols[7]:
            st.markdown(
                f'<div class="tb-title-cell"><span>{title}</span><span class="tb-title-sub">{subtitle}</span></div>',
                unsafe_allow_html=True,
            )


def _page_hero(badge: str, title: str, desc: str) -> None:
    """Blue gradient hero — always visible without scrolling."""
    st.markdown(f"""
<div class="page-hero">
  <div class="page-hero-badge">{badge}</div>
  <h1 class="page-hero-title">{title}</h1>
  <p class="page-hero-desc">{desc}</p>
</div>
""", unsafe_allow_html=True)


def render_app_footer() -> None:
    """Footer — brand + account only. Tool pages are gated behind onboarding."""
    user = st.session_state.get("user")
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("""
<div class="footer-brand-marker">
  <div class="footer-brand-name"><img src="app/static/skout-logo.png" style="height:32px;width:auto;display:block"></div>
  <p class="footer-tagline">AI-powered influencer discovery &amp; outreach. Find the right creators in plain English.</p>
</div>
""", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="footer-col-label">Account</div>', unsafe_allow_html=True)
        if user:
            role = user.get("role", "creator")
            if role == "creator":
                st.page_link(_P_CREATOR_DASHBOARD,  label="My Dashboard")
            else:
                st.page_link(_P_BUSINESS_DASHBOARD, label="My Dashboard")
        else:
            st.page_link(_P_CREATOR,  label="Join as Creator")
            st.page_link(_P_BUSINESS, label="Join as Business")
            st.page_link(_P_LOGIN,    label="Log in")

    st.markdown("""
<div class="footer-bottom-bar">
  <span>© 2025 Skout — LangChain · Pinecone · FastAPI · Streamlit</span>
  <span style="color:var(--blue-600);font-weight:700">skout.ai</span>
</div>
""", unsafe_allow_html=True)


def render_app_sidebar(active: str = "") -> None:
    pass


def render_footer() -> None:
    render_app_footer()
