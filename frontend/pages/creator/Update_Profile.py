"""Update Profile — lets a logged-in creator view and edit their existing profile."""
from __future__ import annotations

import streamlit as st

from frontend.utils.api_client import APIError, get_creator, update_creator, fetch_instagram_profile
from frontend.utils.session import restore_session
from frontend.utils.styles import inject_css, _P_CREATOR_DASHBOARD

inject_css()
restore_session()

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

user = st.session_state.get("user")
if not user or user.get("role") != "creator":
    st.switch_page(_P_CREATOR_DASHBOARD)
    st.stop()

creator_id = user.get("creator_id")
token = st.session_state.get("user_token", "")

if not creator_id:
    st.error("No creator profile linked to your account.")
    st.stop()

# ── Load existing profile ──────────────────────────────────────────────────────
try:
    prof = get_creator(creator_id)
except APIError as e:
    st.error(f"Could not load profile: {e}")
    st.stop()

# ── Header ─────────────────────────────────────────────────────────────────────
hdr_a, hdr_b, hdr_spc, hdr_back = st.columns([2.2, 5, 3, 1.5])
with hdr_a:
    st.markdown(
        '<div class="sk-hdr" style="display:flex;align-items:center;gap:9px">'
        '<img src="app/static/skout-logo.png" style="height:30px;width:auto;display:block"></div>',
        unsafe_allow_html=True)
with hdr_b:
    st.markdown(
        '<div style="font-size:13px;font-weight:700;color:#0F172A;'
        'font-family:Poppins,sans-serif">✏️ Update Profile</div>',
        unsafe_allow_html=True)
with hdr_back:
    if st.button("← Dashboard", key="up_back"):
        st.switch_page(_P_CREATOR_DASHBOARD)

st.markdown("<div style='padding-top:1.5rem'></div>", unsafe_allow_html=True)

# ── Instagram quick-refetch ────────────────────────────────────────────────────
pf = st.session_state.get("up_ig_prefill", {})

st.markdown(
    '<div class="app-card" style="margin-bottom:16px;border:1.5px solid #DBEAFE;background:#EFF6FF">'
    '<span class="app-section-label">⚡ Refresh from Instagram</span>'
    '<div style="font-size:12.5px;color:#64748B;margin-bottom:10px">'
    "Re-fetch your follower count, bio, and name from Instagram."
    '</div>',
    unsafe_allow_html=True,
)
ig_col, btn_col = st.columns([3, 1])
ig_quick = ig_col.text_input(
    "Instagram handle", value=prof.get("instagram_handle") or "",
    label_visibility="collapsed", key="up_ig_handle_fetch",
)
if btn_col.button("🔄 Fetch", use_container_width=True, key="up_ig_fetch_btn"):
    if not ig_quick.strip():
        st.warning("Enter your Instagram handle first.")
    else:
        with st.spinner("Fetching…"):
            try:
                ig_data = fetch_instagram_profile(ig_quick.strip())
                if ig_data.get("found"):
                    st.session_state["up_ig_prefill"] = ig_data
                    st.success(f"✅ Found @{ig_data.get('username')} — {ig_data.get('followers', 0):,} followers")
                    st.rerun()
                else:
                    st.warning(ig_data.get("error", "Could not fetch profile."))
            except APIError as e:
                st.warning(f"Could not reach Instagram: {e}")
st.markdown('</div>', unsafe_allow_html=True)

# ── Edit form ──────────────────────────────────────────────────────────────────
with st.form("update_profile_form", clear_on_submit=False):

    # Identity
    st.markdown('<div class="app-card" style="margin-bottom:16px"><span class="app-section-label">Identity</span>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    display_name = c1.text_input("Display name", value=prof.get("display_name") or "")
    phone        = c2.text_input("Phone",         value=prof.get("phone") or "")
    c3, c4 = st.columns(2)
    country = c3.text_input("Country (ISO-2)", value=prof.get("country") or "", max_chars=2).upper()
    city    = c4.text_input("City",            value=prof.get("city") or "")
    st.markdown("</div>", unsafe_allow_html=True)

    # Socials
    st.markdown(
        '<div class="app-card" style="margin-bottom:16px">'
        '<span class="app-section-label">Social platforms</span>',
        unsafe_allow_html=True,
    )
    sc1, sc2 = st.columns(2)
    ig_handle    = sc1.text_input("Instagram handle",    value=pf.get("username") or prof.get("instagram_handle") or "")
    ig_followers = sc2.number_input("Instagram followers", value=int(pf.get("followers") or prof.get("instagram_followers") or 0), min_value=0, max_value=100_000_000, step=1_000)
    tt_handle    = sc1.text_input("TikTok handle",       value=prof.get("tiktok_handle") or "")
    tt_followers = sc2.number_input("TikTok followers",  value=int(prof.get("tiktok_followers") or 0), min_value=0, max_value=100_000_000, step=1_000)
    yt_handle    = sc1.text_input("YouTube handle / URL", value=prof.get("youtube_channel") or "")
    yt_subs      = sc2.number_input("YouTube subscribers", value=int(prof.get("youtube_subscribers") or 0), min_value=0, max_value=100_000_000, step=1_000)
    tw_handle    = sc1.text_input("Twitter / X handle", value=prof.get("twitter_handle") or "")
    website      = sc2.text_input("Website",             value=pf.get("website") or prof.get("website") or "")
    st.markdown("</div>", unsafe_allow_html=True)

    # Niche & Audience
    _ALL_NICHES = ["beauty","fashion","fitness","food","travel","gaming","tech",
                   "parenting","education","business","finance","lifestyle",
                   "art","music","sports","automotive","home-decor","sustainability","pets","books"]
    _ALL_LANGS  = ["en","hi","es","fr","de","pt","ja","ko","zh","ar","id","ru"]
    _ALL_CTRIES = ["US","IN","GB","BR","DE","FR","CA","AU","JP","MX","PH"]
    _AGE_OPTS   = ["13-17","18-24","25-34","35-44","45-54","55+"]

    st.markdown('<div class="app-card" style="margin-bottom:16px"><span class="app-section-label">Niche & audience</span>', unsafe_allow_html=True)
    na1, na2 = st.columns(2)
    niches = na1.multiselect("Niches", _ALL_NICHES, default=[n for n in (prof.get("niches") or []) if n in _ALL_NICHES])
    languages = na2.multiselect("Content languages", _ALL_LANGS, default=[l for l in (prof.get("languages") or []) if l in _ALL_LANGS])
    na3, na4 = st.columns(2)
    aud_countries = na3.multiselect("Top audience countries", _ALL_CTRIES, default=[c for c in (prof.get("audience_countries") or []) if c in _ALL_CTRIES])
    cur_age = prof.get("audience_age_range") or "18-24"
    age_idx = _AGE_OPTS.index(cur_age) if cur_age in _AGE_OPTS else 1
    age_range = na4.selectbox("Dominant audience age", _AGE_OPTS, index=age_idx)
    st.markdown("</div>", unsafe_allow_html=True)

    # Rates & Collabs
    _ALL_COLLAB = ["sponsored-post","story","reel","long-form","affiliate","ambassador","event"]
    st.markdown('<div class="app-card" style="margin-bottom:16px"><span class="app-section-label">Rates & collaborations</span>', unsafe_allow_html=True)
    rc1, rc2, rc3 = st.columns(3)
    engagement   = rc1.number_input("Avg engagement rate", 0.0, 1.0, float(prof.get("avg_engagement_rate") or 0.035), step=0.001, format="%.3f")
    avg_views    = rc2.number_input("Avg views per post",  0, 100_000_000, int(prof.get("avg_views") or 0), step=100)
    min_rate     = rc3.number_input("Min rate (USD / post)", 0.0, 1_000_000.0, float(prof.get("min_rate_usd") or 0.0), step=50.0)
    cv1, cv2 = st.columns([1, 2])
    open_to      = cv1.checkbox("Open to brand collabs", value=bool(prof.get("open_to_collabs", True)))
    collab_types = cv2.multiselect("Preferred collab types", _ALL_COLLAB,
                                   default=[c for c in (prof.get("preferred_collab_types") or []) if c in _ALL_COLLAB])
    st.markdown("</div>", unsafe_allow_html=True)

    # Bio
    st.markdown('<div class="app-card" style="margin-bottom:16px"><span class="app-section-label">Bio</span>', unsafe_allow_html=True)
    bio = st.text_area("Bio", value=pf.get("bio") or prof.get("bio") or "", height=100, label_visibility="collapsed",
                       placeholder="Tell brands who you are and what you create.")
    st.markdown("</div>", unsafe_allow_html=True)

    submitted = st.form_submit_button("Save changes →", type="primary", use_container_width=True)

# ── Handle submit ──────────────────────────────────────────────────────────────
if submitted:
    payload: dict = {
        "display_name":          display_name.strip() or None,
        "phone":                 phone.strip() or None,
        "country":               country.strip() or None,
        "city":                  city.strip() or None,
        "instagram_handle":      ig_handle.strip() or None,
        "instagram_followers":   int(ig_followers),
        "tiktok_handle":         tt_handle.strip() or None,
        "tiktok_followers":      int(tt_followers),
        "youtube_channel":       yt_handle.strip() or None,
        "youtube_subscribers":   int(yt_subs),
        "twitter_handle":        tw_handle.strip() or None,
        "website":               website.strip() or None,
        "niches":                niches,
        "languages":             languages,
        "audience_countries":    aud_countries,
        "audience_age_range":    age_range,
        "avg_engagement_rate":   float(engagement),
        "avg_views":             int(avg_views),
        "min_rate_usd":          float(min_rate),
        "open_to_collabs":       bool(open_to),
        "preferred_collab_types": collab_types,
        "bio":                   bio.strip() or None,
    }
    # drop None values so only provided fields are patched
    payload = {k: v for k, v in payload.items() if v is not None or k in ("open_to_collabs",)}

    try:
        with st.spinner("Saving…"):
            update_creator(creator_id, payload, token)
        st.session_state.pop("up_ig_prefill", None)
        st.success("Profile updated successfully!")
        st.rerun()
    except APIError as e:
        st.error(str(e))
