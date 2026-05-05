"""AI Outreach — draft personalized creator messages."""
from __future__ import annotations

import streamlit as st

from frontend.utils.api_client import APIError, draft_outreach, get_creator, list_creators
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
.draft-card{
  background:#F8FAFF;border:1.5px solid #E0E7FF;border-radius:16px;
  padding:1.25rem 1.4rem;font-size:13.5px;color:#0F172A;
  line-height:1.8;white-space:pre-wrap;
}
.draft-subject{
  background:#EEF2FF;border:1.5px solid #C7D2FE;border-radius:10px;
  padding:8px 14px;font-size:12px;font-weight:600;color:#3730A3;margin-bottom:10px;
}
.draft-subject span{font-weight:400;color:#4F46E5;}
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
        'font-family:Poppins,sans-serif">✉️ AI Outreach</div>',
        unsafe_allow_html=True)
with hdr_c:
    if st.button("← Dashboard", use_container_width=True):
        st.switch_page(_P_HOME)
st.markdown("<div style='padding-top:1.5rem'></div>", unsafe_allow_html=True)

left, right = st.columns([1, 1], gap="large")

# ── LEFT: inputs ──
with left:
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown('<span class="app-section-label">Creator</span>', unsafe_allow_html=True)

    # Pre-fill from session (set by Campaigns/Discover pages via switch_page)
    prefill_id = st.session_state.get("outreach_creator_id", "")

    search_term = st.text_input(
        "Search by name or Instagram handle",
        placeholder="e.g. Priya  or  @priyastyles",
    )

    creator_data = None
    creator_id   = prefill_id  # may be overridden below

    if search_term:
        # Search client-side from full creator list
        try:
            all_rows = list_creators(limit=200)
        except APIError:
            all_rows = []
        q = search_term.lstrip("@").lower()
        matched = [
            r for r in all_rows
            if q in (r.get("display_name") or "").lower()
            or q in ((r.get("handles") or {}).get("instagram") or "").lstrip("@").lower()
        ]
        if not matched:
            st.warning("No creators found. Try a different name or handle.")
        else:
            options = {
                f"{r.get('display_name') or r.get('full_name') or 'Unknown'}"
                f" — @{((r.get('handles') or {}).get('instagram') or '—')}": r["id"]
                for r in matched
            }
            chosen = st.selectbox("Select creator", list(options.keys())) if len(options) > 1 else list(options.keys())[0]
            creator_id = options[chosen]
    elif prefill_id:
        # Came from another page with a known ID — keep using it silently
        pass

    if creator_id:
        try:
            creator_data = get_creator(creator_id)
        except APIError as e:
            st.warning(str(e))

    if creator_data:
        name    = creator_data.get("display_name") or "—"
        country = creator_data.get("country") or ""
        bio     = creator_data.get("bio") or ""
        niches  = creator_data.get("niches") or []
        niche_tags = "".join(
            f'<span style="background:var(--blue-50);border:1px solid var(--blue-100);'
            f'color:var(--blue-700);border-radius:5px;font-size:11px;font-weight:600;'
            f'padding:2px 8px;margin-right:4px;font-family:var(--fb)">{n}</span>'
            for n in niches[:4]
        )
        bio_line = f'<div style="font-size:12px;color:var(--muted);line-height:1.5">{bio[:120]}{"…" if len(bio)>120 else ""}</div>' if bio else ""
        st.markdown(
            '<div style="background:var(--bg-alt);border:1px solid var(--border);border-radius:8px;padding:10px 14px;margin:-4px 0 12px">'
            f'<div style="font-family:var(--fd);font-weight:700;font-size:14px;color:var(--navy);margin-bottom:4px">{name} <span style="font-weight:400;color:var(--muted);font-size:12px">· {country}</span></div>'
            f'<div style="margin-bottom:4px">{niche_tags}</div>'
            f'{bio_line}'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<span class="app-section-label" style="margin-top:16px">Campaign brief</span>', unsafe_allow_html=True)

    brand_name = st.text_input("Brand name", value="AuraGlow")
    campaign_brief = st.text_area(
        "Brief",
        height=130,
        value="We're launching a clean-beauty serum targeting Gen-Z. "
              "Looking for 1 reel + 3 stories within 2 weeks. Budget flexible.",
    )

    c1, c2 = st.columns(2)
    tone    = c1.selectbox("Tone",    ["friendly-professional", "casual", "formal"])
    channel = c2.selectbox("Channel", ["email", "instagram_dm", "tiktok_dm"])

    draft_btn = st.button("✨ Generate draft", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── RIGHT: output ──
with right:
    if draft_btn:
        if not creator_id:
            st.error("Search for a creator first.")
        else:
            try:
                with st.spinner(""):
                    draft = draft_outreach({
                        "creator_id":     creator_id,
                        "brand_name":     brand_name,
                        "campaign_brief": campaign_brief,
                        "tone":           tone,
                        "channel":        channel,
                    })

                subject = draft.get("subject", "")
                body    = draft.get("body", "")

                st.markdown(f"""
<div style="margin-bottom:12px">
  <div style="display:inline-flex;align-items:center;gap:6px;
              background:var(--blue-50);border:1px solid var(--blue-100);
              color:var(--blue-600);border-radius:6px;
              font-family:var(--fd);font-size:11px;font-weight:700;
              padding:3px 10px;letter-spacing:.06em;text-transform:uppercase;
              margin-bottom:10px">
    Draft ready
  </div>
  <div style="font-family:var(--fd);font-weight:700;font-size:15px;color:var(--navy)">
    {channel.replace("_", " ").title()} message
    {f'<span style="font-size:13px;font-weight:500;color:var(--muted);margin-left:8px">→ {creator_data.get("display_name","") if creator_data else ""}</span>' if creator_data else ""}
  </div>
</div>
""", unsafe_allow_html=True)

                if subject and channel == "email":
                    st.markdown(f"""
<div class="draft-subject">Subject line <span>— {subject}</span></div>
""", unsafe_allow_html=True)

                st.markdown(f'<div class="draft-card">{body}</div>', unsafe_allow_html=True)

                st.markdown("""
<div style="margin-top:10px;font-size:12px;color:var(--muted);display:flex;align-items:center;gap:5px">
  💡 Always personalise before sending. A/B test subject lines.
</div>
""", unsafe_allow_html=True)

                with st.expander("Edit & copy"):
                    st.text_area("Message body", value=body, height=260)

            except APIError as e:
                st.error(str(e))

    elif st.session_state.get("outreach_creator_id"):
        st.markdown("""
<div class="app-card" style="text-align:center;padding:3rem">
  <div style="font-size:1.8rem;margin-bottom:.6rem">✉️</div>
  <div style="font-family:var(--fd);font-weight:700;font-size:15px;color:var(--navy);margin-bottom:.4rem">
    Ready to draft
  </div>
  <div style="font-size:13px;color:var(--muted)">
    Creator loaded. Fill the brief and click <strong>Generate draft</strong>.
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div class="app-card" style="text-align:center;padding:3.5rem 2rem">
  <div style="font-size:2.2rem;margin-bottom:.75rem">✦</div>
  <div style="font-family:var(--fd);font-weight:700;font-size:15px;color:var(--navy);margin-bottom:.4rem">
    Your draft appears here
  </div>
  <div style="font-size:13px;color:var(--muted);line-height:1.65;max-width:360px;margin:0 auto">
    Enter a creator ID (from Discover or Filter), fill the campaign brief, and hit Generate.
  </div>
</div>
""", unsafe_allow_html=True)

