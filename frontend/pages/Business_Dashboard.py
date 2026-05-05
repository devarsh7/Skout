"""Skout Business Dashboard."""
from __future__ import annotations
import streamlit as st
from frontend.utils.api_client import APIError, _req, list_creators, update_me
from frontend.utils.map_utils import _fmt
from frontend.utils.session import clear_session, restore_session
from frontend.utils.styles import (
    _P_BUSINESS, _P_CAMPAIGNS, _P_CREATOR, _P_DISCOVER,
    _P_FILTER, _P_OUTREACH, _P_MAP, _P_AI_AGENT,
    _P_CREATOR_MATCH, _P_LOCAL_MARKET, inject_css,
)

inject_css()
restore_session()

user = st.session_state.get("user")
if not user or user.get("role") != "business":
    st.switch_page("pages/Home.py")
    st.stop()

# ── Account Settings dialog ────────────────────────────────────────────────────
@st.dialog("Account Settings", width="large")
def _settings(user: dict) -> None:
    token = st.session_state.get("user_token", "")
    try:
        fresh = _req("GET", "/auth/me", headers={"Authorization": f"Bearer {token}"})
        meta = dict(fresh.get("profile_meta") or {})
        st.session_state["user"]["profile_meta"] = meta
    except Exception:
        meta = dict(user.get("profile_meta") or {})

    view, edit = st.tabs(["📋 Profile", "✏️ Edit"])

    with view:
        st.markdown("""
<style>
.sv{background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;
    padding:10px 14px;font-size:13.5px;color:#0F172A;margin-bottom:4px;}
.sl{font-size:10px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;
    color:#94A3B8;margin-bottom:4px;margin-top:12px;display:block;}
.s-sect{font-size:10.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
    color:#4F46E5;margin-top:18px;margin-bottom:6px;padding-bottom:4px;
    border-bottom:1.5px solid #EEF2FF;display:block;}
</style>""", unsafe_allow_html=True)

        st.markdown('<span class="s-sect">Account</span>', unsafe_allow_html=True)
        st.markdown(
            f'<span class="sl">Username & Email</span>'
            f'<div class="sv">@{user.get("username","")} &nbsp;·&nbsp; {user.get("email","")}</div>',
            unsafe_allow_html=True)

        st.markdown('<span class="s-sect">Business Profile</span>', unsafe_allow_html=True)
        for lbl, val in [
            ("Company",   meta.get("company_name", "")),
            ("Website",   meta.get("website", "")),
            ("Contact",   meta.get("contact_name", "")),
            ("Phone",     meta.get("phone", "")),
            ("Country",   meta.get("country", "")),
            ("Industry",  meta.get("industry", "")),
            ("Budget",    meta.get("budget", "")),
            ("Platforms", "  ·  ".join(meta.get("platforms") or [])),
            ("Goals",     meta.get("goals", "")),
        ]:
            if val:
                st.markdown(f'<span class="sl">{lbl}</span><div class="sv">{val}</div>',
                            unsafe_allow_html=True)

        st.markdown('<span class="s-sect">Match Intelligence Targeting</span>', unsafe_allow_html=True)
        any_match = False
        for lbl, val in [
            ("Target City",       meta.get("target_city", "")),
            ("Target Gender",     meta.get("target_gender", "")),
            ("Target Age Ranges", "  ·  ".join(meta.get("target_age_range") or [])),
            ("Target Categories", "  ·  ".join(meta.get("target_categories") or [])),
        ]:
            if val:
                any_match = True
                st.markdown(f'<span class="sl">{lbl}</span><div class="sv">{val}</div>',
                            unsafe_allow_html=True)
        if not any_match:
            st.markdown('<div style="font-size:12.5px;color:#94A3B8;padding:8px 0">'
                        'No match criteria set — fill in the Edit tab to improve Creator Match scores.</div>',
                        unsafe_allow_html=True)

    with edit:
        company_locked = bool(meta.get("company_name"))
        if company_locked:
            st.markdown(
                f'<div style="background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:10px;'
                f'padding:10px 14px;margin-bottom:12px">'
                f'<span style="font-size:10px;font-weight:700;letter-spacing:.09em;'
                f'text-transform:uppercase;color:#94A3B8">Company name (locked)</span>'
                f'<div style="font-size:14.5px;font-weight:700;color:#0F172A;margin-top:4px">'
                f'{meta["company_name"]}</div></div>', unsafe_allow_html=True)

        with st.form("ep"):
            st.markdown('<div style="font-size:10.5px;font-weight:700;letter-spacing:.12em;'
                        'text-transform:uppercase;color:#4F46E5;margin-bottom:10px;'
                        'padding-bottom:4px;border-bottom:1.5px solid #EEF2FF">Business Profile</div>',
                        unsafe_allow_html=True)
            if not company_locked:
                cn = st.text_input("Company / Brand name *", value="", placeholder="Acme Corp")
            else:
                cn = meta["company_name"]
            a, b = st.columns(2)
            web = a.text_input("Website",      value=meta.get("website", ""),      placeholder="https://acmecorp.com")
            con = b.text_input("Contact name", value=meta.get("contact_name", ""), placeholder="Alex Johnson")
            c_, d = st.columns(2)
            ph  = c_.text_input("Phone",          value=meta.get("phone", ""),   placeholder="+1 555 000 1234")
            ctr = d.text_input("Country (ISO-2)", value=meta.get("country", ""), placeholder="US", max_chars=2)
            e_, f_ = st.columns(2)
            ind_opts = ["— select —","Beauty & Personal Care","Fashion & Apparel","Food & Beverage",
                        "Technology & Software","Travel & Hospitality","Health & Wellness",
                        "Finance & Fintech","Gaming & Entertainment","Education","Other"]
            cur_ind = meta.get("industry", "— select —")
            ind = e_.selectbox("Industry", ind_opts, index=ind_opts.index(cur_ind) if cur_ind in ind_opts else 0)
            bud_opts = ["— select —","Under $5K","$5K – $20K","$20K – $50K","$50K – $100K","$100K+"]
            cur_bud = meta.get("budget", "— select —")
            bud = f_.selectbox("Monthly budget", bud_opts, index=bud_opts.index(cur_bud) if cur_bud in bud_opts else 0)
            plat = st.multiselect("Platforms to activate",
                ["Instagram","TikTok","YouTube","Twitter / X","LinkedIn","Pinterest","Twitch"],
                default=meta.get("platforms", []))
            goals = st.text_area("Campaign goals", value=meta.get("goals", ""), height=80,
                                 placeholder="e.g. Drive awareness for our new vegan skincare line in Europe.")

            st.markdown('<div style="font-size:10.5px;font-weight:700;letter-spacing:.12em;'
                        'text-transform:uppercase;color:#4F46E5;margin:16px 0 10px;'
                        'padding-bottom:4px;border-bottom:1.5px solid #EEF2FF">'
                        '🎯 Match Intelligence Targeting</div>'
                        '<div style="font-size:12px;color:#64748B;margin-bottom:10px">'
                        'These fields power your SKOUT Match scores on the Creator Match page.</div>',
                        unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            target_city = m1.text_input("Target city", value=meta.get("target_city", ""), placeholder="e.g. Toronto")
            gender_opts = ["— any —", "Female", "Male"]
            cur_gender  = (meta.get("target_gender") or "— any —").capitalize()
            target_gender = m2.selectbox("Target audience gender", gender_opts,
                                         index=gender_opts.index(cur_gender) if cur_gender in gender_opts else 0)
            target_ages = st.multiselect("Target audience age range",
                ["13-17","18-24","25-34","35-44","45-54","55+"], default=meta.get("target_age_range", []))
            target_cats = st.multiselect("Target content categories",
                ["beauty","fashion","fitness","food","travel","gaming","tech","parenting",
                 "education","business","finance","lifestyle","art","music","sports",
                 "sustainability","pets","books"], default=meta.get("target_categories", []))

            if st.form_submit_button("💾 Save changes", type="primary", use_container_width=True):
                try:
                    payload = {
                        "website": web or None, "contact_name": con or None,
                        "phone": ph or None, "country": ctr.upper() if ctr else None,
                        "industry": ind if ind != "— select —" else None,
                        "budget": bud if bud != "— select —" else None,
                        "platforms": plat, "goals": goals or None,
                        "target_city": target_city.strip() or None,
                        "target_gender": target_gender.lower() if target_gender != "— any —" else None,
                        "target_age_range": target_ages or None,
                        "target_categories": target_cats or None,
                    }
                    if not company_locked:
                        payload["company_name"] = cn or None
                    r = update_me(payload, token)
                    st.session_state["user"]["profile_meta"] = r.get("profile_meta")
                    st.success("✓ Saved — match scores will update on next page load.")
                    st.rerun()
                except APIError as ex:
                    st.error(str(ex))


# ── CSS ────────────────────────────────────────────────────────────────────────
_DCSS = """
<style>
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stMainBlockContainer"]{
  background:linear-gradient(150deg,#EEF2FF 0%,#F8FAFF 50%,#EFF6FF 100%) !important;
}
.main .block-container,[data-testid="stMainBlockContainer"]{
  padding:0 3.5rem 4rem !important;max-width:100% !important;
}
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"]{gap:1rem !important;}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) [data-testid="stVerticalBlock"]{gap:0 !important;}
[data-testid="stHorizontalBlock"]:has(.sk-hdr){
  background:rgba(255,255,255,.97) !important;border-bottom:1px solid #E8EDFF !important;
  box-shadow:0 2px 20px rgba(79,70,229,.08) !important;padding:0 3.5rem !important;
  min-height:56px !important;align-items:center !important;
  position:sticky !important;top:0 !important;z-index:1000 !important;
  margin-left:-3.5rem !important;margin-right:-3.5rem !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) [data-testid="stColumn"]{
  display:flex !important;align-items:center !important;padding:0 4px !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) .stMarkdown,
[data-testid="stHorizontalBlock"]:has(.sk-hdr) [data-testid="stMarkdownContainer"]{
  display:flex !important;align-items:center !important;height:100% !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) .stButton>button{
  background:transparent !important;color:#4F46E5 !important;
  border:1.5px solid #C7D2FE !important;box-shadow:none !important;
  font-size:12px !important;font-weight:600 !important;
  padding:5px 14px !important;border-radius:9px !important;transition:background .15s !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) .stButton>button:hover{
  background:#EEF2FF !important;transform:none !important;box-shadow:none !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) .sk-out .stButton>button{
  color:#DC2626 !important;border-color:#FECACA !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) .sk-out .stButton>button:hover{background:#FEF2F2 !important;}
@keyframes riseIn{0%{opacity:0;transform:translateY(18px)}100%{opacity:1;transform:translateY(0)}}
@keyframes popIn{0%{opacity:0;transform:scale(.88)}60%{transform:scale(1.04)}100%{opacity:1;transform:scale(1)}}
.mk{background:white;border-radius:20px;padding:1.3rem 1.5rem 1.2rem;
  border-left:5px solid var(--c,#2563EB);border-top:1px solid #EEF2FF;
  border-right:1px solid #EEF2FF;border-bottom:1px solid #EEF2FF;
  box-shadow:0 4px 24px rgba(15,23,42,.07),0 1px 4px rgba(15,23,42,.04);
  animation:riseIn .5s cubic-bezier(.22,1,.36,1) both;
  transition:transform .25s cubic-bezier(.34,1.56,.64,1),box-shadow .25s ease;height:100%;}
.mk:hover{transform:translateY(-6px);box-shadow:0 16px 40px rgba(15,23,42,.12),0 4px 10px rgba(15,23,42,.05);}
.mk-icon{font-size:1.4rem;margin-bottom:.45rem;display:block;}
.mk-val{font-family:Poppins,sans-serif;font-size:2rem;font-weight:900;color:var(--c,#2563EB);
  line-height:1;margin-bottom:4px;letter-spacing:-.03em;animation:popIn .6s cubic-bezier(.22,1,.36,1) .1s both;}
.mk-lbl{font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#94A3B8;}
.mk-sub{font-size:12px;color:#64748B;margin-top:5px;font-weight:500;}
.mk:nth-child(1){animation-delay:.04s}.mk:nth-child(2){animation-delay:.10s}
.mk:nth-child(3){animation-delay:.16s}.mk:nth-child(4){animation-delay:.22s}
.fcard-wrap{background:white;border-radius:20px;padding:1.75rem 1.5rem 1.4rem;
  box-shadow:0 4px 24px rgba(15,23,42,.07),0 1px 4px rgba(15,23,42,.04);border:1px solid #EEF2FF;
  position:relative;overflow:hidden;min-height:210px;display:flex;flex-direction:column;
  transition:transform .3s cubic-bezier(.34,1.56,.64,1),box-shadow .3s ease,border-color .3s ease;
  animation:riseIn .55s cubic-bezier(.22,1,.36,1) both;}
.fcard-wrap::after{content:'';position:absolute;top:-28px;right:-28px;width:90px;height:90px;
  border-radius:50%;background:var(--fc-bg,#EEF2FF);pointer-events:none;opacity:.85;}
.fcard-icon{width:50px;height:50px;border-radius:14px;background:var(--fc-bg,#EEF2FF);
  display:flex;align-items:center;justify-content:center;font-size:1.45rem;
  margin-bottom:.9rem;flex-shrink:0;position:relative;z-index:1;}
.fcard-title{font-family:Poppins,sans-serif;font-size:14.5px;font-weight:700;color:#0F172A;
  margin-bottom:.4rem;line-height:1.25;position:relative;z-index:1;}
.fcard-desc{font-size:12px;color:#64748B;line-height:1.6;flex:1;margin-bottom:.9rem;position:relative;z-index:1;}
.fcard-cta{display:flex;align-items:center;gap:5px;font-size:12px;font-weight:700;
  color:var(--fc-c,#4F46E5);position:relative;z-index:1;}
.fc-arr{display:inline-block;transition:transform .2s cubic-bezier(.34,1.56,.64,1);}
[data-testid="stColumn"]:has(.fc-marker){position:relative !important;cursor:pointer !important;}
[data-testid="stColumn"]:has(.fc-marker):hover .fcard-wrap{
  transform:translateY(-8px);box-shadow:0 18px 42px rgba(15,23,42,.1),0 4px 12px rgba(15,23,42,.05);border-color:#C7D2FE;}
[data-testid="stColumn"]:has(.fc-marker):hover .fc-arr{transform:translateX(5px);}
[data-testid="stColumn"]:has(.fc-marker) [data-testid="stVerticalBlock"]{gap:0 !important;}
[data-testid="stColumn"]:has(.fc-marker) div:has(> [data-testid="stPageLink"]){
  height:0 !important;min-height:0 !important;padding:0 !important;margin:0 !important;
  overflow:visible !important;border:none !important;background:transparent !important;}
[data-testid="stColumn"]:has(.fc-marker) [data-testid="stPageLink"],
[data-testid="stColumn"]:has(.fc-marker) .stPageLink{
  position:absolute !important;inset:0 !important;z-index:10 !important;
  margin:0 !important;padding:0 !important;overflow:hidden !important;}
[data-testid="stColumn"]:has(.fc-marker) a[data-testid="stPageLink-NavLink"]{
  all:unset !important;display:block !important;position:absolute !important;
  inset:0 !important;min-height:220px !important;cursor:pointer !important;
  z-index:10 !important;color:transparent !important;font-size:0 !important;}
</style>
"""

_SPACER = "<div style='display:block;padding-top:2rem;width:100%'></div>"
_MINI   = "<div style='display:block;padding-top:0.75rem;width:100%'></div>"


def _sp(mini: bool = False) -> None:
    st.markdown(_MINI if mini else _SPACER, unsafe_allow_html=True)


def _header(user: dict, subtitle: str) -> None:
    meta    = user.get("profile_meta") or {}
    company = meta.get("company_name") or f"@{user.get('username','')}"

    a, b, spc, c, d, e = st.columns([2.2, 1.6, 4, 2.4, 1.1, 0.95])
    with a:
        st.markdown(
            '<div class="sk-hdr" style="display:flex;align-items:center;gap:9px">'
            '<img src="app/static/skout-logo.png" style="height:30px;width:auto;display:block"></div>',
            unsafe_allow_html=True)
    with b:
        st.markdown(f'<div style="font-size:12px;color:#94A3B8;font-weight:500;'
                    f'padding-left:12px;border-left:2px solid #EEF2FF">{subtitle}</div>',
                    unsafe_allow_html=True)
    with spc:
        pass
    with c:
        st.markdown(
            f'<div style="display:inline-flex;align-items:center;gap:7px;'
            f'background:#EEF2FF;border:1.5px solid #C7D2FE;'
            f'border-radius:999px;padding:5px 14px 5px 7px;max-width:200px">'
            f'<div style="width:26px;height:26px;border-radius:50%;flex-shrink:0;'
            f'background:linear-gradient(135deg,#4F46E5,#7C3AED);'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:12px;font-weight:800;color:#fff">💼</div>'
            f'<span style="font-size:13px;color:#3730A3;font-weight:700;'
            f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{company}</span>'
            f'</div>', unsafe_allow_html=True)
    with d:
        if st.button("⚙️ Settings", key="bd_settings"):
            _settings(user)
    with e:
        st.markdown('<div class="sk-out">', unsafe_allow_html=True)
        if st.button("Log out", key="bd_logout"):
            clear_session()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ── Render ─────────────────────────────────────────────────────────────────────
st.markdown(_DCSS, unsafe_allow_html=True)
_header(user, "Business Dashboard")
_sp()

try:    creators = list_creators(limit=200)
except APIError: creators = []

total_f  = sum(c.get("total_followers") or 0 for c in creators)
avg_eng  = sum(c.get("avg_engagement_rate") or 0 for c in creators) / max(len(creators), 1)
n_ctries = len({c.get("country") for c in creators if c.get("country")})
n_open   = sum(1 for c in creators if c.get("open_to_collabs"))

_l, c1, c2, c3, c4, _r = st.columns([0.18, 1, 1, 1, 1, 0.18], gap="medium")
for col, color, icon, val, lbl, sub in [
    (c1, "#2563EB", "👥", str(len(creators)), "Total Creators",  "indexed & searchable"),
    (c2, "#7C3AED", "📡", _fmt(total_f),      "Combined Reach",  "total followers"),
    (c3, "#059669", "📊", f"{avg_eng:.1%}",   "Avg Engagement",  "across all creators"),
    (c4, "#D97706", "🌍", str(n_ctries),      "Countries",       f"{n_open} open to collabs"),
]:
    with col:
        st.markdown(
            f'<div class="mk" style="--c:{color}">'
            f'<span class="mk-icon">{icon}</span>'
            f'<div class="mk-val">{val}</div>'
            f'<div class="mk-lbl">{lbl}</div>'
            f'<div class="mk-sub">{sub}</div>'
            f'</div>', unsafe_allow_html=True)

_sp()

st.markdown(
    '<div style="padding:0 0 1.4rem">'
    '<div style="font-size:10.5px;font-weight:700;letter-spacing:.15em;'
    'text-transform:uppercase;color:#4F46E5;margin-bottom:5px">Platform Suite</div>'
    '<div style="font-family:Poppins,sans-serif;font-size:1.35rem;font-weight:800;'
    'color:#0F172A;letter-spacing:-.025em">'
    'Everything you need to find and reach the right creators'
    '</div></div>',
    unsafe_allow_html=True)

CARDS = [
    ("🔍","#DBEAFE","#2563EB","#BFDBFE","Discover Influencers","Find creators in plain English. Semantic AI ranking across niches and geographies."),
    ("✉️","#EDE9FE","#7C3AED","#DDD6FE","AI Outreach","Generate personalized first-touch messages tailored to your brand voice."),
    ("📊","#DCFCE7","#059669","#A7F3D0","Campaigns","Track and manage your influencer campaigns end-to-end from brief to results."),
    ("🗺️","#E0F2FE","#0891B2","#A5F3FC","Creator Map","Visualize your global creator network on an interactive world map."),
    ("🤖","#EEF2FF","#4F46E5","#C7D2FE","AI Agent","Autonomous multi-agent workflows for campaign research and creator discovery."),
    ("🎯","#FEF3C7","#D97706","#FDE68A","Creator Match","AI compatibility scoring across location, niche, audience and engagement quality."),
    ("📍","#FFE4E6","#E11D48","#FECDD3","Local Market Intelligence","Hyperlocal insights — discover creators dominating your city or region."),
    ("🎛️","#F1F5F9","#475569","#CBD5E1","Smart Filters","Layer hard constraints: follower range, engagement rate, geo, niche."),
]
PATHS = [_P_DISCOVER, _P_OUTREACH, _P_CAMPAIGNS, _P_MAP, _P_AI_AGENT, _P_CREATOR_MATCH, _P_LOCAL_MARKET, _P_FILTER]

r1 = st.columns(4, gap="medium")
_sp(mini=True)
r2 = st.columns(4, gap="medium")
for i, ((icon, bg, color, accent, title, desc), path) in enumerate(zip(CARDS, PATHS)):
    col = (r1 if i < 4 else r2)[i % 4]
    with col:
        st.markdown('<span class="fc-marker"></span>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="fcard-wrap" style="--fc-bg:{bg};--fc-c:{color};'
            f'--fc-ac:{accent};animation-delay:{0.06 + i * 0.06:.2f}s">'
            f'<div class="fcard-icon">{icon}</div>'
            f'<div class="fcard-title">{title}</div>'
            f'<div class="fcard-desc">{desc}</div>'
            f'<div class="fcard-cta">Explore <span class="fc-arr">→</span></div>'
            f'</div>', unsafe_allow_html=True)
        st.page_link(path, label="Explore")

_sp()
