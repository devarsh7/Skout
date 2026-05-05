"""Filter & Refine — structured filters + semantic query."""
from __future__ import annotations

import streamlit as st

from frontend.components.creator_card import render_creator_card
from frontend.utils.api_client import APIError, filter_search
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
        'font-family:Poppins,sans-serif">🎯 Filter & Refine</div>',
        unsafe_allow_html=True)
with hdr_c:
    if st.button("← Dashboard", use_container_width=True):
        st.switch_page(_P_HOME)
st.markdown("<div style='padding-top:1.5rem'></div>", unsafe_allow_html=True)

left, right = st.columns([1, 2], gap="large")

with left:
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown('<span class="app-section-label">Filters</span>', unsafe_allow_html=True)

    query = st.text_area(
        "Semantic hint (optional)",
        placeholder="e.g. 'engaged foodie with strong storytelling'",
        height=68,
    )

    platforms = st.multiselect(
        "Platforms",
        ["instagram", "tiktok", "youtube", "facebook", "twitter"],
        default=["instagram"],
    )
    niches = st.multiselect(
        "Niches",
        ["beauty", "fashion", "fitness", "food", "travel", "gaming", "tech",
         "parenting", "education", "business", "finance", "lifestyle",
         "art", "music", "sports", "automotive", "home-decor", "sustainability", "pets", "books"],
    )
    languages = st.multiselect(
        "Languages",
        ["en", "hi", "es", "fr", "de", "pt", "ja", "ko", "zh", "ar"],
    )
    countries = st.multiselect(
        "Creator country",
        ["US", "IN", "GB", "BR", "DE", "FR", "CA", "AU", "JP", "MX", "ES", "IT", "NL", "AE", "SG"],
    )
    audience_countries = st.multiselect(
        "Audience country focus",
        ["US", "IN", "GB", "BR", "DE", "FR", "CA", "AU", "JP", "MX"],
    )
    cities = st.text_input("Cities", placeholder="Mumbai, Berlin, Austin")

    min_f, max_f = st.select_slider(
        "Follower range",
        options=[1_000, 5_000, 10_000, 25_000, 50_000, 100_000,
                 250_000, 500_000, 1_000_000, 5_000_000, 10_000_000],
        value=(1_000, 500_000),
    )

    min_engagement_pct = st.slider("Min engagement rate (%)", 0.0, 20.0, 0.0, step=0.5, format="%.1f%%")
    min_engagement = min_engagement_pct / 100
    top_k = st.slider("Max results", 5, 100, 20, step=5)

    c1, c2 = st.columns(2)
    verified_only = c1.checkbox("Verified only")
    open_only     = c2.checkbox("Open to collabs", value=True)

    run = st.button("Apply Filters →", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    if run:
        filters = {
            "platforms":           platforms,
            "niches":              niches,
            "languages":           languages,
            "countries":           countries,
            "cities":              [c.strip() for c in cities.split(",") if c.strip()],
            "min_total_followers": int(min_f),
            "max_total_followers": int(max_f),
            "min_engagement_rate": float(min_engagement),
            "audience_countries":  audience_countries,
            "verified_only":       verified_only,
            "open_to_collabs_only": open_only,
        }
        try:
            with st.spinner(""):
                res = filter_search(filters=filters, query=query or None, top_k=top_k)

            hits = res.get("results", [])
            explanation = res.get("explanation", "")

            st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
  <div style="font-family:var(--fd);font-weight:700;font-size:15px;color:var(--navy)">
    {len(hits)} result{'s' if len(hits) != 1 else ''}
  </div>
  {f'<div style="font-size:12px;color:var(--muted);max-width:480px">{explanation}</div>' if explanation else ''}
</div>
""", unsafe_allow_html=True)

            if not hits:
                st.markdown("""
<div class="app-card" style="text-align:center;padding:2.5rem">
  <div style="font-size:1.8rem;margin-bottom:.6rem">🎯</div>
  <div style="font-family:var(--fd);font-weight:700;color:var(--navy);margin-bottom:.3rem">No matches</div>
  <div style="font-size:12.5px;color:var(--muted)">Loosen your filters to see more creators.</div>
</div>
""", unsafe_allow_html=True)
            else:
                for hit in hits:
                    render_creator_card(hit)

        except APIError as e:
            st.error(str(e))
    else:
        st.markdown("""
<div class="app-card" style="text-align:center;padding:3.5rem 2rem">
  <div style="font-size:2rem;margin-bottom:.75rem">🎛️</div>
  <div style="font-family:var(--fd);font-weight:700;font-size:15px;color:var(--navy);margin-bottom:.4rem">
    Set your filters
  </div>
  <div style="font-size:13px;color:var(--muted);line-height:1.65;max-width:360px;margin:0 auto">
    Choose platforms, niches, follower range, and engagement thresholds. Results appear here.
  </div>
</div>
""", unsafe_allow_html=True)

