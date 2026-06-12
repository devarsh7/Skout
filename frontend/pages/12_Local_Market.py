"""Local Market Intelligence — 4-tab hyperlocal creator analytics."""
from __future__ import annotations

import streamlit as st

from backend.services.location_confidence import confidence_badge_html
from frontend.utils.api_client import (
    APIError,
    local_benchmarks,
    local_cities,
    local_creator_vs_benchmark,
    local_leaderboard,
    local_neighbourhood_creators,
    local_neighbourhoods,
    local_recalculate_benchmarks,
    local_trending_formats,
)
from frontend.utils.map_utils import _AVC, _NE, _fmt, _ini
from frontend.utils.session import restore_session
from frontend.utils.styles import _P_HOME, _P_OUTREACH, inject_css

inject_css()
restore_session()

user = st.session_state.get("user")
if not user:
    st.switch_page(_P_HOME)

# ── Shared CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stMainBlockContainer"]{
  background:linear-gradient(150deg,#EEF2FF 0%,#F8FAFF 50%,#EFF6FF 100%) !important;
}
.main .block-container,[data-testid="stMainBlockContainer"]{padding:0 3.5rem 4rem !important;max-width:100% !important;}
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

/* Cards */
.lm-card{background:white;border-radius:20px;padding:1.4rem 1.6rem;
  box-shadow:0 4px 24px rgba(15,23,42,.07),0 1px 4px rgba(15,23,42,.04);
  border:1px solid #EEF2FF;animation:riseIn .5s cubic-bezier(.22,1,.36,1) both;}

/* Leaderboard rows */
.lb-row{display:flex;align-items:center;gap:14px;background:white;
  border-radius:16px;padding:.9rem 1.2rem;
  border:1px solid #F1F5F9;box-shadow:0 1px 4px rgba(15,23,42,.04);
  margin-bottom:8px;transition:border-color .18s,box-shadow .18s;
  animation:riseIn .45s cubic-bezier(.22,1,.36,1) both;}
.lb-row:hover{border-color:#C7D2FE;box-shadow:0 4px 18px rgba(79,70,229,.1);}
.lb-rank{font-family:Poppins,sans-serif;font-size:1.1rem;font-weight:900;
  color:#C7D2FE;min-width:30px;text-align:center;}
.lb-rank.top{color:#F59E0B;}
.lb-av{width:46px;height:46px;border-radius:13px;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
  font-family:Poppins,sans-serif;font-weight:800;font-size:16px;color:white;}
.lb-info{flex:1;min-width:0;}
.lb-name{font-weight:700;font-size:14px;color:#0F172A;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.lb-handle{font-size:12px;color:#64748B;margin-top:1px;}
.lb-meta{font-size:11.5px;color:#94A3B8;margin-top:3px;}
.lb-eng{text-align:center;min-width:64px;flex-shrink:0;}
.lb-eng-val{font-family:Poppins,sans-serif;font-size:1.2rem;font-weight:900;color:#059669;}
.lb-eng-lbl{font-size:9.5px;font-weight:700;letter-spacing:.08em;
  text-transform:uppercase;color:#94A3B8;}

/* Benchmark widget */
.bm-stat{background:#F8FAFF;border:1px solid #EEF2FF;border-radius:14px;
  padding:1.1rem 1.3rem;text-align:center;}
.bm-val{font-family:Poppins,sans-serif;font-size:1.6rem;font-weight:900;color:#4F46E5;line-height:1;}
.bm-lbl{font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
  color:#94A3B8;margin-top:4px;}
.bm-cmp{background:white;border-radius:16px;padding:1.2rem 1.5rem;
  border:1.5px solid #DCFCE7;margin-top:12px;animation:riseIn .4s both;}
.bm-ratio{font-family:Poppins,sans-serif;font-size:2rem;font-weight:900;
  color:#059669;line-height:1;}
.bm-ratio.below{color:#D97706;}

/* Neighbourhood grid */
.nh-card{background:white;border-radius:16px;padding:1.1rem 1.2rem;
  border:1.5px solid #EEF2FF;text-align:center;cursor:pointer;
  transition:all .2s cubic-bezier(.34,1.56,.64,1);}
.nh-card:hover{border-color:#C7D2FE;box-shadow:0 6px 22px rgba(79,70,229,.12);transform:translateY(-4px);}
.nh-name{font-family:Poppins,sans-serif;font-weight:700;font-size:13px;color:#0F172A;margin-bottom:6px;}
.nh-count{display:inline-flex;align-items:center;justify-content:center;
  background:#EEF2FF;color:#4F46E5;border:1.5px solid #C7D2FE;
  border-radius:999px;font-size:13px;font-weight:800;
  font-family:Poppins,sans-serif;min-width:36px;height:36px;padding:0 10px;}

/* Format bar chart */
.fmt-bar-wrap{margin-bottom:10px;}
.fmt-lbl{font-size:13px;font-weight:600;color:#0F172A;margin-bottom:4px;
  display:flex;justify-content:space-between;}
.fmt-bar-bg{background:#F1F5F9;border-radius:99px;height:10px;overflow:hidden;}
.fmt-bar-fill{height:100%;border-radius:99px;transition:width .6s ease;}

/* Confidence legend */
.conf-legend{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px;}
.conf-item{display:inline-flex;align-items:center;gap:5px;
  font-size:11.5px;font-weight:600;color:#475569;}
</style>
""", unsafe_allow_html=True)

_SP   = "<div style='display:block;padding-top:1.8rem;width:100%'></div>"
_MINI = "<div style='display:block;padding-top:.75rem;width:100%'></div>"

NICHES = [
    "beauty", "fashion", "fitness", "food", "travel", "gaming",
    "tech", "parenting", "education", "business", "finance",
    "lifestyle", "art", "music", "sports", "sustainability", "pets", "books",
]

# ── Header ─────────────────────────────────────────────────────────────────────
hdr_a, hdr_b, hdr_spc, hdr_c = st.columns([2.2, 5, 4, 1.5])
with hdr_a:
    st.markdown(
        '<div class="sk-hdr" style="display:flex;align-items:center;gap:9px">'
        '<img src="app/static/skout-logo.png" style="height:30px;width:auto;display:block"></div>',
        unsafe_allow_html=True)
with hdr_b:
    st.markdown(
        '<div style="font-size:13px;font-weight:700;color:#0F172A;'
        'font-family:Poppins,sans-serif">📍 Local Market Intelligence</div>',
        unsafe_allow_html=True)
with hdr_c:
    if st.button("← Dashboard", use_container_width=True):
        st.switch_page(_P_HOME)

st.markdown(_SP, unsafe_allow_html=True)

# ── Load city list ─────────────────────────────────────────────────────────────
try:
    city_list = [r["city"] for r in local_cities() if r.get("city")]
except APIError:
    city_list = []

city_options = sorted(set(city_list)) if city_list else ["Toronto", "New York", "London", "Vancouver"]

# ── 4 tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆  Local Leaderboard",
    "📊  Industry Benchmarks",
    "🏘️  Neighbourhoods",
    "📈  Trending Formats",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LOCAL LEADERBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(_MINI, unsafe_allow_html=True)

    # Controls
    f1, f2, f3, _, f4 = st.columns([1.2, 1.2, 1, 2, 1])
    with f1:
        lb_city = st.selectbox("City", city_options, key="lb_city",
                               label_visibility="visible")
    with f2:
        lb_cat  = st.selectbox("Category", NICHES, key="lb_cat")
    with f3:
        lb_lim  = st.selectbox("Top", [5, 10, 20, 50], index=1, key="lb_lim")
    with f4:
        lb_refresh = st.button("🔄 Refresh Rankings", use_container_width=True, key="lb_ref")

    st.markdown(_MINI, unsafe_allow_html=True)

    # Location confidence legend
    st.markdown(
        '<div class="conf-legend">'
        '<span style="font-size:11px;font-weight:700;letter-spacing:.08em;'
        'text-transform:uppercase;color:#94A3B8;margin-right:4px">LOCATION CONFIDENCE:</span>'
        '<span class="conf-item">✅ HIGH — 3+ sources agree</span>'
        '<span class="conf-item">🟡 MEDIUM — 2 sources agree</span>'
        '<span class="conf-item">🟠 LOW — only self-reported</span>'
        '</div>',
        unsafe_allow_html=True)

    with st.spinner(f"Loading top {lb_lim} {lb_cat} creators in {lb_city}…"):
        try:
            board = local_leaderboard(lb_city, lb_cat, limit=lb_lim)
        except APIError as e:
            st.error(str(e))
            board = []

    if not board:
        st.markdown(
            '<div class="lm-card" style="text-align:center;padding:2.5rem">'
            '<div style="font-size:2.5rem;margin-bottom:.75rem">🏆</div>'
            '<div style="font-size:14px;font-weight:600;color:#0F172A">'
            f'No creators indexed for {lb_city} × {lb_cat}</div>'
            '<div style="font-size:12.5px;color:#94A3B8;margin-top:.4rem">'
            'Onboard creators from this city and category to build the leaderboard.</div>'
            '</div>',
            unsafe_allow_html=True)
    else:
        for entry in board:
            rank       = entry["rank"]
            name       = entry["display_name"] or "Creator"
            handle_ig  = entry.get("instagram_handle") or ""
            handle_tt  = entry.get("tiktok_handle") or ""
            handle     = handle_ig or handle_tt or ""
            followers  = entry.get("total_followers") or 0
            eng        = entry.get("avg_engagement_rate") or 0.0
            city_e     = entry.get("city") or ""
            hood       = entry.get("neighbourhood") or ""
            niches     = entry.get("niches") or []
            conf_lvl   = entry.get("location_confidence") or "LOW"
            open_c     = entry.get("open_to_collabs", True)
            avc        = _AVC[hash(name) % len(_AVC)]
            delay      = 0.04 + rank * 0.03

            rank_class = "top" if rank <= 3 else ""
            rank_icon  = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
            conf_badge = confidence_badge_html(conf_lvl)
            niche_str  = "  ·  ".join(
                f'{_NE.get(n, "")} {n.title()}' for n in niches[:3])
            loc_str    = "  ·  ".join(filter(None, [hood or city_e]))
            handle_str = f"@{handle}" if handle else ""
            avail_html = "" if open_c else ' <span style="font-size:11px;color:#DC2626">⏸</span>'

            card_col, eng_col, cta_col = st.columns([5.5, 1, 1.3])
            with card_col:
                st.markdown(
                    f'<div class="lb-row" style="animation-delay:{delay:.2f}s">'
                    f'<div class="lb-rank {rank_class}">{rank_icon}</div>'
                    f'<div class="lb-av" style="background:{avc}">{_ini(name)}</div>'
                    f'<div class="lb-info">'
                    f'<div class="lb-name">{name}{avail_html} &nbsp;{conf_badge}</div>'
                    f'<div class="lb-handle">{handle_str} &nbsp;·&nbsp; 👥 {_fmt(followers)}</div>'
                    f'<div class="lb-meta">'
                    + (f'📍 {loc_str} &nbsp;·&nbsp; ' if loc_str else '')
                    + (f'{niche_str}' if niche_str else '')
                    + f'</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True)
            with eng_col:
                eng_color = "#059669" if eng >= 0.05 else "#D97706" if eng >= 0.02 else "#94A3B8"
                st.markdown(
                    f'<div style="text-align:center;padding:.5rem">'
                    f'<div style="font-family:Poppins,sans-serif;font-size:1.15rem;'
                    f'font-weight:900;color:{eng_color}">{eng:.1%}</div>'
                    f'<div style="font-size:9.5px;font-weight:700;letter-spacing:.08em;'
                    f'text-transform:uppercase;color:#94A3B8">Engagement</div>'
                    f'</div>',
                    unsafe_allow_html=True)
            with cta_col:
                st.page_link(_P_OUTREACH, label="✉️ Work Together", use_container_width=True)

        # Admin recalculate
        with st.expander("⚙️ Admin"):
            if st.button("Recalculate All Benchmarks", key="admin_recalc"):
                with st.spinner("Recalculating…"):
                    try:
                        r = local_recalculate_benchmarks()
                        st.success(f"Done — {r.get('rows_upserted', 0)} rows updated for {r.get('month_year')}.")
                    except APIError as e:
                        st.error(str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — INDUSTRY BENCHMARKS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(_MINI, unsafe_allow_html=True)

    bc1, bc2 = st.columns(2)
    with bc1:
        bm_city = st.selectbox("City", city_options, key="bm_city")
    with bc2:
        bm_cat  = st.selectbox("Category", NICHES, key="bm_cat")

    st.markdown(_MINI, unsafe_allow_html=True)

    with st.spinner(f"Loading {bm_city} × {bm_cat} benchmarks…"):
        try:
            bm = local_benchmarks(bm_city, bm_cat)
        except APIError as e:
            st.error(str(e))
            bm = {}

    n_creators = bm.get("creator_count", 0)

    if n_creators == 0:
        st.markdown(
            '<div class="lm-card" style="text-align:center;padding:2rem">'
            f'<div style="font-size:14px;font-weight:600;color:#0F172A">'
            f'No data for {bm_city} × {bm_cat}</div>'
            '<div style="font-size:12.5px;color:#94A3B8;margin-top:.4rem">'
            'Onboard creators from this city and category to generate benchmarks.</div>'
            '</div>',
            unsafe_allow_html=True)
    else:
        avg_eng = bm.get("avg_engagement_rate", 0)
        avg_fol = bm.get("avg_followers", 0)
        month   = bm.get("month_year", "—")

        # Stat cards
        s1, s2, s3 = st.columns(3)
        for col, val, lbl in [
            (s1, f"{avg_eng:.2%}", "Avg Engagement Rate"),
            (s2, _fmt(int(avg_fol)), "Avg Followers"),
            (s3, str(n_creators), f"Creators in {bm_city} × {bm_cat.title()}"),
        ]:
            with col:
                st.markdown(
                    f'<div class="bm-stat">'
                    f'<div class="bm-val">{val}</div>'
                    f'<div class="bm-lbl">{lbl}</div>'
                    f'</div>',
                    unsafe_allow_html=True)

        st.markdown(_MINI, unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:11px;font-weight:700;letter-spacing:.1em;'
            f'text-transform:uppercase;color:#94A3B8">Data period: {month}</div>',
            unsafe_allow_html=True)

    # ── Creator Comparison ─────────────────────────────────────────────────────
    st.markdown(_SP, unsafe_allow_html=True)
    st.markdown(
        '<div style="font-family:Poppins,sans-serif;font-weight:700;font-size:1rem;'
        'color:#0F172A;margin-bottom:.5rem">Compare a creator to this benchmark</div>',
        unsafe_allow_html=True)

    cmp_id = st.text_input("Creator ID", placeholder="Paste creator UUID from their profile…", key="cmp_id")
    if st.button("Compare →", key="cmp_btn") and cmp_id.strip():
        with st.spinner("Comparing…"):
            try:
                cmp = local_creator_vs_benchmark(cmp_id.strip(), bm_city, bm_cat)
            except APIError as e:
                st.error(str(e))
                cmp = {}

        if cmp and "ratio" in cmp and cmp["ratio"] is not None:
            ratio     = cmp["ratio"]
            direction = cmp.get("direction", "above")
            c_eng     = cmp.get("creator_engagement", 0)
            c_fol     = cmp.get("creator_followers", 0)
            message   = cmp.get("message", "")
            bm_avg    = (cmp.get("benchmark") or {}).get("avg_engagement_rate", 0)

            ratio_color = "#059669" if direction == "above" else "#D97706"
            ratio_class = "bm-ratio" if direction == "above" else "bm-ratio below"

            st.markdown(
                f'<div class="bm-cmp">'
                f'<div style="display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap">'
                f'<div><div class="{ratio_class}">{ratio}x</div>'
                f'<div style="font-size:10px;font-weight:700;letter-spacing:.08em;'
                f'text-transform:uppercase;color:#94A3B8">the local average</div></div>'
                f'<div style="flex:1;min-width:180px">'
                f'<div style="font-size:14px;font-weight:600;color:#0F172A;margin-bottom:6px">'
                f'{cmp.get("creator_name","")}</div>'
                f'<div style="font-size:13px;color:#64748B">{message}</div>'
                f'<div style="font-size:12px;color:#94A3B8;margin-top:4px">'
                f'👥 {_fmt(c_fol)} followers</div>'
                f'</div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True)
        elif cmp:
            st.info(cmp.get("message", "No comparison data available."))


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — NEIGHBOURHOODS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(_MINI, unsafe_allow_html=True)

    nh_city = st.selectbox(
        "City",
        ["Toronto", "New York", "Los Angeles", "London", "Vancouver", "Sydney", "Berlin", "Singapore"]
        + sorted(set(city_options) - {"Toronto", "New York", "Los Angeles", "London", "Vancouver"}),
        key="nh_city",
    )

    with st.spinner(f"Loading neighbourhoods for {nh_city}…"):
        try:
            hoods = local_neighbourhoods(nh_city)
        except APIError as e:
            st.error(str(e))
            hoods = []

    if not hoods:
        st.markdown(
            '<div class="lm-card" style="text-align:center;padding:2rem">'
            f'<div style="font-size:14px;color:#64748B">'
            f'No neighbourhood data for {nh_city}.</div>'
            '</div>',
            unsafe_allow_html=True)
    else:
        total_c = sum(h.get("creator_count", 0) for h in hoods)
        st.markdown(
            f'<div style="font-size:12px;color:#94A3B8;margin-bottom:1rem">'
            f'{len(hoods)} neighbourhoods in {nh_city} · {total_c} creators have set their neighbourhood</div>',
            unsafe_allow_html=True)

        # Grid — 4 per row
        for row_start in range(0, len(hoods), 4):
            cols = st.columns(4, gap="medium")
            for j, hood in enumerate(hoods[row_start:row_start + 4]):
                with cols[j]:
                    cnt = hood.get("creator_count", 0)
                    cnt_html = (
                        f'<span class="nh-count">{cnt}</span>'
                        if cnt > 0
                        else f'<span class="nh-count" style="background:#F8FAFC;color:#94A3B8;border-color:#E2E8F0">0</span>'
                    )
                    st.markdown(
                        f'<div class="nh-card">'
                        f'<div class="nh-name">{hood["name"]}</div>'
                        f'{cnt_html}'
                        f'<div style="font-size:10px;color:#94A3B8;margin-top:5px">creators</div>'
                        f'</div>',
                        unsafe_allow_html=True)

        # Creator drill-down
        st.markdown(_SP, unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family:Poppins,sans-serif;font-weight:700;font-size:.95rem;'
            'color:#0F172A;margin-bottom:.5rem">Explore a neighbourhood</div>',
            unsafe_allow_html=True)

        hood_names = [h["name"] for h in hoods]
        selected_hood = st.selectbox("Select neighbourhood", hood_names, key="sel_hood")
        if selected_hood:
            with st.spinner(f"Loading creators in {selected_hood}…"):
                try:
                    nh_creators = local_neighbourhood_creators(selected_hood, nh_city)
                except APIError as e:
                    nh_creators = []

            if not nh_creators:
                st.markdown(
                    f'<div class="lm-card" style="padding:1.2rem;text-align:center;color:#94A3B8">'
                    f'No creators have listed {selected_hood} as their neighbourhood yet.</div>',
                    unsafe_allow_html=True)
            else:
                for c in nh_creators[:10]:
                    name    = c.get("display_name") or c.get("full_name") or "Creator"
                    handle  = c.get("instagram_handle") or c.get("tiktok_handle") or ""
                    fol     = c.get("total_followers") or 0
                    eng     = c.get("avg_engagement_rate") or 0.0
                    niches  = c.get("niches") or []
                    avc     = _AVC[hash(name) % len(_AVC)]
                    st.markdown(
                        f'<div class="lb-row">'
                        f'<div class="lb-av" style="background:{avc}">{_ini(name)}</div>'
                        f'<div class="lb-info">'
                        f'<div class="lb-name">{name}</div>'
                        f'<div class="lb-handle">{"@" + handle if handle else ""} &nbsp;·&nbsp; 👥 {_fmt(fol)}</div>'
                        f'<div class="lb-meta">📊 {eng:.1%} engagement &nbsp;·&nbsp; '
                        + "  ".join(f'{_NE.get(n,"")} {n}' for n in niches[:3])
                        + f'</div></div></div>',
                        unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — TRENDING FORMATS
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(_MINI, unsafe_allow_html=True)

    tf1, tf2 = st.columns(2)
    with tf1:
        tf_city = st.selectbox("City", city_options, key="tf_city")
    with tf2:
        tf_cat  = st.selectbox("Category", NICHES, key="tf_cat")

    st.markdown(_MINI, unsafe_allow_html=True)

    with st.spinner(f"Analyzing content formats for {tf_city} × {tf_cat}…"):
        try:
            tf = local_trending_formats(tf_city, tf_cat)
        except APIError as e:
            st.error(str(e))
            tf = {}

    if not tf.get("data_available"):
        creators_in_area = tf.get("creators_in_area", 0)
        posts_tracked    = tf.get("posts_tracked", 0)
        reason           = tf.get("reason", "Not enough data")

        st.markdown(
            '<div class="lm-card" style="padding:2rem">'
            '<div style="font-size:1.5rem;margin-bottom:.75rem">📈</div>'
            '<div style="font-family:Poppins,sans-serif;font-weight:700;font-size:.95rem;'
            'color:#0F172A;margin-bottom:.4rem">Trending Formats — coming soon</div>'
            f'<div style="font-size:13px;color:#64748B;margin-bottom:1rem">{reason}</div>'
            '<div style="background:#F8FAFF;border:1px solid #EEF2FF;border-radius:12px;'
            'padding:1rem;font-size:12.5px;color:#64748B;line-height:1.8">'
            + (f'<b>{creators_in_area}</b> creators indexed in this area<br>' if creators_in_area else '')
            + (f'<b>{posts_tracked}</b> posts tracked (need at least 5)<br>' if posts_tracked is not None else '')
            + 'This widget activates automatically once creator posts are ingested via the post ingestion pipeline.'
            '</div>'
            '<div style="margin-top:1.2rem;padding:.9rem 1.1rem;background:#EEF2FF;'
            'border-radius:12px;font-size:12px;color:#4F46E5">'
            '<b>How formats are tracked:</b> Each post submitted via the POST /posts endpoint '
            'is tagged with platform + format (Reel, Carousel, Static, Story). '
            'Once 5+ posts are tracked for this city × category, this widget activates.'
            '</div>'
            '</div>',
            unsafe_allow_html=True)

        # Preview widget design
        st.markdown(_MINI, unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:11px;font-weight:700;letter-spacing:.1em;'
            'text-transform:uppercase;color:#94A3B8;margin-bottom:.75rem">'
            'Widget preview (demo data)</div>',
            unsafe_allow_html=True)

        demo_formats = [
            ("📹 Reel",     0.084, "#4F46E5"),
            ("📱 Story",    0.031, "#7C3AED"),
            ("🎠 Carousel", 0.022, "#8B5CF6"),
            ("📸 Static",   0.018, "#A78BFA"),
        ]
        max_eng = max(f[1] for f in demo_formats)

        demo_card, _ = st.columns([2, 1])
        with demo_card:
            st.markdown(
                '<div class="lm-card">'
                '<div style="font-family:Poppins,sans-serif;font-weight:700;font-size:13.5px;'
                'color:#0F172A;margin-bottom:4px">📈 Format Engagement Breakdown</div>'
                '<div style="font-size:11.5px;color:#94A3B8;margin-bottom:1rem">Demo data — not real</div>',
                unsafe_allow_html=True)
            for label, eng, color in demo_formats:
                pct  = eng / max_eng * 100
                st.markdown(
                    f'<div class="fmt-bar-wrap">'
                    f'<div class="fmt-lbl"><span>{label}</span><span style="color:{color};font-weight:700">{eng:.1%}</span></div>'
                    f'<div class="fmt-bar-bg"><div class="fmt-bar-fill" style="width:{pct:.0f}%;background:{color}"></div></div>'
                    f'</div>',
                    unsafe_allow_html=True)
            st.markdown(
                '<div style="margin-top:1rem;padding:.75rem 1rem;background:#EEF2FF;'
                'border-radius:10px;font-size:12.5px;color:#4F46E5;font-weight:600">'
                '📹 Reels are getting <b>3.8x</b> more engagement than Carousels (demo)'
                '</div>'
                '</div>',
                unsafe_allow_html=True)

    else:
        formats      = tf.get("formats", [])
        headline     = tf.get("headline", "")
        posts_tracked = tf.get("posts_tracked", 0)

        if headline:
            st.markdown(
                f'<div class="lm-card" style="background:linear-gradient(135deg,#4338CA,#4F46E5);'
                f'padding:1.2rem 1.5rem;margin-bottom:1rem">'
                f'<div style="font-size:1.4rem;margin-bottom:.4rem">📈</div>'
                f'<div style="font-family:Poppins,sans-serif;font-weight:700;font-size:15px;'
                f'color:#fff;line-height:1.4">{headline}</div>'
                f'<div style="font-size:11.5px;color:rgba(255,255,255,.6);margin-top:4px">'
                f'Based on {posts_tracked} posts tracked this month</div>'
                f'</div>',
                unsafe_allow_html=True)

        if formats:
            max_eng = max(f["avg_engagement"] for f in formats)
            FORMAT_ICONS = {"Reel": "📹", "Carousel": "🎠", "Static": "📸", "Story": "📱", "Video": "▶️"}
            FORMAT_COLORS = ["#4F46E5", "#7C3AED", "#059669", "#D97706", "#0891B2"]

            bar_col, _ = st.columns([2.5, 1])
            with bar_col:
                st.markdown('<div class="lm-card">', unsafe_allow_html=True)
                st.markdown(
                    '<div style="font-family:Poppins,sans-serif;font-weight:700;font-size:13.5px;'
                    'color:#0F172A;margin-bottom:1rem">Format Engagement Breakdown</div>',
                    unsafe_allow_html=True)
                for i, f in enumerate(formats):
                    pct   = f["avg_engagement"] / max_eng * 100
                    icon  = FORMAT_ICONS.get(f["format"], "")
                    color = FORMAT_COLORS[i % len(FORMAT_COLORS)]
                    st.markdown(
                        f'<div class="fmt-bar-wrap">'
                        f'<div class="fmt-lbl">'
                        f'<span>{icon} {f["format"]} <span style="color:#94A3B8;font-size:11px">({f["post_count"]} posts)</span></span>'
                        f'<span style="color:{color};font-weight:800">{f["avg_engagement"]:.1%}</span>'
                        f'</div>'
                        f'<div class="fmt-bar-bg">'
                        f'<div class="fmt-bar-fill" style="width:{pct:.0f}%;background:{color}"></div>'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
