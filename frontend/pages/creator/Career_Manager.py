"""SKOUT Creator AI Agent — personalized career manager chat interface."""
from __future__ import annotations

import streamlit as st
from frontend.utils.api_client import (
    APIError,
    creator_agent_chat,
    creator_agent_history,
    get_creator,
)
from frontend.utils.session import clear_session, restore_session
from frontend.utils.styles import _P_CREATOR_DASHBOARD, _P_HOME, inject_css

inject_css()
restore_session()

# ── Auth guard ────────────────────────────────────────────────────────────────
user = st.session_state.get("user")
token = st.session_state.get("user_token", "")
if not user or user.get("role") != "creator":
    st.switch_page(_P_HOME)
    st.stop()

# ── Load creator profile ───────────────────────────────────────────────────────
uid   = user.get("creator_id")
uname = user.get("username", "")
prof: dict = {}
if uid:
    try:
        prof = get_creator(uid)
    except APIError:
        pass

name      = prof.get("display_name") or prof.get("full_name") or uname
niches    = prof.get("niches") or []
city      = prof.get("city") or ""
total_f   = prof.get("total_followers") or 0
eng       = prof.get("avg_engagement_rate") or 0.0
skout_sc  = prof.get("authenticity_score")
open_c    = prof.get("open_to_collabs", True)
rate      = prof.get("min_rate_usd") or 0.0
niche_lbl = niches[0].title() if niches else "Creator"

# ── Page CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Background — indigo gradient matching creator dashboard ── */
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"]{
  background:linear-gradient(150deg,#EEF2FF 0%,#F8FAFF 50%,#EFF6FF 100%) !important;
}
[data-testid="stMainBlockContainer"]{
  padding:0 2.5rem 2rem !important;max-width:100% !important;
}

/* ── Sticky header ── */
[data-testid="stHorizontalBlock"]:has(.sk-hdr){
  background:rgba(255,255,255,.97) !important;
  border-bottom:1px solid #E8EDFF !important;
  box-shadow:0 2px 20px rgba(79,70,229,.08) !important;
  padding:0 2.5rem !important;min-height:56px !important;
  align-items:center !important;
  position:sticky !important;top:0 !important;z-index:1000 !important;
  margin-left:-2.5rem !important;margin-right:-2.5rem !important;
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
  background:#EEF2FF !important;transform:none !important;box-shadow:none !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) .sk-out .stButton>button{
  color:#DC2626 !important;border-color:#FECACA !important;
}
[data-testid="stHorizontalBlock"]:has(.sk-hdr) .sk-out .stButton>button:hover{
  background:#FEF2F2 !important;
}

/* ── Chat messages — indigo accent for assistant ── */
[data-testid="stChatMessage"]{
  background:rgba(255,255,255,.85) !important;
  border:1px solid #E8EDFF !important;
  border-radius:14px !important;
  padding:14px 18px !important;
  margin-bottom:8px !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]){
  border-left:3px solid #6366F1 !important;
  background:white !important;
}

/* ── Welcome card ── */
.ca-welcome{
  background:white;border-radius:20px;
  border:1.5px solid #EEF2FF;
  box-shadow:0 4px 28px rgba(79,70,229,.1);
  padding:1.75rem 1.75rem 1.5rem;
  margin-bottom:1.25rem;
}
.ca-creator-row{
  display:flex;align-items:center;gap:14px;margin-bottom:1.1rem;
}
.ca-avatar{
  width:46px;height:46px;border-radius:13px;flex-shrink:0;
  background:linear-gradient(135deg,#4F46E5,#7C3AED);
  display:flex;align-items:center;justify-content:center;
  font-family:Poppins,sans-serif;font-weight:900;font-size:18px;color:#fff;
  border:3px solid rgba(255,255,255,.3);
  box-shadow:0 4px 14px rgba(79,70,229,.25);
}
.ca-name-block{flex:1;min-width:0;}
.ca-name{
  font-family:Poppins,sans-serif;font-weight:800;font-size:1.05rem;
  color:#0F172A;margin:0 0 3px;line-height:1.1;
}
.ca-sub{font-size:12px;color:#64748B;}
.ca-niche-pill{
  background:#EEF2FF;color:#4F46E5;border:1.5px solid #C7D2FE;
  font-size:11px;font-weight:700;padding:3px 11px;border-radius:999px;
  display:inline-block;margin-left:6px;vertical-align:middle;
}
.ca-status-dot{
  width:8px;height:8px;border-radius:50%;
  display:inline-block;margin-right:5px;vertical-align:middle;
}

/* Stats strip */
.ca-stats{
  display:grid;grid-template-columns:repeat(3,1fr);gap:10px;
  margin-bottom:1.15rem;
}
.ca-stat{
  background:#F8FAFF;border:1px solid #E8EDFF;border-radius:12px;
  padding:.75rem 1rem;text-align:center;
}
.ca-stat-val{
  font-family:Poppins,sans-serif;font-size:1.25rem;font-weight:900;
  color:#4F46E5;line-height:1;
}
.ca-stat-lbl{
  font-size:9.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:#94A3B8;margin-top:3px;
}

/* Suggestion grid */
.ca-grid{
  display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:.25rem;
}
.ca-item{
  background:#F8FAFF;border:1.5px solid #E8EDFF;border-radius:14px;
  padding:.85rem 1rem;
}
.ca-item-icon{font-size:1.1rem;display:block;margin-bottom:.3rem;}
.ca-item-title{font-weight:700;font-size:12.5px;color:#0F172A;margin-bottom:.15rem;}
.ca-item-hint{font-size:11px;color:#64748B;font-style:italic;line-height:1.5;}
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
def _ini(n: str) -> str:
    parts = n.split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else n[:2].upper()


hdr_a, hdr_b, hdr_spc, hdr_c, hdr_d, hdr_e = st.columns([2.2, 1.8, 4, 2.4, 1.1, 0.95])
with hdr_a:
    st.markdown(
        '<div class="sk-hdr" style="display:flex;align-items:center;gap:9px">'
        '<img src="app/static/skout-logo.png" style="height:30px;width:auto;display:block">'
        '</div>',
        unsafe_allow_html=True)
with hdr_b:
    st.markdown(
        '<div style="font-size:13px;font-weight:700;color:#0F172A;'
        'font-family:Poppins,sans-serif">✨ SKOUT Agent</div>',
        unsafe_allow_html=True)
with hdr_spc:
    pass
with hdr_c:
    avail_label = "Available" if open_c else "Unavailable"
    st.markdown(
        f'<div style="display:inline-flex;align-items:center;gap:7px;'
        f'background:#EEF2FF;border:1.5px solid #C7D2FE;'
        f'border-radius:999px;padding:5px 14px 5px 7px;max-width:200px">'
        f'<div style="width:26px;height:26px;border-radius:50%;flex-shrink:0;'
        f'background:linear-gradient(135deg,#4F46E5,#7C3AED);'
        f'display:flex;align-items:center;justify-content:center;'
        f'font-size:11px;font-weight:800;color:#fff">🎤</div>'
        f'<span style="font-size:12px;color:#3730A3;font-weight:700;'
        f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap">@{uname}</span>'
        f'</div>',
        unsafe_allow_html=True)
with hdr_d:
    if st.button("← Dashboard", key="ca_dash"):
        st.switch_page(_P_CREATOR_DASHBOARD)
with hdr_e:
    st.markdown('<div class="sk-out">', unsafe_allow_html=True)
    if st.button("Log out", key="ca_logout"):
        clear_session()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='padding-top:1.5rem'></div>", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "ca_msgs" not in st.session_state:
    st.session_state.ca_msgs   = []
    st.session_state.ca_loaded = False

# ── Load conversation history once per session ────────────────────────────────
if not st.session_state.ca_loaded:
    with st.spinner("Loading your conversation…"):
        try:
            st.session_state.ca_msgs = creator_agent_history(token)
        except APIError:
            pass
    st.session_state.ca_loaded = True


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt_num(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


# ── Chat layout ───────────────────────────────────────────────────────────────
_, chat_col, _ = st.columns([0.06, 1, 0.06])
with chat_col:

    # Welcome card — shown only for empty conversations
    if not st.session_state.ca_msgs:
        avail_dot_color = "#10B981" if open_c else "#F59E0B"
        skout_display   = f"{skout_sc:.0f}" if skout_sc is not None else "—"

        st.markdown(
            f'<div class="ca-welcome">'

            f'<div class="ca-creator-row">'
            f'<div class="ca-avatar">{_ini(name)}</div>'
            f'<div class="ca-name-block">'
            f'<div class="ca-name">{name}'
            f'<span class="ca-niche-pill">{niche_lbl}</span>'
            f'</div>'
            f'<div class="ca-sub">'
            f'<span class="ca-status-dot" style="background:{avail_dot_color}"></span>'
            f'{avail_label}'
            + (f' &nbsp;·&nbsp; 📍 {city}' if city else '')
            + f'</div>'
            f'</div>'
            f'</div>'

            f'<div class="ca-stats">'
            f'<div class="ca-stat"><div class="ca-stat-val">{_fmt_num(total_f)}</div>'
            f'<div class="ca-stat-lbl">Followers</div></div>'
            f'<div class="ca-stat"><div class="ca-stat-val">{eng:.1f}%</div>'
            f'<div class="ca-stat-lbl">Engagement</div></div>'
            f'<div class="ca-stat"><div class="ca-stat-val">{skout_display}</div>'
            f'<div class="ca-stat-lbl">SKOUT Score</div></div>'
            f'</div>'

            f'<div style="font-family:Poppins,sans-serif;font-weight:800;font-size:1.1rem;'
            f'color:#0F172A;margin-bottom:.35rem">Hey {name.split()[0]}, I\'m your career manager</div>'
            f'<div style="font-size:13.5px;color:#64748B;line-height:1.7;margin-bottom:1.1rem">'
            f'I know your real numbers — {_fmt_num(total_f)} followers, {eng:.1f}% engagement'
            + (f', based in {city}' if city else '')
            + f'. Use me to set smart rates, craft pitches, and land better brand deals.'
            f'</div>'

            f'<div class="ca-grid">'
            f'<div class="ca-item"><span class="ca-item-icon">💰</span>'
            f'<div class="ca-item-title">Rate card</div>'
            f'<div class="ca-item-hint">"What should I charge for a sponsored reel?"</div></div>'

            f'<div class="ca-item"><span class="ca-item-icon">📝</span>'
            f'<div class="ca-item-title">Pitch a brand</div>'
            f'<div class="ca-item-hint">"Write a pitch to a local café in {city or "my city"}"</div></div>'

            f'<div class="ca-item"><span class="ca-item-icon">✏️</span>'
            f'<div class="ca-item-title">Bio review</div>'
            f'<div class="ca-item-hint">"Review my bio and suggest improvements"</div></div>'

            f'<div class="ca-item"><span class="ca-item-icon">🤝</span>'
            f'<div class="ca-item-title">Negotiate a deal</div>'
            f'<div class="ca-item-hint">"A brand offered $200, how should I respond?"</div></div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Message history
    for msg in st.session_state.ca_msgs:
        role   = msg.get("role", "user")
        avatar = "✨" if role == "assistant" else "🎤"
        with st.chat_message(role, avatar=avatar):
            st.markdown(msg.get("content", ""))

    # ── Chat input ────────────────────────────────────────────────────────────
    no_profile = not uid or not prof
    placeholder = (
        "Complete your creator onboarding to use the AI Agent…"
        if no_profile
        else "Ask about rates, pitches, brand negotiation, content strategy…"
    )

    if prompt := st.chat_input(placeholder, disabled=no_profile):
        st.session_state.ca_msgs.append({"role": "user", "content": prompt})

        with st.spinner("Thinking…"):
            try:
                resp = creator_agent_chat(prompt, token)
                st.session_state.ca_msgs.append(resp)
            except APIError as err:
                err_msg = str(err)
                hint = ""
                if "GROQ_API_KEY" in err_msg:
                    hint = "\n\nAdd `GROQ_API_KEY=your_key` to your `.env` file and restart the backend. Get a free key at console.groq.com."
                elif "503" in err_msg:
                    hint = "\n\nMake sure the backend is running: `uvicorn backend.main:app --reload`"
                st.session_state.ca_msgs.append({
                    "role": "assistant",
                    "content": f"⚠️ {err_msg}{hint}",
                })
        st.rerun()

    if no_profile:
        st.markdown(
            '<div style="text-align:center;padding:1rem 0;font-size:13px;color:#94A3B8">'
            '👆 Complete your '
            '<a href="/Creator_Onboarding" target="_self" '
            'style="color:#6366F1;font-weight:600;text-decoration:none">creator onboarding</a>'
            ' to unlock your AI career manager.</div>',
            unsafe_allow_html=True,
        )
