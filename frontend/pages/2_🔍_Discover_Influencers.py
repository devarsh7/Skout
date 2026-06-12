"""Discover — natural-language creator search."""
from __future__ import annotations

import streamlit as st

from frontend.components.creator_card import render_creator_card
from frontend.utils.api_client import APIError, discover
from frontend.utils.styles import _P_HOME, inject_css


inject_css()
st.markdown("""
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
  background:rgba(255,255,255,.97) !important;
  border-bottom:1px solid #E8EDFF !important;
  box-shadow:0 2px 20px rgba(79,70,229,.08) !important;
  padding:0 3.5rem !important;min-height:56px !important;
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
}
@keyframes riseIn{0%{opacity:0;transform:translateY(14px)}100%{opacity:1;transform:translateY(0)}}
.app-card{
  background:white;border-radius:20px;padding:1.75rem 2rem;margin-bottom:1.25rem;
  box-shadow:0 4px 24px rgba(15,23,42,.07),0 1px 4px rgba(15,23,42,.04);
  border:1px solid #EEF2FF;animation:riseIn .5s cubic-bezier(.22,1,.36,1) both;
}
.app-section-label{
  font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  color:#4F46E5;display:block;margin-bottom:.75rem;
}
.ex-pills{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;}
.ex-pills .stButton>button{
  background:#F8FAFF !important;color:#4F46E5 !important;
  border:1.5px solid #E0E7FF !important;font-size:11.5px !important;
  font-weight:600 !important;padding:4px 12px !important;
  border-radius:999px !important;box-shadow:none !important;
}
.ex-pills .stButton>button:hover{background:#EEF2FF !important;transform:none !important;}
</style>
""", unsafe_allow_html=True)

hdr_a, hdr_b, hdr_spc, hdr_c = st.columns([2.2, 5, 4, 1.5])
with hdr_a:
    st.markdown(
        '<div class="sk-hdr" style="display:flex;align-items:center;gap:9px">'
        '<img src="app/static/skout-logo.png" style="height:30px;width:auto;display:block"></div>',
        unsafe_allow_html=True)
with hdr_b:
    st.markdown(
        '<div style="font-size:13px;font-weight:700;color:#0F172A;'
        'font-family:Poppins,sans-serif">🔍 Discover Creators</div>',
        unsafe_allow_html=True)
with hdr_c:
    if st.button("← Dashboard", use_container_width=True):
        st.switch_page(_P_HOME)
st.markdown("<div style='padding-top:1.5rem'></div>", unsafe_allow_html=True)

EXAMPLES = [
    "vegan skincare micro-influencers in Berlin with Gen-Z audience",
    "tech reviewers in India, 50k+ YouTube subs, Hindi-speaking",
    "dog creators on TikTok, US-based, 10k–100k followers",
    "sustainable fashion, engagement above 5%, Europe",
]

if "disc_query" not in st.session_state:
    st.session_state["disc_query"] = EXAMPLES[0]

# Search card
st.markdown('<div class="app-card">', unsafe_allow_html=True)
st.markdown('<span class="app-section-label">Search brief</span>', unsafe_allow_html=True)

col_q, col_k = st.columns([5, 1])
with col_q:
    query = st.text_area(
        "Describe what you're looking for",
        value=st.session_state["disc_query"],
        height=88,
        placeholder="e.g. beauty creators in Toronto with a Gen-Z female audience, 50K–500K followers",
        label_visibility="collapsed",
    )
    query = query or st.session_state["disc_query"]
with col_k:
    top_k = st.number_input("Results", min_value=1, max_value=50, value=10)
    run = st.button("Search →", use_container_width=True)

# Example pills
st.markdown('<div class="ex-pills">', unsafe_allow_html=True)
for i, ex in enumerate(EXAMPLES):
    if st.button(ex, key=f"ex_{i}"):
        st.session_state["disc_query"] = ex
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)  # close app-card

# ── Results ──
if run:
    st.session_state["disc_query"] = query
    try:
        with st.spinner(""):
            res = discover(query=query, top_k=int(top_k))

        hits = res.get("results", [])
        explanation = res.get("explanation", "")

        st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            margin:20px 0 12px">
  <div style="font-family:var(--fd);font-weight:700;font-size:15px;color:var(--navy)">
    {len(hits)} creator{'s' if len(hits) != 1 else ''} found
  </div>
  {f'<div style="font-size:12.5px;color:var(--muted);max-width:600px">{explanation}</div>' if explanation else ''}
</div>
""", unsafe_allow_html=True)

        if not hits:
            st.markdown("""
<div class="app-card" style="text-align:center;padding:3rem">
  <div style="font-size:2rem;margin-bottom:.75rem">🔍</div>
  <div style="font-family:var(--fd);font-weight:700;color:var(--navy);margin-bottom:.4rem">No matches found</div>
  <div style="font-size:13px;color:var(--muted)">Try broadening your brief or removing location/follower constraints.</div>
</div>
""", unsafe_allow_html=True)
        else:
            for hit in hits:
                render_creator_card(hit)

    except APIError as e:
        st.error(str(e))
else:
    st.markdown("""
<div class="app-card" style="text-align:center;padding:3.5rem 2rem;margin-top:16px">
  <div style="font-size:2.5rem;margin-bottom:1rem">✦</div>
  <div style="font-family:var(--fd);font-weight:700;font-size:16px;color:var(--navy);margin-bottom:.5rem">
    Describe your ideal creator
  </div>
  <div style="font-size:13.5px;color:var(--muted);max-width:420px;margin:0 auto;line-height:1.65">
    Use plain English — platform, niche, location, audience demographics, follower count. The Discovery Agent handles semantic matching.
  </div>
</div>
""", unsafe_allow_html=True)

