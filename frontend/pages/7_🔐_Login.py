"""Login page."""
from __future__ import annotations

import streamlit as st

from frontend.utils.api_client import APIError, login_user
from frontend.utils.session import save_session
from frontend.utils.styles import _P_BUSINESS, _P_CREATOR, _P_HOME, inject_app_css, inject_css, render_app_footer, _app_topbar


inject_css()
inject_app_css()
_app_topbar("🔐 Login", "Welcome back to Skout", active="")

st.markdown('<div class="app-body">', unsafe_allow_html=True)

# Centered card
_, col, _ = st.columns([1, 1.4, 1])

with col:
    st.markdown("""
<div style="text-align:center;margin-bottom:2rem">
  <div style="font-size:2.5rem;margin-bottom:.5rem">🦉</div>
  <h2 style="font-family:var(--fd);font-weight:800;font-size:1.6rem;color:var(--navy);margin:0 0 .4rem">
    Welcome back
  </h2>
  <p style="font-size:13.5px;color:var(--muted);margin:0">
    Log in to manage your Skout profile
  </p>
</div>
""", unsafe_allow_html=True)

    with st.form("login_form"):
        email    = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Log in →", type="primary", use_container_width=True)

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
<div style="text-align:center;margin-top:1.5rem;font-size:13px;color:var(--muted)">
  Don't have an account?
</div>
""", unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        st.markdown('<div class="sk-nav-creator">', unsafe_allow_html=True)
        st.page_link(_P_CREATOR, label="🎤 Join as Creator")
        st.markdown('</div>', unsafe_allow_html=True)
    with r2:
        st.markdown('<div class="sk-nav-business">', unsafe_allow_html=True)
        st.page_link(_P_BUSINESS, label="💼 Join as Business")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
render_app_footer()
