"""Sign Up page — with OTP email verification."""
from __future__ import annotations

import streamlit as st

from frontend.utils.api_client import APIError, register_user, resend_otp, verify_otp
from frontend.utils.styles import inject_app_css, inject_css, render_app_footer, _app_topbar


inject_css()
inject_app_css()
_app_topbar("📝 Sign Up", "Create your Skout account", active="")

st.markdown('<div class="app-body">', unsafe_allow_html=True)

# Centered card
_, col, _ = st.columns([1, 1.4, 1])

with col:
    # Pre-fill from onboarding session state if available
    prefill_email      = st.session_state.get("signup_prefill_email", "")
    prefill_role       = st.session_state.get("signup_prefill_role", "creator")
    prefill_creator_id = st.session_state.get("signup_prefill_creator_id")

    # ── Step 1: Registration form ─────────────────────────────────────────────
    if "pending_verify_email" not in st.session_state:

        role_label = "Creator" if prefill_role == "creator" else "Business"
        st.markdown(f"""
<div style="text-align:center;margin-bottom:1.75rem">
  <div style="font-size:2.2rem;margin-bottom:.5rem">{"🎤" if prefill_role == "creator" else "💼"}</div>
  <h2 style="font-family:var(--fd);font-weight:800;font-size:1.5rem;color:var(--navy);margin:0 0 .35rem">
    Create your account
  </h2>
  <p style="font-size:13px;color:var(--muted);margin:0">
    Joining as a <strong style="color:var(--navy)">{role_label}</strong>
  </p>
</div>
""", unsafe_allow_html=True)

        with st.form("signup_form"):
            username         = st.text_input("Username *", placeholder="priyastyles")
            email            = st.text_input("Email *",    value=prefill_email, placeholder="you@example.com")
            password         = st.text_input("Password *", type="password", placeholder="At least 8 characters")
            confirm_password = st.text_input("Confirm password *", type="password", placeholder="Repeat password")
            submitted        = st.form_submit_button("Create account →", type="primary", use_container_width=True)

        if submitted:
            errors = []
            if not username.strip():      errors.append("Username is required.")
            if not email.strip():         errors.append("Email is required.")
            if not password:              errors.append("Password is required.")
            if password != confirm_password: errors.append("Passwords do not match.")
            if len(password) < 8:         errors.append("Password must be at least 8 characters.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                try:
                    with st.spinner("Creating your account…"):
                        register_user(
                            username   = username.strip(),
                            email      = email.strip(),
                            password   = password,
                            role       = prefill_role,
                            creator_id = prefill_creator_id,
                        )
                    st.session_state["pending_verify_email"] = email.strip()
                    st.session_state["pending_verify_username"] = username.strip()
                    st.rerun()
                except APIError as e:
                    st.error(str(e))

    # ── Step 2: OTP verification ──────────────────────────────────────────────
    else:
        verify_email    = st.session_state["pending_verify_email"]
        verify_username = st.session_state.get("pending_verify_username", "")

        st.markdown(f"""
<div style="text-align:center;margin-bottom:1.75rem">
  <div style="font-size:2.2rem;margin-bottom:.5rem">📬</div>
  <h2 style="font-family:var(--fd);font-weight:800;font-size:1.5rem;color:var(--navy);margin:0 0 .35rem">
    Verify your email
  </h2>
  <p style="font-size:13px;color:var(--muted);margin:0 0 .5rem">
    We sent a 6-digit code to <strong style="color:var(--navy)">{verify_email}</strong>
  </p>
  <p style="font-size:12px;color:var(--subtle);margin:0">
    Check your inbox (and spam folder). Code expires in 10 minutes.
  </p>
</div>
""", unsafe_allow_html=True)

        with st.form("otp_form"):
            otp = st.text_input(
                "Verification code",
                max_chars=6,
                placeholder="123456",
            )
            verify_btn = st.form_submit_button("Verify →", type="primary", use_container_width=True)

        if verify_btn:
            if not otp.strip():
                st.error("Enter the 6-digit code.")
            else:
                try:
                    with st.spinner("Verifying…"):
                        data = verify_otp(verify_email, otp.strip())
                    # Verified — store session
                    st.session_state["user"]       = data
                    st.session_state["user_token"] = data.get("token")
                    # Clear pending state and prefills
                    for k in ["pending_verify_email", "pending_verify_username",
                              "signup_prefill_email", "signup_prefill_role",
                              "signup_prefill_creator_id"]:
                        st.session_state.pop(k, None)

                    st.success(f"✅ Welcome to Skout, **{data['username']}**! Your account is verified.")
                    st.balloons()
                except APIError as e:
                    st.error(str(e))

        # Resend OTP
        st.markdown('<div style="text-align:center;margin-top:1rem">', unsafe_allow_html=True)
        if st.button("Resend code", use_container_width=False):
            try:
                resend_otp(verify_email)
                st.success("New code sent!")
            except APIError as e:
                st.error(str(e))
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("← Use a different email", use_container_width=False):
            st.session_state.pop("pending_verify_email", None)
            st.session_state.pop("pending_verify_username", None)
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
render_app_footer()
