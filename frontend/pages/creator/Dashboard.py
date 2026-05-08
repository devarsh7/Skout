"""Skout — Creator Dashboard page."""
from __future__ import annotations
import streamlit as st
from frontend.utils.api_client import APIError, _req, get_creator, update_me
from frontend.utils.map_utils import _AVC, _fmt, _ini, _NE
from frontend.utils.session import clear_session, restore_session
from frontend.utils.styles import _P_HOME, inject_css

inject_css()
restore_session()

user = st.session_state.get("user")
if not user or user.get("role") != "creator":
    st.switch_page(_P_HOME)
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

        st.markdown('<span class="s-sect">Creator Profile</span>', unsafe_allow_html=True)
        creator_id = user.get("creator_id")
        if creator_id:
            try:
                prof = get_creator(creator_id)
                for lbl, val in [
                    ("Display name", prof.get("display_name") or prof.get("full_name", "")),
                    ("Location",     ", ".join(filter(None, [prof.get("city",""), prof.get("country","")])) ),
                    ("Niches",       "  ·  ".join(prof.get("niches") or [])),
                    ("Languages",    "  ·  ".join(prof.get("languages") or [])),
                    ("Min rate",     f'${prof["min_rate_usd"]:,.0f}/post' if prof.get("min_rate_usd") else ""),
                ]:
                    if val:
                        st.markdown(
                            f'<span class="sl">{lbl}</span><div class="sv">{val}</div>',
                            unsafe_allow_html=True)
            except APIError:
                st.caption("Could not load creator profile.")
        else:
            st.markdown(
                '<div style="font-size:12.5px;color:#94A3B8;padding:8px 0">'
                'No creator profile linked yet — complete onboarding to appear in search.</div>',
                unsafe_allow_html=True)

    with edit:
        with st.form("creator_settings_form"):
            st.markdown(
                '<div style="font-size:10.5px;font-weight:700;letter-spacing:.12em;'
                'text-transform:uppercase;color:#4F46E5;margin-bottom:10px;'
                'padding-bottom:4px;border-bottom:1.5px solid #EEF2FF">Profile Settings</div>',
                unsafe_allow_html=True)
            st.info("To update your creator profile, visit the Update Profile page from the sidebar.", icon="✏️")
            st.form_submit_button("Close", use_container_width=True)


# ── Dashboard CSS ──────────────────────────────────────────────────────────────
_DCSS = """
<style>
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
  background: linear-gradient(150deg,#EEF2FF 0%,#F8FAFF 50%,#EFF6FF 100%) !important;
}
.main .block-container,
[data-testid="stMainBlockContainer"] {
  padding: 0 2.5rem 4rem !important;
  max-width: 100% !important;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > div {
  margin-bottom: 1.25rem !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) [data-testid="stVerticalBlock"] {
  gap: 0 !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr){
  background: rgba(255,255,255,.97) !important;
  border-bottom: 1px solid #E8EDFF !important;
  box-shadow: 0 2px 20px rgba(79,70,229,.08) !important;
  padding: 0 3.5rem !important;
  min-height: 56px !important;
  align-items: center !important;
  position: sticky !important; top:0 !important; z-index:1000 !important;
  margin-left: -3.5rem !important; margin-right: -3.5rem !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) [data-testid="stColumn"]{
  display:flex !important; align-items:center !important; padding:0 4px !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) .stMarkdown,
[data-testid="stHorizontalBlock"]:has(.sk-hdr) [data-testid="stMarkdownContainer"]{
  display:flex !important; align-items:center !important; height:100% !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) .stButton>button{
  background: transparent !important; color: #4F46E5 !important;
  border: 1.5px solid #C7D2FE !important; box-shadow: none !important;
  font-size: 12px !important; font-weight: 600 !important;
  padding: 5px 14px !important; border-radius: 9px !important;
  transition: background .15s !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) .stButton>button:hover{
  background: #EEF2FF !important; transform: none !important; box-shadow: none !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) .sk-out .stButton>button{
  color: #DC2626 !important; border-color: #FECACA !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) .sk-out .stButton>button:hover{
  background: #FEF2F2 !important;
}
@keyframes riseIn {
  0%  { opacity:0; transform:translateY(18px); }
  100%{ opacity:1; transform:translateY(0); }
}
@keyframes popIn {
  0%  { opacity:0; transform:scale(.88); }
  60% { transform:scale(1.04); }
  100%{ opacity:1; transform:scale(1); }
}
.sc {
  background: white; border-radius:16px;
  padding: 1.25rem 1rem; text-align:center;
  box-shadow: 0 4px 20px rgba(15,23,42,.07), 0 1px 4px rgba(15,23,42,.04);
  border: 1px solid #EEF2FF;
  border-bottom: 3px solid var(--sc,#6366F1);
  transition: transform .25s cubic-bezier(.34,1.56,.64,1), box-shadow .25s ease;
  animation: riseIn .5s cubic-bezier(.22,1,.36,1) both;
}
.sc:hover { transform:translateY(-5px); box-shadow:0 14px 36px rgba(15,23,42,.1); }
.sc-icon{ font-size:1.2rem; margin-bottom:.35rem; }
.sc-val { font-family:Poppins,sans-serif; font-size:1.5rem; font-weight:900;
          color:var(--sc,#6366F1); line-height:1; }
.sc-lbl { font-size:10px; font-weight:700; letter-spacing:.08em;
          text-transform:uppercase; color:#94A3B8; margin-top:4px; }
.sc:nth-child(1){animation-delay:.06s}.sc:nth-child(2){animation-delay:.11s}
.sc:nth-child(3){animation-delay:.16s}.sc:nth-child(4){animation-delay:.21s}
.sc:nth-child(5){animation-delay:.26s}.sc:nth-child(6){animation-delay:.31s}
.sc:nth-child(7){animation-delay:.36s}
.sc-explore{
  display:inline-block;margin-top:9px;
  font-size:10px;font-weight:700;letter-spacing:.05em;
  color:var(--sc,#7C3AED);text-decoration:none !important;
  padding:3px 11px;border:1.5px solid var(--sc,#7C3AED);border-radius:999px;
  opacity:.7;transition:opacity .15s,background .15s;
}
.sc-explore:hover{opacity:1;background:rgba(124,58,237,.08);}
.ch {
  background: linear-gradient(135deg,#4338CA 0%,#4F46E5 35%,#6366F1 65%,#818CF8 100%);
  border-radius: 18px; padding: 1rem 1.25rem;
  box-shadow: 0 8px 40px rgba(79,70,229,.22), 0 2px 8px rgba(79,70,229,.12);
  animation: riseIn .55s cubic-bezier(.22,1,.36,1) both;
}
.ic {
  background:white; border-radius:16px; padding:1.5rem 1.75rem;
  box-shadow:0 4px 24px rgba(15,23,42,.07), 0 1px 4px rgba(15,23,42,.04);
  border:1px solid #EEF2FF;
  animation:riseIn .5s cubic-bezier(.22,1,.36,1) both;
  height: 100%;
}
.ic-hd {
  font-size:9.5px; font-weight:700; letter-spacing:.1em; text-transform:uppercase;
  color:#94A3B8; padding-bottom:.75rem; border-bottom:1px solid #F1F5F9;
  margin-bottom:1.1rem; display:block;
}
.ic a[data-testid="stPageLink-NavLink"]{
  display:flex !important; align-items:center !important;
  background:#F8FAFC !important; border:1.5px solid #E2E8F0 !important;
  border-radius:11px !important; padding:9px 14px !important;
  font-size:13px !important; font-weight:600 !important;
  color:#0F172A !important; margin-bottom:7px !important;
  transition: all .18s cubic-bezier(.34,1.56,.64,1) !important;
}
.ic a[data-testid="stPageLink-NavLink"]:hover{
  background:#EEF2FF !important; border-color:#C7D2FE !important;
  color:#4F46E5 !important; transform:translateX(5px) !important;
}
</style>
"""


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
        st.markdown(
            f'<div style="font-size:12px;color:#94A3B8;font-weight:500;'
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
            f'font-size:12px;font-weight:800;color:#fff">🎤</div>'
            f'<span style="font-size:13px;color:#3730A3;font-weight:700;'
            f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{company}</span>'
            f'</div>',
            unsafe_allow_html=True)
    with d:
        if st.button("⚙️ Settings", key="cd_settings"):
            _settings(user)
    with e:
        st.markdown('<div class="sk-out">', unsafe_allow_html=True)
        if st.button("Log out", key="cd_logout"):
            clear_session()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ── Render ─────────────────────────────────────────────────────────────────────
st.markdown(_DCSS, unsafe_allow_html=True)
_header(user, "Creator Dashboard")
st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

uid   = user.get("creator_id")
uname = user.get("username", "")
prof: dict = {}
if uid:
    try:
        prof = get_creator(uid)
    except APIError:
        pass

name    = prof.get("display_name") or prof.get("full_name") or uname
bio     = prof.get("bio") or ""
niches  = prof.get("niches") or []
country = prof.get("country") or ""
city    = prof.get("city") or ""
ig      = prof.get("instagram_handle") or ""
tt      = prof.get("tiktok_handle") or ""
yt      = prof.get("youtube_channel") or ""
total_f = prof.get("total_followers") or 0
ig_f    = prof.get("instagram_followers") or 0
tt_f    = prof.get("tiktok_followers") or 0
yt_s    = prof.get("youtube_subscribers") or 0
eng     = prof.get("avg_engagement_rate") or 0.0
avg_v   = prof.get("avg_views") or 0
rate    = prof.get("min_rate_usd") or 0.0
indexed = prof.get("vector_indexed", False)
open_c  = prof.get("open_to_collabs", True)
collabs = prof.get("preferred_collab_types") or []
langs   = prof.get("languages") or []
avc     = _AVC[hash(uname) % len(_AVC)]
loc     = ", ".join(filter(None, [city, country]))
plat    = "  ·  ".join(filter(None, [
    f"📸 @{ig}" if ig else "",
    f"🎵 @{tt}" if tt else "",
    f"▶️ {yt}"  if yt else ""]))

niche_pills = "".join(
    '<span style="background:rgba(255,255,255,.18);color:#fff;'
    'font-size:12px;font-weight:600;padding:4px 13px;border-radius:999px;'
    'margin:0 5px 5px 0;display:inline-block;border:1px solid rgba(255,255,255,.2)">'
    + _NE.get(n, "") + " " + n + "</span>"
    for n in niches[:6])

idx_lbl = "✅  Indexed & Live"  if indexed else "⏳  Indexing soon"
idx_bg  = "rgba(16,185,129,.18)" if indexed else "rgba(245,158,11,.18)"

rate_html = ""
if rate:
    rate_html = (
        f'<div style="margin-top:14px;display:inline-flex;align-items:baseline;gap:4px">'
        f'<span style="font-family:Poppins,sans-serif;font-size:1.25rem;'
        f'font-weight:900;color:#fff">${rate:,.0f}</span>'
        f'<span style="font-size:11px;opacity:.5;color:#fff">/post</span></div>')

# ── Hero ───────────────────────────────────────────────────────────────────────
h1, h2 = st.columns([3, 1], gap="large")
with h1:
    st.markdown(
        '<div class="ch">'
        '<div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">'
        f'<div style="width:52px;height:52px;border-radius:14px;background:{avc};'
        'display:flex;align-items:center;justify-content:center;'
        'font-family:Poppins,sans-serif;font-weight:900;font-size:20px;color:#fff;'
        'border:3px solid rgba(255,255,255,.25);flex-shrink:0">' + _ini(name) + '</div>'
        '<div style="flex:1;min-width:0">'
        '<h1 style="font-family:Poppins,sans-serif;font-size:1.25rem;font-weight:800;'
        'color:#fff;margin:0 0 2px;line-height:1.1">' + name +
        f'<span style="font-size:.8rem;opacity:.4;font-weight:400;margin-left:8px">'
        f'@{uname}</span></h1>'
        + (f'<div style="font-size:12px;color:rgba(255,255,255,.65);margin-bottom:2px">{plat}</div>' if plat else "")
        + (f'<div style="font-size:11px;color:rgba(255,255,255,.45)">📍 {loc}</div>' if loc else "")
        + '</div>'
        '<div>' + niche_pills + '</div>'
        '</div>'
        + '</div>',
        unsafe_allow_html=True)
with h2:
    st.markdown(
        f'<div class="ch" style="text-align:center;height:100%">'
        f'<div style="display:inline-flex;align-items:center;gap:6px;'
        f'background:{idx_bg};color:#fff;border:1.5px solid rgba(255,255,255,.25);'
        f'font-size:12.5px;font-weight:700;padding:6px 14px;border-radius:999px;'
        f'margin-bottom:8px">{idx_lbl}</div>'
        f'<div style="font-size:11.5px;color:rgba(255,255,255,.5);line-height:1.5">'
        + ("Brands discover you in semantic search." if indexed else "Your profile will be indexed shortly.")
        + f'</div>{rate_html}</div>',
        unsafe_allow_html=True)

# ── Stats (left) + Profile details (right) ────────────────────────────────────
sc_data = [
    ("#6366F1", "👥", _fmt(total_f), "Total"),
    ("#2563EB", "📸", _fmt(ig_f),    "Instagram"),
    ("#8B5CF6", "🎵", _fmt(tt_f),    "TikTok"),
    ("#EC4899", "▶️", _fmt(yt_s),    "YouTube"),
    ("#059669", "📊", f"{eng:.1%}",  "Engagement"),
    ("#06B6D4", "👁️", _fmt(avg_v),   "Avg Views"),
]

sc_html = "".join(
    f'<div class="sc" style="--sc:{c}">'
    f'<div class="sc-icon">{ico}</div>'
    f'<div class="sc-val">{val}</div>'
    f'<div class="sc-lbl">{lbl}</div>'
    f'</div>'
    for c, ico, val, lbl in sc_data
)
sc_html += (
    '<div class="sc" style="--sc:#7C3AED">'
    '<div class="sc-icon">✨</div>'
    '<div class="sc-val">AI</div>'
    '<div class="sc-lbl">Career Manager</div>'
    '<a class="sc-explore" href="/Career_Manager" target="_self">Explore →</a>'
    '</div>'
)

oc_bg  = "#F0FDF4" if open_c else "#FEF2F2"
oc_tc  = "#059669" if open_c else "#DC2626"
oc_bc  = "#BBF7D0" if open_c else "#FECACA"
oc_lbl = "✅ Open to collabs" if open_c else "⏸ Not available"

detail_rows = [("Collab status",
    f'<span style="background:{oc_bg};color:{oc_tc};border:1.5px solid {oc_bc};'
    f'font-size:12.5px;font-weight:700;padding:5px 13px;border-radius:999px;'
    f'display:inline-block">{oc_lbl}</span>')]
if rate:  detail_rows.append(("Min rate", f'<b style="font-family:Poppins;font-size:17px;color:#0F172A">${rate:,.0f}</b><span style="color:#94A3B8;font-size:11px;margin-left:2px">/post</span>'))
if loc:   detail_rows.append(("Location", loc))
if langs: detail_rows.append(("Languages", "  ·  ".join(langs[:6])))

detail_html = "".join(
    f'<div style="display:flex;gap:14px;align-items:center;padding:12px 0;border-bottom:1px solid #F1F5F9">'
    f'<div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;'
    f'color:#94A3B8;min-width:115px;flex-shrink:0">{lbl}</div>'
    f'<div style="font-size:13.5px;color:#0F172A">{val}</div></div>'
    for lbl, val in detail_rows
)

if collabs:
    pills = "".join(
        f'<span style="background:#EEF2FF;color:#4F46E5;border:1.5px solid #C7D2FE;'
        f'font-size:11.5px;font-weight:600;padding:3px 11px;border-radius:999px;'
        f'margin:0 5px 5px 0;display:inline-block">{ct}</span>'
        for ct in collabs)
    detail_html += (
        f'<div style="padding:12px 0">'
        f'<div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;'
        f'color:#94A3B8;margin-bottom:8px">Collab types</div>{pills}</div>'
    )

st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;align-items:start;margin-top:1.5rem">

  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem">
    {sc_html}
  </div>

  <div class="ic">
    <span class="ic-hd">Profile Details</span>
    {detail_html}
  </div>

</div>
""", unsafe_allow_html=True)


