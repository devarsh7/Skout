"""Business Onboarding — OTP sent BEFORE any DB writes. Account created atomically on verify."""
from __future__ import annotations

import re
import streamlit as st

from frontend.utils.api_client import APIError, send_otp_email, register_business_verified
from frontend.utils.styles import inject_css, _P_BUSINESS_DASHBOARD


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

hdr_a, hdr_b, hdr_spc = st.columns([2.2, 7, 2])
with hdr_a:
    st.markdown(
        '<div class="sk-hdr" style="display:flex;align-items:center;gap:9px">'
        '<img src="app/static/skout-logo.png" style="height:30px;width:auto;display:block"></div>',
        unsafe_allow_html=True)
with hdr_b:
    st.markdown(
        '<div style="font-size:13px;font-weight:700;color:#0F172A;'
        'font-family:Poppins,sans-serif">💼 Business Onboarding</div>',
        unsafe_allow_html=True)
st.markdown("<div style='padding-top:1.5rem'></div>", unsafe_allow_html=True)


def _make_username(name: str) -> str:
    u = re.sub(r"[^a-z0-9_]", "", name.strip().lower().replace(" ", "_").replace("-", "_"))
    return (u or "brand")[:28]


# ── OTP step — shown after form submit, before any DB write ───────────────────
if "business_pending" in st.session_state:
    pending = st.session_state["business_pending"]
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown(
            '<div class="app-card" style="text-align:center;padding:2.5rem 2rem">'
            '<div style="font-size:2.5rem;margin-bottom:.75rem">📬</div>'
            '<h2 style="font-family:var(--fd);font-weight:800;font-size:1.4rem;color:var(--navy);margin:0 0 .5rem">Verify your email</h2>'
            f'<p style="font-size:13px;color:var(--muted);margin:0 0 .25rem">We sent a 6-digit code to</p>'
            f'<p style="font-size:13.5px;font-weight:700;color:var(--navy);margin:0 0 .25rem">{pending["email"]}</p>'
            '<p style="font-size:12px;color:var(--subtle);margin:0 0 1.5rem">Code expires in 10 minutes. Check spam if you don\'t see it.</p>'
            '<p style="font-size:12px;color:var(--blue-600);margin:0">Your account will only be created once this is verified.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        if pending.get("dev_otp"):
            st.info(f"🛠️ **Dev mode** — email not configured. Your code is: **{pending['dev_otp']}**")

        with st.form("business_otp_form"):
            otp = st.text_input("Verification code", max_chars=6, placeholder="123456")
            verify_btn = st.form_submit_button("Verify & create account →", type="primary", use_container_width=True)

        if verify_btn:
            if not otp.strip():
                st.error("Enter the 6-digit code from your email.")
            else:
                base_username = pending["username"]
                form = pending["form"]
                try:
                    data = None
                    with st.spinner("Verifying and creating your account…"):
                        for suffix in [""] + [str(i) for i in range(1, 20)]:
                            candidate = f"{base_username}{suffix}"[:30]
                            try:
                                data = register_business_verified({
                                    **form,
                                    "username": candidate,
                                    "otp": otp.strip(),
                                })
                                break
                            except APIError as e:
                                if "Username already taken" in str(e):
                                    continue
                                raise
                    if data:
                        st.session_state["user"]       = data
                        st.session_state["user_token"] = data.get("token")
                        st.session_state.pop("business_pending", None)
                        st.switch_page(_P_BUSINESS_DASHBOARD)
                except APIError as e:
                    st.error(str(e))

        col_r, col_back = st.columns(2)
        with col_r:
            if st.button("Resend code", use_container_width=True):
                try:
                    resp = send_otp_email(pending["email"], pending.get("name", ""))
                    new_dev = (resp or {}).get("dev_otp")
                    if new_dev:
                        st.session_state["business_pending"]["dev_otp"] = new_dev
                        st.rerun()
                    else:
                        st.success("New code sent!")
                except APIError as e:
                    st.error(str(e))
        with col_back:
            if st.button("← Start over", use_container_width=True):
                st.session_state.pop("business_pending", None)
                st.rerun()

    st.stop()


# ── Main form ─────────────────────────────────────────────────────────────────
main, aside = st.columns([3, 1], gap="large")

with aside:
    st.markdown("""
<div class="app-card">
  <span class="app-section-label">What you get</span>
  <div style="font-size:13px;color:var(--muted);line-height:1.75">
    <div style="margin-bottom:10px">
      <strong style="color:var(--navy)">🔍 Semantic search</strong><br>
      Find creators in plain English — no filters spreadsheet required.
    </div>
    <div style="margin-bottom:10px">
      <strong style="color:var(--navy)">🎯 LangGraph filtering</strong><br>
      Layer hard constraints on top of AI ranking: follower range, engagement, geo, niche.
    </div>
    <div>
      <strong style="color:var(--navy)">✉️ AI outreach drafts</strong><br>
      Personalized first-touch messages in your brand voice, ready to send.
    </div>
  </div>
</div>

<div class="app-card" style="margin-top:12px">
  <span class="app-section-label">Onboarding timeline</span>
  <div style="font-size:12.5px;color:var(--muted);line-height:1.8">
    <div>📋 Submit form</div>
    <div>→ Verify your email</div>
    <div>→ Review within 1 business day</div>
    <div>→ Account setup call (30 min)</div>
    <div>→ Access granted</div>
  </div>
</div>
""", unsafe_allow_html=True)

with main:
    with st.form("business_onboard", clear_on_submit=False):

        # ── Company ──
        st.markdown('<div class="app-card" style="margin-bottom:16px"><span class="app-section-label">Company</span>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        company_name  = c1.text_input("Company / Brand name *", placeholder="Acme Corp")
        website       = c2.text_input("Website *",              placeholder="https://acmecorp.com")
        c3, c4 = st.columns(2)
        contact_name  = c3.text_input("Contact name *",         placeholder="Alex Johnson")
        contact_email = c4.text_input("Work email *",           placeholder="alex@acmecorp.com")
        c5, c6 = st.columns(2)
        phone         = c5.text_input("Phone",                  placeholder="+1 555 000 1234")
        country       = c6.text_input("Country (ISO-2) *",      max_chars=2, placeholder="US")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Campaign needs ──
        st.markdown('<div class="app-card" style="margin-bottom:16px"><span class="app-section-label">Campaign needs</span>', unsafe_allow_html=True)
        n1, n2 = st.columns(2)
        industry = n1.selectbox("Industry", [
            "— select —", "Beauty & Personal Care", "Fashion & Apparel", "Food & Beverage",
            "Technology & Software", "Travel & Hospitality", "Health & Wellness",
            "Finance & Fintech", "Gaming & Entertainment", "Education", "Other",
        ])
        budget = n2.selectbox("Monthly influencer budget (USD)", [
            "— select —", "Under $5K", "$5K – $20K", "$20K – $50K", "$50K – $100K", "$100K+",
        ])
        platforms = st.multiselect(
            "Platforms to activate",
            ["Instagram", "TikTok", "YouTube", "Twitter / X", "LinkedIn", "Pinterest", "Twitch"],
        )
        goals = st.text_area(
            "Campaign goals *", height=120,
            placeholder="e.g. Drive awareness for our new vegan skincare line in Europe.",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # ── How heard ──
        st.markdown('<div class="app-card" style="margin-bottom:16px"><span class="app-section-label">One last thing</span>', unsafe_allow_html=True)
        how_heard = st.selectbox("How did you hear about Skout?", [
            "— select —", "Search engine", "Social media", "Referral", "Conference / event", "Other",
        ])
        agree = st.checkbox("I agree that my information will be used to set up a Skout business account.")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Account password ──
        st.markdown(
            '<div class="app-card" style="margin-bottom:16px;border:1.5px solid var(--blue-100)">'
            '<span class="app-section-label">🔐 Create your Skout account</span>'
            '<div style="font-size:12.5px;color:var(--muted);margin-bottom:10px">'
            'Set a password to log in and track your access request.</div>',
            unsafe_allow_html=True,
        )
        pw1, pw2 = st.columns(2)
        password         = pw1.text_input("Password *",         type="password", placeholder="At least 8 characters")
        confirm_password = pw2.text_input("Confirm password *", type="password", placeholder="Repeat password")
        st.markdown("</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button("Send verification code →", type="primary", use_container_width=True)

if submitted:
    cn  = (company_name  or "").strip()
    web = (website       or "").strip()
    ctn = (contact_name  or "").strip()
    em  = (contact_email or "").strip()
    gls = (goals         or "").strip()
    pw  = (password      or "")
    cpw = (confirm_password or "")
    ct  = (country       or "").strip().upper()

    errors = []
    if not cn:              errors.append("Company name is required.")
    if not web:             errors.append("Website is required.")
    if not ctn:             errors.append("Contact name is required.")
    if not em or "@" not in em: errors.append("A valid work email is required.")
    if not gls:             errors.append("Campaign goals are required.")
    if not agree:           errors.append("Please agree to the terms.")
    if not pw:              errors.append("Password is required.")
    if len(pw) < 8:         errors.append("Password must be at least 8 characters.")
    if pw != cpw:           errors.append("Passwords do not match.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        try:
            with st.spinner("Sending verification code…"):
                resp = send_otp_email(em, ctn)

            dev_otp = (resp or {}).get("dev_otp")
            base_username = _make_username(cn)
            st.session_state["business_pending"] = {
                "email":    em,
                "name":     ctn,
                "username": base_username,
                "dev_otp":  dev_otp,
                "form": {
                    "email":        em,
                    "password":     pw,
                    "company_name": cn,
                    "website":      web or None,
                    "contact_name": ctn or None,
                    "phone":        (phone or "").strip() or None,
                    "country":      ct or None,
                    "industry":     industry if industry != "— select —" else None,
                    "budget":       budget   if budget   != "— select —" else None,
                    "platforms":    platforms,
                    "goals":        gls or None,
                },
            }
            st.rerun()

        except APIError as e:
            st.error(str(e))
