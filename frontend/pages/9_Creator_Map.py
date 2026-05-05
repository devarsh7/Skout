"""Creator World Map — interactive geographic view with filters."""
from __future__ import annotations

import streamlit as st

from frontend.utils.api_client import APIError, list_creators
from frontend.utils.map_utils import _NC, _DC, _NE, _fmt, _map_df, _draw_map
from frontend.utils.session import restore_session
from frontend.utils.styles import _P_HOME, inject_css

inject_css()
restore_session()

user = st.session_state.get("user")
if not user:
    st.switch_page(_P_HOME)

# ── page CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stMainBlockContainer"]{
  background:linear-gradient(150deg,#EEF2FF 0%,#F8FAFF 50%,#EFF6FF 100%) !important;
}
.main .block-container,[data-testid="stMainBlockContainer"]{
  padding:0 !important;max-width:100% !important;
}
section[data-testid="stMain"]>div>div[data-testid="stVerticalBlock"]{gap:.4rem !important;}
[data-testid="stHorizontalBlock"]:has(.sk-hdr){
  background:rgba(255,255,255,.97) !important;
  border-bottom:1px solid #E8EDFF !important;
  box-shadow:0 2px 20px rgba(79,70,229,.08) !important;
  padding:0 2rem !important;min-height:56px !important;
  align-items:center !important;
  position:sticky !important;top:0 !important;z-index:1000 !important;
}
/* content columns: small outer margin so map/filters don't touch viewport edges */
[data-testid="stHorizontalBlock"]:has(.fp-mk){
  padding:0 1.25rem !important;
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
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.fp-mk){
  background:white !important;border-radius:20px !important;
  border:1px solid #E8EDFF !important;
  box-shadow:0 4px 28px rgba(79,70,229,.08),0 1px 4px rgba(15,23,42,.04) !important;
  padding:0 !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.fp-mk)>[data-testid="stVerticalBlock"]{
  padding:1.4rem 1.4rem 1.2rem !important;gap:.55rem !important;
}
.fp-title{font-family:Poppins,sans-serif;font-weight:700;font-size:13.5px;
  color:#0F172A;display:flex;align-items:center;gap:7px;margin-bottom:2px;}
.fp-hr{height:1px;background:#F1F5F9;margin:4px 0 2px;}
.fp-lbl{font-size:10px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;
  color:#94A3B8;display:block;margin-bottom:2px;}
.ms{background:white;border-radius:20px;overflow:hidden;
  box-shadow:0 4px 28px rgba(79,70,229,.08),0 1px 4px rgba(15,23,42,.04);}
.ms-top{padding:1rem 1.5rem;display:flex;align-items:center;
  justify-content:space-between;border-bottom:1px solid #F0F4FF;}
.ms-title{font-family:Poppins,sans-serif;font-weight:700;font-size:14px;
  color:#0F172A;display:flex;align-items:center;gap:8px;}
.ms-count{background:#EEF2FF;color:#4F46E5;border:1.5px solid #C7D2FE;
  border-radius:999px;font-size:12px;font-weight:700;padding:3px 12px;}
.ms-legend{padding:.75rem 1.5rem;display:flex;flex-wrap:wrap;gap:5px;
  background:#FAFBFF;border-top:1px solid #F0F4FF;}
.ms-tag{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:600;
  color:#475569;background:white;border:1px solid #E2E8F0;padding:3px 9px;border-radius:7px;}
.ms-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0;}
@keyframes riseIn{0%{opacity:0;transform:translateY(14px)}100%{opacity:1;transform:translateY(0)}}
</style>
""", unsafe_allow_html=True)

_SPACER = "<div style='display:block;padding-top:1.5rem;width:100%'></div>"
_MINI   = "<div style='display:block;padding-top:0.6rem;width:100%'></div>"

# ── header ────────────────────────────────────────────────────────────────────
meta    = (user.get("profile_meta") or {})
company = meta.get("company_name") or f"@{user.get('username','')}"

hdr_a, hdr_b, hdr_spc, hdr_c = st.columns([2.2, 5, 4, 1.5])
with hdr_a:
    st.markdown(
        '<div class="sk-hdr" style="display:flex;align-items:center;gap:9px">'
        '<img src="app/static/skout-logo.png" style="height:30px;width:auto;display:block"></div>',
        unsafe_allow_html=True)
with hdr_b:
    st.markdown(
        '<div style="font-size:13px;font-weight:700;color:#0F172A;'
        'font-family:Poppins,sans-serif">🗺️ Creator World Map</div>',
        unsafe_allow_html=True)
with hdr_c:
    if st.button("← Dashboard", use_container_width=True):
        st.switch_page(_P_HOME)

st.markdown(_SPACER, unsafe_allow_html=True)

# ── data ──────────────────────────────────────────────────────────────────────
try:
    creators = list_creators(limit=200)
except APIError:
    creators = []

all_niches = sorted({n for c in creators for n in (c.get("niches") or [])})
all_ctries = sorted({str(c.get("country")) for c in creators if c.get("country")})

# ── layout: filters left, map right ──────────────────────────────────────────
fp_col, map_col = st.columns([1.3, 3.4], gap="large")

with fp_col:
    with st.container(border=True):
        st.markdown('<span class="fp-mk"></span>', unsafe_allow_html=True)
        st.markdown('<div class="fp-title">🎛️&nbsp; Filters</div>', unsafe_allow_html=True)

        st.markdown('<div class="fp-hr"></div>', unsafe_allow_html=True)
        st.markdown('<span class="fp-lbl">Search</span>', unsafe_allow_html=True)
        search = st.text_input("Search creator", placeholder="Name or @handle…",
                               label_visibility="collapsed", key="cms")

        st.markdown('<div class="fp-hr"></div>', unsafe_allow_html=True)
        st.markdown('<span class="fp-lbl">Niche</span>', unsafe_allow_html=True)
        sel_niches = st.multiselect("Select niches", all_niches,
                                    placeholder="All niches",
                                    label_visibility="collapsed", key="cmn")

        st.markdown('<div class="fp-hr"></div>', unsafe_allow_html=True)
        st.markdown('<span class="fp-lbl">Platform</span>', unsafe_allow_html=True)
        f_ig = st.checkbox("📸 Instagram", key="cmi")
        f_tt = st.checkbox("🎵 TikTok",    key="cmt")
        f_yt = st.checkbox("▶️ YouTube",   key="cmy")

        st.markdown('<div class="fp-hr"></div>', unsafe_allow_html=True)
        st.markdown('<span class="fp-lbl">Min Followers</span>', unsafe_allow_html=True)
        min_f = st.select_slider(
            "Minimum followers", label_visibility="collapsed",
            options=[0, 1_000, 5_000, 10_000, 50_000, 100_000, 500_000, 1_000_000],
            value=0, format_func=lambda x: _fmt(x) if x else "Any", key="cmf")

        st.markdown('<div class="fp-hr"></div>', unsafe_allow_html=True)
        st.markdown('<span class="fp-lbl">Country</span>', unsafe_allow_html=True)
        sel_ct = st.selectbox("Select country", ["All"] + all_ctries,
                              label_visibility="collapsed", key="cmc")

        st.markdown('<div class="fp-hr"></div>', unsafe_allow_html=True)
        only_op = st.checkbox("✅ Open to collabs only", key="cmo")

# apply filters
fil = creators[:]
if search:
    q = search.lstrip("@").lower()
    fil = [c for c in fil if
           q in (c.get("full_name") or "").lower() or
           q in (c.get("display_name") or "").lower() or
           q in (c.get("instagram_handle") or "").lower() or
           q in (c.get("tiktok_handle") or "").lower()]
if sel_niches:
    fil = [c for c in fil if any(n in (c.get("niches") or []) for n in sel_niches)]
if f_ig: fil = [c for c in fil if c.get("instagram_handle")]
if f_tt: fil = [c for c in fil if c.get("tiktok_handle")]
if f_yt: fil = [c for c in fil if c.get("youtube_channel")]
if min_f > 0:
    fil = [c for c in fil if (c.get("total_followers") or 0) >= min_f]
if sel_ct != "All":
    fil = [c for c in fil if c.get("country") == sel_ct]
if only_op:
    fil = [c for c in fil if c.get("open_to_collabs")]

with map_col:
    legend = "".join(
        f'<span class="ms-tag">'
        f'<span class="ms-dot" style="background:rgb({",".join(str(x) for x in _NC.get(n, _DC)[:3])})"></span>'
        f'{_NE.get(n, "")}&thinsp;{n}</span>'
        for n in sorted(all_niches))
    st.markdown(
        f'<div class="ms">'
        f'<div class="ms-top">'
        f'<span class="ms-title">🗺️ Creator World Map</span>'
        f'<span class="ms-count">{len(fil)} creator{"s" if len(fil) != 1 else ""}</span>'
        f'</div>',
        unsafe_allow_html=True)
    _draw_map(_map_df(fil), height=480)
    st.markdown(f'<div class="ms-legend">{legend}</div></div>', unsafe_allow_html=True)
