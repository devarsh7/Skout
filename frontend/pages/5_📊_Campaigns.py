"""Campaigns & Creator Directory."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from frontend.utils.api_client import APIError, get_creator, list_creators
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
.metric-row{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:1.25rem;}
.metric-box{
  background:white;border-radius:18px;padding:1.2rem 1.4rem;
  box-shadow:0 4px 20px rgba(15,23,42,.07),0 1px 3px rgba(15,23,42,.04);
  border:1px solid #EEF2FF;animation:riseIn .5s cubic-bezier(.22,1,.36,1) both;
}
.metric-label{font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#94A3B8;margin-bottom:6px;}
.metric-value{font-family:Poppins,sans-serif;font-size:1.6rem;font-weight:900;color:#4F46E5;line-height:1;margin-bottom:4px;}
.metric-sub{font-size:12px;color:#64748B;}
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
        'font-family:Poppins,sans-serif">📊 Campaigns & Directory</div>',
        unsafe_allow_html=True)
with hdr_c:
    if st.button("← Dashboard", use_container_width=True):
        st.switch_page(_P_HOME)
st.markdown("<div style='padding-top:1.5rem'></div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Creator Directory", "Campaign Tracker"])

with tab1:
    col_limit, _ = st.columns([1, 4])
    with col_limit:
        limit = st.select_slider("Show", [10, 25, 50, 100, 200], value=50)

    try:
        rows = list_creators(limit=limit)
    except APIError as e:
        st.error(str(e))
        rows = []

    if not rows:
        st.markdown("""
<div class="app-card" style="text-align:center;padding:3rem;margin-top:16px">
  <div style="font-size:2rem;margin-bottom:.75rem">👤</div>
  <div style="font-family:var(--fd);font-weight:700;font-size:15px;color:var(--navy);margin-bottom:.4rem">
    No creators yet
  </div>
  <div style="font-size:13px;color:var(--muted);max-width:360px;margin:0 auto;line-height:1.65">
    Share the Creator Onboarding page to start building your roster.
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        total = len(rows)
        avg_eng = sum((r.get("avg_engagement_rate") or 0) for r in rows) / max(total, 1) * 100
        total_reach = sum(r.get("total_followers", 0) or 0 for r in rows)
        open_to_collabs = sum(1 for r in rows if r.get("open_to_collabs", True))

        st.markdown(f"""
<div class="metric-row">
  <div class="metric-box">
    <div class="metric-label">Total creators</div>
    <div class="metric-value">{total:,}</div>
    <div class="metric-sub">in directory</div>
  </div>
  <div class="metric-box">
    <div class="metric-label">Total reach</div>
    <div class="metric-value">{"%.1fM" % (total_reach/1_000_000) if total_reach>=1_000_000 else "%.0fK" % (total_reach/1_000)}</div>
    <div class="metric-sub">combined followers</div>
  </div>
  <div class="metric-box">
    <div class="metric-label">Avg engagement</div>
    <div class="metric-value">{avg_eng:.2f}%</div>
    <div class="metric-sub">across all creators</div>
  </div>
  <div class="metric-box">
    <div class="metric-label">Open to collabs</div>
    <div class="metric-value">{open_to_collabs}</div>
    <div class="metric-sub">available now</div>
  </div>
</div>
""", unsafe_allow_html=True)

        df = pd.DataFrame([
            {
                "Name":       r.get("display_name") or "—",
                "Country":    r.get("country") or "—",
                "Niches":     ", ".join(r.get("niches", [])[:3]),
                "Followers":  r.get("total_followers", 0) or 0,
                "Engagement": round((r.get("avg_engagement_rate") or 0) * 100, 2),
                "Instagram":  (r.get("handles") or {}).get("instagram") or "—",
                "TikTok":     (r.get("handles") or {}).get("tiktok") or "—",
                "Open":       "✓" if r.get("open_to_collabs", True) else "–",
                "id":         r["id"],
            }
            for r in rows
        ])

        st.dataframe(
            df.drop(columns=["id"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Followers":  st.column_config.NumberColumn(format="%d"),
                "Engagement": st.column_config.NumberColumn(format="%.2f%%"),
            },
        )

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.markdown('<span class="app-section-label">Creator detail</span>', unsafe_allow_html=True)

        search_term = st.text_input(
            "Search by name or Instagram handle",
            placeholder="e.g. Priya  or  @priyastyles",
        )

        # Filter loaded rows client-side — no extra API call needed
        matched = []
        if search_term and rows:
            q = search_term.lstrip("@").lower()
            for r in rows:
                name_match = q in (r.get("display_name") or "").lower()
                ig = ((r.get("handles") or {}).get("instagram") or "").lstrip("@").lower()
                ig_match = q in ig
                if name_match or ig_match:
                    matched.append(r)

        if search_term and not matched:
            st.markdown(
                '<div style="font-size:13px;color:var(--muted);padding:8px 0">'
                'No creators found. Try a different name or handle.</div>',
                unsafe_allow_html=True,
            )
        elif matched:
            # Show a selectbox if multiple matches
            options = {
                f"{r.get('display_name') or r.get('full_name') or 'Unknown'}"
                f" — @{((r.get('handles') or {}).get('instagram') or '—')}": r["id"]
                for r in matched
            }
            chosen_label = st.selectbox("Select creator", list(options.keys())) if len(options) > 1 else list(options.keys())[0]
            selected_id = options[chosen_label]

            try:
                c = get_creator(selected_id)
                handles = c.get("handles") or {}
                niches  = c.get("niches") or []
                niche_html = "".join(
                    f'<span style="background:var(--blue-50);border:1px solid var(--blue-100);'
                    f'color:var(--blue-700);border-radius:5px;font-size:11px;font-weight:600;'
                    f'padding:2px 8px;margin-right:4px">{n}</span>'
                    for n in niches[:5]
                )
                handles_rows = "".join(
                    f'<div style="font-size:13px;color:var(--muted);margin-bottom:4px">'
                    f'<strong style="color:var(--navy)">{k.title()}:</strong> @{v}</div>'
                    for k, v in handles.items() if v
                ) or '<div style="font-size:13px;color:var(--muted)">None on file</div>'

                html = (
                    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;padding:4px 0">'
                    '<div>'
                    f'<div style="font-family:var(--fd);font-weight:700;font-size:16px;color:var(--navy);margin-bottom:6px">{c.get("display_name") or c.get("full_name") or "—"}</div>'
                    f'<div style="margin-bottom:8px">{niche_html}</div>'
                    f'<div style="font-size:13px;color:var(--muted);line-height:1.8">'
                    f'<strong style="color:var(--navy)">Email:</strong> {c.get("email") or "—"}<br>'
                    f'<strong style="color:var(--navy)">Phone:</strong> {c.get("phone") or "—"}<br>'
                    f'<strong style="color:var(--navy)">Location:</strong> {", ".join(filter(None, [c.get("city"), c.get("country")])) or "—"}'
                    '</div>'
                    '</div>'
                    '<div>'
                    '<div style="font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--subtle);margin-bottom:8px">Handles</div>'
                    f'{handles_rows}'
                    '</div>'
                    '</div>'
                )
                st.markdown(html, unsafe_allow_html=True)

                if st.button("✉️ Draft outreach to this creator"):
                    st.session_state["outreach_creator_id"] = selected_id
                    st.switch_page("pages/4_✉️_AI_Outreach.py")

            except APIError as e:
                st.error(str(e))
        else:
            st.markdown(
                '<div style="font-size:13px;color:var(--muted);padding:8px 0">'
                'Type a name or Instagram handle above to view contact info and social handles.</div>',
                unsafe_allow_html=True,
            )

        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("""
<div class="app-card" style="margin-top:8px">
  <div style="display:flex;align-items:start;gap:16px">
    <div style="font-size:2rem">🚧</div>
    <div>
      <div style="font-family:var(--fd);font-weight:700;font-size:15px;color:var(--navy);margin-bottom:4px">
        Campaign tracker — coming in v1.1
      </div>
      <div style="font-size:13px;color:var(--muted);line-height:1.7;max-width:560px">
        Full Kanban board already modelled in the backend.
        States: <code>drafted → sent → opened → replied → negotiating → booked / declined</code>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px">
  <div class="app-card" style="opacity:.55;pointer-events:none">
    <div style="font-family:var(--fd);font-weight:700;font-size:13px;color:var(--navy);margin-bottom:6px">📤 Sent (0)</div>
    <div style="height:60px;border:1.5px dashed var(--border);border-radius:8px"></div>
  </div>
  <div class="app-card" style="opacity:.55;pointer-events:none">
    <div style="font-family:var(--fd);font-weight:700;font-size:13px;color:var(--navy);margin-bottom:6px">💬 Replied (0)</div>
    <div style="height:60px;border:1.5px dashed var(--border);border-radius:8px"></div>
  </div>
  <div class="app-card" style="opacity:.55;pointer-events:none">
    <div style="font-family:var(--fd);font-weight:700;font-size:13px;color:var(--navy);margin-bottom:6px">🤝 Booked (0)</div>
    <div style="height:60px;border:1.5px dashed var(--border);border-radius:8px"></div>
  </div>
</div>
""", unsafe_allow_html=True)

