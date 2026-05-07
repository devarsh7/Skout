"""Login page — styled to match the Skout homepage theme."""
from __future__ import annotations

import streamlit as st

from frontend.utils.api_client import APIError, login_user
from frontend.utils.session import save_session
from frontend.utils.styles import _P_BUSINESS, _P_CREATOR, _P_HOME, inject_css, render_navbar

inject_css()
render_navbar()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
:root{
  --ind-600:#4F46E5;--vio-600:#7C3AED;
  --ind-100:#E0E7FF;--ind-200:#C7D2FE;
  --mk-navy:#1E1B4B;--mk-muted:#6B7280;
}

[data-testid="stMain"]{
  background:linear-gradient(165deg,#F0EFFF 0%,#EEF0FF 45%,#F5F3FF 100%) !important;
  min-height:100vh;
}
[data-testid="stMainBlockContainer"]{padding-top:0 !important;padding-bottom:0 !important;}
[data-testid="stVerticalBlock"]{gap:0 !important;}
.stMarkdown{margin:0 !important;padding:0 !important;}

/* page top spacing */
.lp-top{padding-top:2rem;}

/* logo + heading above card */
.lp-header{text-align:center;padding:0 0 1.25rem;}
.lp-header img{height:38px;width:auto;display:block;margin:0 auto .9rem;}
.lp-title{
  font-family:'Inter',sans-serif;font-weight:800;font-size:1.45rem;
  color:var(--mk-navy);margin:0 0 .3rem;letter-spacing:-.03em;
}
.lp-sub{font-size:13px;color:var(--mk-muted);margin:0;line-height:1.6;}

/* form card */
[data-testid="stForm"]{
  background:#fff !important;
  border:1.5px solid var(--ind-200) !important;
  border-radius:20px !important;
  padding:1.75rem 1.75rem 1.5rem !important;
  box-shadow:0 6px 32px rgba(79,70,229,.09) !important;
}
[data-testid="stForm"] .stTextInput input{
  border:1.5px solid var(--ind-100) !important;
  border-radius:10px !important;
  font-family:'Inter',sans-serif !important;font-size:14px !important;
  color:var(--mk-navy) !important;background:#fff !important;
}
[data-testid="stForm"] .stTextInput input:focus{
  border-color:var(--ind-600) !important;
  box-shadow:0 0 0 3px rgba(79,70,229,.11) !important;
}
[data-testid="stForm"] label{
  font-family:'Inter',sans-serif !important;font-size:12.5px !important;
  font-weight:600 !important;color:var(--mk-navy) !important;
}
[data-testid="stForm"] button[kind="primaryFormSubmit"],
[data-testid="stForm"] .stButton>button{
  background:linear-gradient(135deg,var(--ind-600),var(--vio-600)) !important;
  color:#fff !important;border:none !important;border-radius:999px !important;
  font-family:'Inter',sans-serif !important;font-weight:700 !important;
  font-size:14.5px !important;
  box-shadow:0 6px 20px rgba(79,70,229,.32) !important;
  transition:all .22s !important;
}
[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
[data-testid="stForm"] .stButton>button:hover{
  box-shadow:0 10px 26px rgba(79,70,229,.42) !important;
  transform:translateY(-1px) !important;
}

/* footer links below card */
.lp-footer{
  text-align:center;padding:.9rem 0 .25rem;
  font-size:12.5px;color:var(--mk-muted);
}
.lp-links{display:flex;gap:8px;justify-content:center;margin-top:.6rem;}
.lp-link-creator,.lp-link-business{
  display:inline-flex;align-items:center;gap:5px;
  padding:6px 16px;border-radius:999px;
  font-size:12.5px;font-weight:700;font-family:'Inter',sans-serif;
  text-decoration:none !important;
  transition:all .2s cubic-bezier(.34,1.56,.64,1);white-space:nowrap;
}
.lp-link-creator{
  background:linear-gradient(135deg,rgba(99,102,241,.1),rgba(139,92,246,.13));
  color:var(--ind-600) !important;border:1.5px solid rgba(99,102,241,.22);
  box-shadow:0 2px 8px rgba(99,102,241,.08);
}
.lp-link-creator:hover{
  background:linear-gradient(135deg,rgba(99,102,241,.18),rgba(139,92,246,.24)) !important;
  box-shadow:0 5px 16px rgba(99,102,241,.17) !important;transform:scale(1.04) translateY(-1px);
}
.lp-link-business{
  background:#fff;color:var(--ind-600) !important;
  border:1.5px solid var(--ind-200);box-shadow:0 2px 6px rgba(99,102,241,.05);
}
.lp-link-business:hover{
  border-color:var(--ind-600) !important;
  box-shadow:0 5px 14px rgba(99,102,241,.13) !important;transform:scale(1.04) translateY(-1px);
}
</style>
<div class="lp-top"></div>
""", unsafe_allow_html=True)

_, col, _ = st.columns([1, 1.1, 1])

with col:
    st.markdown("""
<div class="lp-header">
  <h2 class="lp-title">Welcome back</h2>
  <p class="lp-sub">Log in to manage your Skout profile</p>
</div>
""", unsafe_allow_html=True)

    with st.form("login_form"):
        email    = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Log in →", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Please fill in all fields.")
        else:
            try:
                with st.spinner("Logging in…"):
                    data = login_user(email, password)
                st.session_state["user"]       = data
                st.session_state["user_token"] = data.get("token")
                save_session(data.get("token", ""))
                st.switch_page(_P_HOME)
            except APIError as e:
                st.error(str(e))

    st.markdown("""
<div class="lp-footer">Don't have an account?</div>
<div class="lp-links">
  <a class="lp-link-creator" href="/Creator_Onboarding" target="_self">🎤 Join as Creator</a>
  <a class="lp-link-business" href="/Business_Onboarding" target="_self">💼 Join as Business</a>
</div>
""", unsafe_allow_html=True)
