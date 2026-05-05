"""AI Agent — SKOUT Assistant chat interface."""
from __future__ import annotations

import streamlit as st
from frontend.utils.api_client import (
    APIError,
    agent_action_save_creators,
    agent_action_send_outreach,
    agent_action_use_brief,
    agent_chat,
    agent_history,
    agent_notifications,
)
from frontend.utils.session import restore_session
from frontend.utils.styles import _P_HOME, inject_css

inject_css()
restore_session()

# ── Auth guard ────────────────────────────────────────────────────────────────
user  = st.session_state.get("user")
token = st.session_state.get("user_token", "")
if not user:
    st.switch_page(_P_HOME)

meta    = user.get("profile_meta") or {}
company = meta.get("company_name") or f"@{user.get('username', '')}"

# ── Page CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"]{
  background:linear-gradient(150deg,#EEF2FF 0%,#F8FAFF 50%,#EFF6FF 100%) !important;
}
[data-testid="stMainBlockContainer"]{
  padding:0 2.5rem 2rem !important;max-width:100% !important;
}

/* Sticky header */
[data-testid="stHorizontalBlock"]:has(.sk-hdr){
  background:rgba(255,255,255,.97) !important;
  border-bottom:1px solid #E8EDFF !important;
  box-shadow:0 2px 20px rgba(79,70,229,.08) !important;
  padding:0 2.5rem !important;min-height:56px !important;
  align-items:center !important;
  position:sticky !important;top:0 !important;z-index:1000 !important;
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

/* Creator chip cards inside messages */
.creator-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;}
.creator-chip{
  background:#F8FAFF;border:1.5px solid #E0E7FF;border-radius:12px;
  padding:8px 14px;font-size:12px;color:#1E1B4B;line-height:1.6;
}
.creator-chip strong{display:block;font-size:13px;color:#3730A3;margin-bottom:1px;}

/* Done badge */
.done-badge{
  display:inline-flex;align-items:center;gap:5px;
  background:#ECFDF5;border:1.5px solid #A7F3D0;
  border-radius:999px;padding:3px 12px;
  font-size:11.5px;font-weight:600;color:#065F46;margin-top:10px;
}

/* Notification banner */
.notif-banner{
  background:#FFF7ED;border:1.5px solid #FED7AA;border-radius:14px;
  padding:10px 16px;margin-bottom:8px;
  font-size:13px;color:#92400E;line-height:1.7;
}

/* Welcome card */
.welcome-card{
  background:white;border-radius:20px;
  border:1.5px solid #EEF2FF;
  box-shadow:0 4px 24px rgba(79,70,229,.08);
  padding:1.75rem 1.75rem 1.5rem;margin-bottom:1.25rem;
}
.welcome-grid{
  display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:1.2rem;
}
.welcome-item{
  background:#F8FAFF;border:1px solid #E8EDFF;border-radius:14px;padding:1rem;
}
.welcome-item-icon{font-size:1.3rem;display:block;margin-bottom:.35rem;}
.welcome-item-title{font-weight:700;font-size:13px;color:#0F172A;margin-bottom:.2rem;}
.welcome-item-hint{font-size:11.5px;color:#64748B;font-style:italic;}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
hdr_a, hdr_b, hdr_spc, hdr_c = st.columns([2.2, 5, 4, 1.5])
with hdr_a:
    st.markdown(
        '<div class="sk-hdr" style="display:flex;align-items:center;gap:9px">'
        '<img src="app/static/skout-logo.png" style="height:30px;width:auto;display:block"></div>',
        unsafe_allow_html=True)
with hdr_b:
    st.markdown(
        '<div style="font-size:13px;font-weight:700;color:#0F172A;'
        'font-family:Poppins,sans-serif">🤖 SKOUT Assistant</div>',
        unsafe_allow_html=True)
with hdr_c:
    if st.button("← Dashboard", use_container_width=True):
        st.switch_page(_P_HOME)

st.markdown("<div style='padding-top:1.5rem'></div>", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "agent_msgs" not in st.session_state:
    st.session_state.agent_msgs         = []
    st.session_state.agent_loaded       = False
    st.session_state.agent_notifs       = []
    st.session_state.agent_action_done  = set()   # msg indices whose action was executed

# ── Load history + notifications once per session ─────────────────────────────
if not st.session_state.agent_loaded:
    with st.spinner("Loading your conversation…"):
        try:
            st.session_state.agent_msgs = agent_history(token)
        except APIError:
            pass
        try:
            resp = agent_notifications(token)
            st.session_state.agent_notifs = resp.get("notifications", [])
        except APIError:
            pass
    st.session_state.agent_loaded = True

# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt_num(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def _render_creator_cards(creators: list[dict]) -> None:
    chips = "".join(
        f'<div class="creator-chip">'
        f'<strong>{c.get("name", "")}</strong>'
        f'{c.get("city", "")}'
        + (f' · {", ".join(c["niches"][:2])}' if c.get("niches") else "")
        + f'<br>{_fmt_num(c.get("total_followers", 0))} followers'
        + f' · {c.get("engagement_pct", 0):.1f}% eng'
        + (f'<br><span style="color:#6366F1">@{c["instagram"]}</span>'
           if c.get("instagram") else "")
        + f'</div>'
        for c in creators
    )
    st.markdown(f'<div class="creator-row">{chips}</div>', unsafe_allow_html=True)


def _render_action_buttons(msg_idx: int, action_data: dict) -> None:
    if msg_idx in st.session_state.agent_action_done:
        st.markdown('<div class="done-badge">✓ Done</div>', unsafe_allow_html=True)
        return

    a_type  = action_data.get("type")
    actions = action_data.get("actions", [])

    if a_type == "creator_list":
        _render_creator_cards(action_data.get("creators", []))

    btn_col, _ = st.columns([2, 5])
    with btn_col:
        if "save_creators" in actions:
            if st.button("⭐ Save these creators", key=f"save_{msg_idx}",
                         type="primary", use_container_width=True):
                creators = action_data.get("creators", [])
                try:
                    result = agent_action_save_creators(
                        [c["id"] for c in creators],
                        [c["name"] for c in creators],
                        token,
                    )
                    st.success(result.get("message", "Saved!"))
                    st.session_state.agent_action_done.add(msg_idx)
                    st.rerun()
                except APIError as exc:
                    st.error(str(exc))

        elif "use_brief" in actions:
            if st.button("📋 Save as campaign", key=f"brief_{msg_idx}",
                         type="primary", use_container_width=True):
                try:
                    result = agent_action_use_brief(
                        action_data.get("brief_text", ""),
                        f"{company} Campaign",
                        token,
                    )
                    st.success(result.get("message", "Brief saved!"))
                    st.session_state.agent_action_done.add(msg_idx)
                    st.rerun()
                except APIError as exc:
                    st.error(str(exc))

        elif "send_outreach" in actions:
            creator_name = action_data.get("creator_name", "this creator")
            if st.button(f"✉️ Record outreach to {creator_name}", key=f"outreach_{msg_idx}",
                         type="primary", use_container_width=True):
                try:
                    result = agent_action_send_outreach(action_data["creator_id"], token)
                    st.success(result.get("message", "Outreach recorded!"))
                    st.session_state.agent_action_done.add(msg_idx)
                    st.rerun()
                except APIError as exc:
                    st.error(str(exc))


# ── Chat layout ───────────────────────────────────────────────────────────────
_, chat_col, _ = st.columns([0.08, 1, 0.08])
with chat_col:

    # Proactive notification banners
    for notif in st.session_state.agent_notifs:
        st.markdown(f'<div class="notif-banner">🔔 {notif}</div>', unsafe_allow_html=True)

    # Welcome card (empty conversation)
    if not st.session_state.agent_msgs:
        st.markdown(
            f'<div class="welcome-card">'
            f'<div style="font-size:1.5rem;margin-bottom:.5rem">🤖</div>'
            f'<div style="font-family:Poppins,sans-serif;font-weight:800;font-size:1.15rem;'
            f'color:#0F172A;margin-bottom:.3rem">Hey, I\'m your SKOUT Assistant</div>'
            f'<div style="font-size:13.5px;color:#64748B;line-height:1.7">'
            f'I can help <strong>{company}</strong> find creators, draft campaign briefs, '
            f'analyse outreach, and more. What do you need today?'
            f'</div>'
            f'<div class="welcome-grid">'
            f'<div class="welcome-item"><span class="welcome-item-icon">🔍</span>'
            f'<div class="welcome-item-title">Find creators</div>'
            f'<div class="welcome-item-hint">"Find food creators in Toronto"</div></div>'
            f'<div class="welcome-item"><span class="welcome-item-icon">📋</span>'
            f'<div class="welcome-item-title">Write a brief</div>'
            f'<div class="welcome-item-hint">"Draft a brief for a summer launch"</div></div>'
            f'<div class="welcome-item"><span class="welcome-item-icon">✉️</span>'
            f'<div class="welcome-item-title">Outreach help</div>'
            f'<div class="welcome-item-hint">"Draft a DM to beauty creators"</div></div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Message history
    for idx, msg in enumerate(st.session_state.agent_msgs):
        role   = msg.get("role", "user")
        avatar = "🤖" if role == "assistant" else "👤"
        with st.chat_message(role, avatar=avatar):
            st.markdown(msg.get("content", ""))
            if role == "assistant" and msg.get("action_data"):
                _render_action_buttons(idx, msg["action_data"])

    # Chat input (fixed to bottom by Streamlit)
    if prompt := st.chat_input("Ask about creators, campaigns, outreach strategy…"):
        st.session_state.agent_msgs.append(
            {"role": "user", "content": prompt, "action_data": None}
        )
        with st.spinner("Thinking…"):
            try:
                response = agent_chat(prompt, token)
                st.session_state.agent_msgs.append(response)
            except APIError as err:
                st.session_state.agent_msgs.append({
                    "role": "assistant",
                    "content": (
                        f"⚠️ Something went wrong: {err}\n\n"
                        "Make sure the backend is running and `GROQ_API_KEY` is set in `.env`."
                    ),
                    "action_data": None,
                })
        st.rerun()
