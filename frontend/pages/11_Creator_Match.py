"""Creator Match Intelligence — Instagram-style creator cards ranked by SKOUT Match Score."""
from __future__ import annotations

import streamlit as st

from backend.services.match_service import calculate_match_score, score_color, score_label
from frontend.utils.api_client import APIError, list_creators
from frontend.utils.map_utils import _AVC, _fmt, _ini, _NE
from frontend.utils.session import restore_session
from frontend.utils.styles import _P_HOME, inject_css
inject_css()
restore_session()

user = st.session_state.get("user")
if not user or user.get("role") != "business":
    st.switch_page(_P_HOME)

meta = user.get("profile_meta") or {}

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@keyframes riseIn{0%{opacity:0;transform:translateY(20px)}100%{opacity:1;transform:translateY(0)}}
@keyframes popIn {0%{opacity:0;transform:scale(.85)}60%{transform:scale(1.05)}100%{opacity:1;transform:scale(1)}}

/* Page background */
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stMainBlockContainer"]{
  background:linear-gradient(145deg,#EEF2FF 0%,#F6F8FF 40%,#EFF6FF 100%) !important;
}
.main .block-container,[data-testid="stMainBlockContainer"]{padding:0 3.5rem 4rem !important;max-width:100% !important;}
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"]{gap:1rem !important;}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) [data-testid="stVerticalBlock"]{gap:0 !important;}

/* Sticky header */
[data-testid="stHorizontalBlock"]:has(.sk-hdr){
  background:rgba(255,255,255,.97) !important;
  border-bottom:1px solid #E8EDFF !important;
  box-shadow:0 2px 24px rgba(79,70,229,.08) !important;
  padding:0 3.5rem !important;min-height:58px !important;
  align-items:center !important;
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
  padding:5px 14px !important;border-radius:9px !important;
  transition:background .15s !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) .stButton>button:hover{
  background:#EEF2FF !important;
}

/* ── Creator card — compact ── */
.mc-card{
  background:white;
  border-radius:20px;
  /* border applied inline per-card with direct score colors */
  border-top-width:4px;border-top-style:solid;
  border-left-width:1.5px;border-left-style:solid;
  border-right-width:1.5px;border-right-style:solid;
  border-bottom-width:1.5px;border-bottom-style:solid;
  padding:2.6rem 1.1rem 1rem;
  box-shadow:0 2px 16px rgba(15,23,42,.06),0 1px 4px rgba(15,23,42,.03);
  text-align:center;
  position:relative;
  overflow:visible;
  transition:transform .26s cubic-bezier(.34,1.56,.64,1),box-shadow .26s ease;
  animation:riseIn .5s cubic-bezier(.22,1,.36,1) both;
  display:flex;flex-direction:column;
}
.mc-card:hover{
  transform:translateY(-8px);
  box-shadow:0 18px 42px rgba(15,23,42,.1),0 4px 12px rgba(15,23,42,.05);
}

/* Match badge — top-right, higher z so tooltip still works */
.mc-badge-wrap{
  position:absolute;top:10px;right:10px;z-index:25;
}
.mc-badge{
  display:flex;flex-direction:column;align-items:center;
  padding:5px 9px;border-radius:11px;
  background:var(--mc-bg,#ECFDF5);
  border:1.5px solid var(--mc-ring,#A7F3D0);
  cursor:default;
}
.mc-badge-score{
  font-family:Poppins,sans-serif;font-size:14px;font-weight:900;
  color:var(--mc,#059669);line-height:1;
}
.mc-badge-lbl{
  font-size:7.5px;font-weight:700;letter-spacing:.07em;
  text-transform:uppercase;color:var(--mc,#059669);opacity:.75;margin-top:1px;
}

/* Avatar ring */
.mc-av-wrap{
  width:66px;height:66px;border-radius:50%;
  background:conic-gradient(var(--mc,#059669) 0%,var(--mc-ring,#A7F3D0) 100%);
  padding:2.5px;margin:0 auto .65rem;flex-shrink:0;position:relative;z-index:1;
}
.mc-av-inner{
  width:100%;height:100%;border-radius:50%;
  background:white;padding:2px;
  display:flex;align-items:center;justify-content:center;
}
.mc-av-circle{
  width:100%;height:100%;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-family:Poppins,sans-serif;font-weight:900;font-size:20px;color:white;
}

/* Name & handles */
.mc-name{
  font-family:Poppins,sans-serif;font-weight:700;font-size:13.5px;
  color:#0F172A;margin-bottom:3px;position:relative;z-index:1;
}
.mc-handles{
  font-size:11.5px;color:#64748B;margin-bottom:4px;
  position:relative;z-index:1;line-height:1.5;
}
.mc-handles a{text-decoration:none !important;}
.mc-handles a:hover{opacity:.75;}
.mc-loc{
  font-size:11px;color:#94A3B8;font-weight:500;
  margin-bottom:9px;position:relative;z-index:1;
}

/* Stats row */
.mc-stats{
  display:flex;justify-content:center;align-items:center;
  gap:0;margin-bottom:9px;
  background:#F8FAFF;border-radius:10px;padding:8px 0;
  position:relative;z-index:1;
}
.mc-stat{flex:1;text-align:center;}
.mc-stat-val{
  font-family:Poppins,sans-serif;font-size:14px;font-weight:900;
  color:#0F172A;line-height:1;
}
.mc-stat-lbl{
  font-size:9px;font-weight:700;letter-spacing:.07em;
  text-transform:uppercase;color:#94A3B8;margin-top:2px;
}
.mc-stat-div{width:1px;height:26px;background:#E2E8F0;flex-shrink:0;}

/* Niche pills */
.mc-niches{
  display:flex;flex-wrap:wrap;justify-content:center;gap:4px;
  flex:1;align-items:flex-end;position:relative;z-index:1;
}
.mc-niche{
  font-size:10.5px;font-weight:600;padding:2px 8px;
  border-radius:999px;background:#EEF2FF;
  color:#4F46E5;border:1px solid #C7D2FE;
}

/* Work Together pill — clickable anchor inside the card */
.mc-wt{
  position:absolute;top:12px;left:12px;
  display:inline-flex;align-items:center;gap:4px;
  font-size:10.5px;font-weight:700;
  color:#4F46E5;background:#EEF2FF;
  border:1.5px solid #C7D2FE;border-radius:999px;
  padding:4px 10px;white-space:nowrap;
  cursor:pointer;z-index:10;
  text-decoration:none;
  transition:background .15s,border-color .15s;
}
.mc-wt:hover{background:#E0E7FF;border-color:#A5B4FC;}

/* Column: positioned container */
[data-testid="stColumn"]:has(.mc-col){
  position:relative !important;
}

/* Criteria pill */
.cr-pill{
  display:inline-flex;align-items:center;gap:5px;
  font-size:12px;font-weight:600;padding:4px 12px;
  border-radius:999px;margin:0 3px 4px 0;
  border:1.5px solid;
}

/* Intro section */
.mc-intro{
  background:white;border-radius:22px;
  padding:1.5rem 1.8rem;
  border:1.5px solid #EEF2FF;
  box-shadow:0 2px 16px rgba(15,23,42,.05);
  animation:riseIn .45s cubic-bezier(.22,1,.36,1) both;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
hdr_a, hdr_b, hdr_spc, hdr_c = st.columns([2.2, 5, 4, 1.5])
with hdr_a:
    st.markdown(
        '<div class="sk-hdr" style="display:flex;align-items:center;gap:9px">'
        '<img src="app/static/skout-logo.png" style="height:30px;width:auto;display:block"></div>',
        unsafe_allow_html=True)
with hdr_b:
    st.markdown(
        '<div style="font-size:13px;font-weight:700;color:#0F172A;'
        'font-family:Poppins,sans-serif">🎯 Creator Match Intelligence</div>',
        unsafe_allow_html=True)
with hdr_c:
    if st.button("← Dashboard", use_container_width=True):
        st.switch_page(_P_HOME)

# ── Big breathing spacer after header ─────────────────────────────────────────
st.markdown("<div style='padding-top:2.25rem'></div>", unsafe_allow_html=True)

# ── Build criteria pills ───────────────────────────────────────────────────────
company         = meta.get("company_name", "")
industry        = meta.get("industry", "")
country         = meta.get("country", "")
budget          = meta.get("budget", "")
platforms       = meta.get("platforms") or []
target_city     = meta.get("target_city", "")
target_gender   = meta.get("target_gender", "")
target_ages     = meta.get("target_age_range") or []
target_cats     = meta.get("target_categories") or []

def _pill(text, color="#4F46E5", bg="#EEF2FF", border="#C7D2FE"):
    return (f'<span class="cr-pill" style="color:{color};background:{bg};border-color:{border}">'
            f'{text}</span>')

pills = ""
if company:       pills += _pill(f"🏢 {company}")
if target_city:   pills += _pill(f"📍 {target_city}", "#0891B2", "#E0F2FE", "#A5F3FC")
elif country:     pills += _pill(f"🌍 {country}", "#0891B2", "#E0F2FE", "#A5F3FC")
if industry:      pills += _pill(f"📂 {industry}", "#7C3AED", "#F5F3FF", "#DDD6FE")
if target_gender: pills += _pill(f"👥 {target_gender.title()}", "#059669", "#F0FDF4", "#A7F3D0")
for age in target_ages:
    pills += _pill(f"🎂 {age}", "#D97706", "#FEF3C7", "#FDE68A")
for cat in target_cats:
    pills += _pill(f"🎯 {cat}", "#E11D48", "#FFE4E6", "#FECDD3")
if budget:        pills += _pill(f"💰 {budget}", "#475569", "#F1F5F9", "#CBD5E1")

no_profile = not pills

# ── Intro / criteria card ──────────────────────────────────────────────────────
if no_profile:
    st.markdown(
        '<div class="mc-intro" style="border-left:4px solid #F59E0B">'
        '<div style="display:flex;align-items:flex-start;gap:14px">'
        '<div style="font-size:2rem;margin-top:2px">⚙️</div>'
        '<div>'
        '<div style="font-family:Poppins,sans-serif;font-weight:700;font-size:14.5px;'
        'color:#0F172A;margin-bottom:4px">Set up your match profile</div>'
        '<div style="font-size:13px;color:#64748B;line-height:1.65">'
        'Scores are based on generic signals right now. Open <b>⚙️ Settings</b> on the '
        'dashboard and fill in your <b>target city, categories, audience gender/age</b> '
        '— scores will immediately reflect your actual targeting.</div>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="mc-intro">'
        '<div style="font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;'
        'color:#94A3B8;margin-bottom:8px">Matching creators against your profile</div>'
        f'<div>{pills}</div>'
        '</div>',
        unsafe_allow_html=True)

st.markdown("<div style='padding-top:1.5rem'></div>", unsafe_allow_html=True)

# ── Load & score ───────────────────────────────────────────────────────────────
with st.spinner("Scoring creators…"):
    try:
        creators = list_creators(limit=200)
    except APIError:
        creators = []

scored = sorted(
    [(calculate_match_score(meta, c), c) for c in creators],
    key=lambda x: x[0]["total"],
    reverse=True,
)

if not scored:
    st.markdown(
        '<div class="mc-intro" style="text-align:center;padding:3rem">'
        '<div style="font-size:3rem;margin-bottom:.75rem">🎯</div>'
        '<div style="font-family:Poppins,sans-serif;font-weight:700;font-size:15px;color:#0F172A">'
        'No creators indexed yet</div>'
        '<div style="font-size:13px;color:#94A3B8;margin-top:.4rem">'
        'Onboard some creators first.</div>'
        '</div>',
        unsafe_allow_html=True)
    st.stop()

# Count line — with side breathing room
top_city = target_city or country or "your market"
st.markdown(
    f'<div style="display:flex;align-items:baseline;gap:8px;'
    f'padding:0 0.75rem;margin-bottom:1.1rem">'
    f'<span style="font-family:Poppins,sans-serif;font-weight:800;font-size:1.2rem;'
    f'color:#0F172A;letter-spacing:-.02em">{len(scored)}</span>'
    f'<span style="font-size:13.5px;color:#64748B">creators ranked for {top_city}</span>'
    f'<span style="margin-left:auto;font-size:11.5px;color:#94A3B8">'
    f'Hover score for breakdown &nbsp;·&nbsp; Click card to reach out</span>'
    f'</div>',
    unsafe_allow_html=True)

# ── Creator card builder ───────────────────────────────────────────────────────
def _card(sd: dict, creator: dict, rank: int) -> str:
    total = sd["total"]
    color, bg, ring = score_color(total)
    lbl   = score_label(total)
    delay = 0.05 + (rank - 1) * 0.04

    name      = creator.get("display_name") or creator.get("full_name") or "Creator"
    ig        = creator.get("instagram_handle") or ""
    tt        = creator.get("tiktok_handle") or ""
    city      = creator.get("city") or ""
    ctry      = creator.get("country") or ""
    loc       = ", ".join(filter(None, [city, ctry]))
    total_f   = creator.get("total_followers") or 0
    eng       = creator.get("avg_engagement_rate") or 0.0
    niches    = creator.get("niches") or []
    avc       = _AVC[hash(name) % len(_AVC)]

    handles_parts = []
    if ig:
        handles_parts.append(
            f'<a href="https://instagram.com/{ig}" target="_blank" '
            f'style="color:#E1306C;font-weight:600">📸 @{ig}</a>')
    if tt:
        handles_parts.append(
            f'<a href="https://tiktok.com/@{tt}" target="_blank" '
            f'style="color:#010101;font-weight:600">🎵 @{tt}</a>')
    handles_str = "  ·  ".join(handles_parts) if handles_parts else ""

    niche_pills = "".join(
        f'<span class="mc-niche">{_NE.get(n, "")} {n}</span>'
        for n in niches[:3])

    # Score breakdown tooltip
    bkdn_rows = "".join(
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'gap:10px;padding:3px 0;font-size:11.5px">'
        f'<span style="color:#64748B">{d["label"]}</span>'
        f'<span style="font-weight:700;color:#0F172A">{d["score"]:.0f}%</span>'
        f'</div>'
        for d in sd["breakdown"].values()
    )
    tooltip = (
        f'<div style="display:none;position:absolute;top:calc(100% + 6px);right:0;'
        f'background:white;border:1.5px solid #E2E8F0;border-radius:14px;'
        f'padding:12px 14px;min-width:200px;'
        f'box-shadow:0 8px 28px rgba(15,23,42,.13);z-index:50;pointer-events:none" '
        f'class="mc-tt">'
        f'<div style="font-size:9.5px;font-weight:700;letter-spacing:.1em;'
        f'text-transform:uppercase;color:#94A3B8;margin-bottom:8px">Breakdown</div>'
        f'{bkdn_rows}'
        f'</div>'
    )

    parts = [
        f'<div class="mc-card" style="'
        f'border-color:{ring};border-top-color:{color};'
        f'animation-delay:{delay:.2f}s">',

        # Work Together pill — direct anchor, no st.page_link needed
        f'<a class="mc-wt" href="4_%E2%9C%89%EF%B8%8F_AI_Outreach">✉️ Work Together</a>',

        # Badge + tooltip — top-right
        f'<div class="mc-badge-wrap"'
        f' onmouseenter="this.querySelector(\'.mc-tt\').style.display=\'block\'"'
        f' onmouseleave="this.querySelector(\'.mc-tt\').style.display=\'none\'">',
        f'<div class="mc-badge" style="background:{bg};border-color:{ring}">',
        f'<div class="mc-badge-score" style="color:{color}">{total:.0f}</div>',
        f'<div class="mc-badge-lbl" style="color:{color}">{lbl}</div>',
        f'</div>',
        tooltip,
        f'</div>',

        # Avatar ring
        f'<div class="mc-av-wrap" style="background:conic-gradient({color} 0%,{ring} 100%)">',
        f'<div class="mc-av-inner">',
        f'<div class="mc-av-circle" style="background:{avc}">{_ini(name)}</div>',
        f'</div></div>',

        # Name
        f'<div class="mc-name">{name}</div>',

        # Handles (or spacer)
        f'<div class="mc-handles">{handles_str}</div>' if handles_str
            else '<div style="height:1.25rem"></div>',

        # Location (or spacer)
        f'<div class="mc-loc">📍 {loc}</div>' if loc
            else '<div style="height:1.15rem"></div>',

        # Stats row
        f'<div class="mc-stats">',
        f'<div class="mc-stat">',
        f'<div class="mc-stat-val">{_fmt(total_f)}</div>',
        f'<div class="mc-stat-lbl">Followers</div>',
        f'</div>',
        f'<div class="mc-stat-div"></div>',
        f'<div class="mc-stat">',
        f'<div class="mc-stat-val">{eng:.1%}</div>',
        f'<div class="mc-stat-lbl">Engagement</div>',
        f'</div>',
        f'</div>',

        # Niches (or spacer)
        f'<div class="mc-niches">{niche_pills}</div>' if niche_pills
            else '<div style="height:1.5rem"></div>',

        '</div>',
    ]
    return "".join(parts)

# ── Grid: 3 cards per row, side-padded ─────────────────────────────────────────
SHOW = min(len(scored), 12)

_, grid, _ = st.columns([0.06, 1, 0.06])
with grid:
    for row_start in range(0, SHOW, 3):
        cols = st.columns(3, gap="large")
        for j, (sd, creator) in enumerate(scored[row_start:row_start + 3]):
            rank = row_start + j + 1
            with cols[j]:
                st.markdown(
                    '<span class="mc-col"></span>' + _card(sd, creator, rank),
                    unsafe_allow_html=True,
                )
        st.markdown("<div style='padding-top:1rem'></div>", unsafe_allow_html=True)

if len(scored) > 12:
    st.markdown(
        f'<div style="text-align:center;padding:1rem 0;font-size:13px;color:#94A3B8">'
        f'Showing top 12 of {len(scored)} creators</div>',
        unsafe_allow_html=True)
