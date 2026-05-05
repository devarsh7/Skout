"""Creator Onboarding — OTP sent BEFORE any DB writes. All data saved atomically on verify."""
from __future__ import annotations

import re
import streamlit as st

from frontend.utils.api_client import (
    APIError, fetch_instagram_profile,
    send_otp_email, register_creator_verified,
)
from frontend.utils.styles import inject_css, _P_CREATOR_DASHBOARD


inject_css()
st.markdown("""
<style>
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stMainBlockContainer"]{
  background:linear-gradient(150deg,#EEF2FF 0%,#F8FAFF 50%,#EFF6FF 100%) !important;
}
/* same specificity as inject_css reset — wins because declared later */
.main .block-container,[data-testid="stMainBlockContainer"]{
  padding:0 3.5rem 4rem !important;max-width:100% !important;
}
/* breathing room between stacked elements in content area */
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"]{gap:1rem !important;}
/* keep header tight */
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
        'font-family:Poppins,sans-serif">🎤 Creator Onboarding</div>',
        unsafe_allow_html=True)
st.markdown("<div style='padding-top:1.5rem'></div>", unsafe_allow_html=True)


def _make_username(name: str) -> str:
    u = re.sub(r"[^a-z0-9_]", "", name.strip().lstrip("@").lower().replace(" ", "_").replace("-", "_"))
    return (u or "creator")[:28]


# ── OTP step — shown after form submit, before any DB write ───────────────────
if "creator_pending" in st.session_state:
    pending = st.session_state["creator_pending"]
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown(
            '<div class="app-card" style="text-align:center;padding:2.5rem 2rem">'
            '<div style="font-size:2.5rem;margin-bottom:.75rem">📬</div>'
            '<h2 style="font-family:var(--fd);font-weight:800;font-size:1.4rem;color:var(--navy);margin:0 0 .5rem">Verify your email</h2>'
            f'<p style="font-size:13px;color:var(--muted);margin:0 0 .25rem">We sent a 6-digit code to</p>'
            f'<p style="font-size:13.5px;font-weight:700;color:var(--navy);margin:0 0 .25rem">{pending["email"]}</p>'
            '<p style="font-size:12px;color:var(--subtle);margin:0 0 1.5rem">Code expires in 10 minutes. Check spam if you don\'t see it.</p>'
            '<p style="font-size:12px;color:var(--blue-600);margin:0">Your profile will only be saved once this is verified.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        if pending.get("dev_otp"):
            st.info(f"🛠️ **Dev mode** — email not configured. Your code is: **{pending['dev_otp']}**")

        with st.form("creator_otp_form"):
            otp = st.text_input("Verification code", max_chars=6, placeholder="123456")
            verify_btn = st.form_submit_button("Verify & create profile →", type="primary", use_container_width=True)

        if verify_btn:
            if not otp.strip():
                st.error("Enter the 6-digit code from your email.")
            else:
                base_username = pending["username"]
                form = pending["form"]
                try:
                    data = None
                    with st.spinner("Verifying and saving your profile…"):
                        for suffix in [""] + [str(i) for i in range(1, 20)]:
                            candidate = f"{base_username}{suffix}"[:30]
                            try:
                                data = register_creator_verified({
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
                        st.session_state["ig_prefill"] = {}
                        st.session_state.pop("creator_pending", None)
                        st.switch_page(_P_CREATOR_DASHBOARD)
                except APIError as e:
                    st.error(str(e))

        col_r, col_back = st.columns(2)
        with col_r:
            if st.button("Resend code", use_container_width=True):
                try:
                    resp = send_otp_email(pending["email"], pending.get("name", ""))
                    new_dev = (resp or {}).get("dev_otp")
                    if new_dev:
                        st.session_state["creator_pending"]["dev_otp"] = new_dev
                        st.rerun()
                    else:
                        st.success("New code sent!")
                except APIError as e:
                    st.error(str(e))
        with col_back:
            if st.button("← Start over", use_container_width=True):
                st.session_state.pop("creator_pending", None)
                st.rerun()

    st.stop()


# ── Main onboarding form ───────────────────────────────────────────────────────
main, aside = st.columns([3, 1], gap="large")

with aside:
    st.markdown("""
<div class="app-card">
  <span class="app-section-label">What happens next?</span>
  <div style="font-size:13px;color:var(--muted);line-height:1.75">
    <div style="margin-bottom:10px">
      <strong style="color:var(--navy)">1. Verify email</strong><br>
      We send a code — your profile is only saved after you confirm.
    </div>
    <div style="margin-bottom:10px">
      <strong style="color:var(--navy)">2. Profile indexed</strong><br>
      Your data is embedded in Skout's vector store within seconds.
    </div>
    <div>
      <strong style="color:var(--navy)">3. Brand discovery</strong><br>
      Vetted brands search in plain English — you surface when it's a strong match.
    </div>
  </div>
</div>

<div class="app-card" style="margin-top:12px">
  <span class="app-section-label">Tips</span>
  <ul style="font-size:12.5px;color:var(--muted);line-height:1.8;padding-left:16px;margin:0">
    <li>A detailed bio improves semantic match quality.</li>
    <li>Add all active platforms — even small ones.</li>
    <li>Accurate engagement rates attract better-fit brands.</li>
  </ul>
</div>
""", unsafe_allow_html=True)

with main:

    # ── Instagram quick-fill ──────────────────────────────────────────────────
    pf = st.session_state.get("ig_prefill", {})
    st.markdown(
        '<div class="app-card" style="margin-bottom:16px;border:1.5px solid var(--blue-100);background:var(--blue-50)">'
        '<span class="app-section-label">⚡ Quick-fill from Instagram</span>'
        '<div style="font-size:12.5px;color:var(--muted);margin-bottom:10px">'
        "Enter your Instagram handle and we'll auto-fill your name, bio, and follower count."
        '</div>',
        unsafe_allow_html=True,
    )
    ig_col, btn_col = st.columns([3, 1])
    ig_quick_handle = ig_col.text_input(
        "Instagram handle", placeholder="priyastyles",
        label_visibility="collapsed", key="ig_quick_handle",
    )
    if btn_col.button("🔄 Fetch", use_container_width=True):
        if not ig_quick_handle.strip():
            st.warning("Enter your Instagram handle first.")
        else:
            with st.spinner("Fetching…"):
                try:
                    ig_data = fetch_instagram_profile(ig_quick_handle.strip())
                    if ig_data.get("found"):
                        st.session_state["ig_prefill"] = ig_data
                        st.success(f"✅ Found **{ig_data.get('username')}** — {ig_data.get('followers', 0):,} followers. Fields pre-filled below.")
                        st.rerun()
                    else:
                        err = ig_data.get("error", "Could not fetch profile.")
                        st.warning(f"⚠️ {err} Fill in manually below.")
                except APIError as e:
                    st.warning(f"Could not reach Instagram: {e}. Fill in manually below.")

    if pf.get("found"):
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin-top:6px;font-size:12.5px;color:var(--muted)">'
            f'<span>📸</span>'
            f'<span><strong style="color:var(--navy)">@{pf.get("username")}</strong> · {pf.get("followers", 0):,} followers</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Main form ─────────────────────────────────────────────────────────────
    with st.form("creator_onboard", clear_on_submit=False):

        # ── Identity ──
        st.markdown('<div class="app-card" style="margin-bottom:16px"><span class="app-section-label">Identity</span>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        full_name    = c1.text_input("Full name *",       value=pf.get("full_name", ""),  placeholder="Priya Sharma")
        display_name = c2.text_input("Display name",                                       placeholder="@priyastyles")
        email        = c3.text_input("Email *",                                            placeholder="priya@example.com")
        c4, c5, c6 = st.columns(3)
        phone   = c4.text_input("Phone",             placeholder="+1 555 123 4567")
        country = c5.text_input("Country (ISO-2) *", max_chars=2, placeholder="IN").upper()
        city    = c6.text_input("City",              placeholder="Mumbai")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Socials ──
        st.markdown(
            '<div class="app-card" style="margin-bottom:16px">'
            '<span class="app-section-label">Social platforms '
            '<span style="font-weight:400;color:var(--muted);text-transform:none;letter-spacing:0;font-size:11px">— at least one required</span></span>',
            unsafe_allow_html=True,
        )
        sc1, sc2 = st.columns(2)
        ig_handle    = sc1.text_input("Instagram handle",       value=pf.get("username", ""), placeholder="priyastyles")
        ig_followers = sc2.number_input("Instagram followers",  value=int(pf.get("followers", 0)), min_value=0, max_value=100_000_000, step=1_000)
        tt_handle    = sc1.text_input("TikTok handle",          placeholder="priyastyles")
        tt_followers = sc2.number_input("TikTok followers",     0, 100_000_000, step=1_000)
        yt_handle    = sc1.text_input("YouTube @ handle / URL", placeholder="@priyastyles")
        yt_subs      = sc2.number_input("YouTube subscribers",  0, 100_000_000, step=1_000)
        tw_handle    = sc1.text_input("Twitter / X handle",     placeholder="priyastyles")
        website      = sc2.text_input("Website",                value=pf.get("website", ""), placeholder="https://priyastyles.com")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Niche & Audience ──
        st.markdown('<div class="app-card" style="margin-bottom:16px"><span class="app-section-label">Niche & audience</span>', unsafe_allow_html=True)
        na1, na2 = st.columns(2)
        niches = na1.multiselect(
            "Niches *",
            ["beauty","fashion","fitness","food","travel","gaming","tech",
             "parenting","education","business","finance","lifestyle",
             "art","music","sports","automotive","home-decor","sustainability","pets","books"],
        )
        languages = na2.multiselect(
            "Content languages",
            ["en","hi","es","fr","de","pt","ja","ko","zh","ar","id","ru"],
        )
        na3, na4 = st.columns(2)
        audience_countries = na3.multiselect("Top audience countries", ["US","IN","GB","BR","DE","FR","CA","AU","JP","MX","PH"])
        age_range = na4.selectbox("Dominant audience age", ["13-17","18-24","25-34","35-44","45-54","55+"], index=1)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Rates & Collabs ──
        st.markdown('<div class="app-card" style="margin-bottom:16px"><span class="app-section-label">Rates & collaborations</span>', unsafe_allow_html=True)
        rc1, rc2, rc3 = st.columns(3)
        engagement   = rc1.number_input("Avg engagement rate", 0.0, 1.0, 0.035, step=0.001, format="%.3f")
        avg_views    = rc2.number_input("Avg views per post",  0, 100_000_000, step=100)
        min_rate     = rc3.number_input("Min rate (USD / post)", 0.0, 1_000_000.0, 0.0, step=50.0)
        cv1, cv2     = st.columns([1, 2])
        open_to      = cv1.checkbox("Open to brand collabs", value=True)
        collab_types = cv2.multiselect(
            "Preferred collab types",
            ["sponsored-post","story","reel","long-form","affiliate","ambassador","event"],
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Bio ──
        st.markdown('<div class="app-card" style="margin-bottom:16px"><span class="app-section-label">Bio</span>', unsafe_allow_html=True)
        bio = st.text_area(
            "Short bio", value=pf.get("bio", ""), height=100, label_visibility="collapsed",
            placeholder="Mumbai-based beauty creator focused on clean, cruelty-free skincare.",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Account password ──
        st.markdown(
            '<div class="app-card" style="margin-bottom:16px;border:1.5px solid var(--blue-100)">'
            '<span class="app-section-label">🔐 Create your Skout account</span>'
            '<div style="font-size:12.5px;color:var(--muted);margin-bottom:10px">'
            'Set a password to log back in and manage your profile.</div>',
            unsafe_allow_html=True,
        )
        pw1, pw2 = st.columns(2)
        password         = pw1.text_input("Password *",         type="password", placeholder="At least 8 characters")
        confirm_password = pw2.text_input("Confirm password *", type="password", placeholder="Repeat password")
        st.markdown("</div>", unsafe_allow_html=True)

        consent = st.checkbox(
            "I consent to Skout storing this profile and making it discoverable to brands.",
            value=False,
        )
        submitted = st.form_submit_button("Send verification code →", type="primary", use_container_width=True)

if submitted:
    errors = []
    fn    = (full_name    or "").strip()
    em    = (email        or "").strip()
    ct    = (country      or "").strip().upper()
    pw    = (password     or "")
    cpw   = (confirm_password or "")

    if not consent:             errors.append("Please grant consent to continue.")
    if not fn or not em or not ct:
        errors.append("Full name, email, and country are required.")
    if "@" not in em:           errors.append("Enter a valid email address.")
    if not any([ig_handle, tt_handle, yt_handle, tw_handle]):
        errors.append("Add at least one social handle.")
    if not niches:              errors.append("Select at least one niche.")
    if not pw:                  errors.append("Password is required.")
    if len(pw) < 8:             errors.append("Password must be at least 8 characters.")
    if pw != cpw:               errors.append("Passwords do not match.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        try:
            with st.spinner("Sending verification code…"):
                resp = send_otp_email(em, fn)

            dev_otp = (resp or {}).get("dev_otp")
            base_username = _make_username((display_name or fn or "creator"))
            st.session_state["creator_pending"] = {
                "email":    em,
                "name":     fn,
                "username": base_username,
                "dev_otp":  dev_otp,
                "form": {
                    "email":                 em,
                    "password":              pw,
                    "full_name":             fn,
                    "display_name":          display_name or None,
                    "phone":                 phone or None,
                    "instagram_handle":      ig_handle or None,
                    "tiktok_handle":         tt_handle or None,
                    "youtube_channel":       yt_handle or None,
                    "twitter_handle":        tw_handle or None,
                    "website":               website or None,
                    "instagram_followers":   int(ig_followers),
                    "tiktok_followers":      int(tt_followers),
                    "youtube_subscribers":   int(yt_subs),
                    "avg_engagement_rate":   float(engagement),
                    "avg_views":             int(avg_views),
                    "bio":                   bio or None,
                    "niches":                niches,
                    "languages":             languages,
                    "country":               ct,
                    "city":                  city or None,
                    "audience_countries":    audience_countries,
                    "audience_age_range":    age_range,
                    "min_rate_usd":          float(min_rate),
                    "open_to_collabs":       bool(open_to),
                    "preferred_collab_types": collab_types,
                },
            }
            st.rerun()

        except APIError as e:
            st.error(str(e))

