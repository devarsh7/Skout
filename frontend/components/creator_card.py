"""Reusable creator result card — compact app-style row."""
from __future__ import annotations

import streamlit as st

_NICHE_COLORS: dict[str, str] = {
    "beauty":         "#FDF2F8,#F9A8D4,#9D174D",
    "fashion":        "#F5F3FF,#C4B5FD,#5B21B6",
    "fitness":        "#ECFDF5,#6EE7B7,#065F46",
    "food":           "#FFF7ED,#FCD34D,#92400E",
    "travel":         "#EFF6FF,#93C5FD,#1E40AF",
    "gaming":         "#F0FDF4,#86EFAC,#14532D",
    "tech":           "#F0F9FF,#7DD3FC,#0C4A6E",
    "lifestyle":      "#FFFBEB,#FDE68A,#78350F",
    "sustainability": "#ECFDF5,#A7F3D0,#064E3B",
    "pets":           "#FFF1F2,#FCA5A5,#881337",
    "music":          "#F5F3FF,#DDD6FE,#4C1D95",
    "sports":         "#EFF6FF,#BFDBFE,#1D4ED8",
}


def _niche_style(niche: str) -> str:
    colors = _NICHE_COLORS.get(niche, "var(--bg-alt),var(--border),var(--muted)")
    parts = colors.split(",")
    if len(parts) == 3:
        return f"background:{parts[0]};border:1px solid {parts[1]};color:{parts[2]}"
    return "background:var(--bg-alt);border:1px solid var(--border);color:var(--muted)"


def _fmt_num(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def _score_color(score: float) -> tuple[str, str]:
    if score >= 0.85:
        return "#065F46", "#D1FAE5"
    if score >= 0.70:
        return "#1D4ED8", "#DBEAFE"
    return "#92400E", "#FEF3C7"


def render_creator_card(hit: dict) -> None:
    creator    = hit["creator"]
    score      = hit.get("score", 0.0)
    reason     = hit.get("reason", "")
    cid        = creator["id"]
    niches     = creator.get("niches", []) or []
    handles    = creator.get("handles", {}) or {}
    followers  = creator.get("total_followers", 0) or 0
    engagement = (creator.get("avg_engagement_rate") or 0) * 100
    loc        = ", ".join(filter(None, [creator.get("city"), creator.get("country")]))
    bio        = creator.get("bio") or ""
    name       = creator.get("display_name") or "—"

    sc_text, sc_bg = _score_color(score)

    # ── build HTML parts as plain strings (no blank lines when empty) ──────────

    niche_pills = "".join(
        f'<span style="display:inline-flex;align-items:center;{_niche_style(n)};'
        f'border-radius:5px;font-size:11px;font-weight:600;padding:2px 7px;'
        f'font-family:var(--fb);margin-right:4px">{n}</span>'
        for n in niches[:4]
    )

    handle_parts = []
    if handles.get("instagram"):
        h = handles["instagram"].lstrip("@")
        handle_parts.append(f'<a href="https://instagram.com/{h}" target="_blank" style="font-size:12px;color:var(--muted);text-decoration:none">IG @{h}</a>')
    if handles.get("tiktok"):
        h = handles["tiktok"].lstrip("@")
        handle_parts.append(f'<a href="https://tiktok.com/@{h}" target="_blank" style="font-size:12px;color:var(--muted);text-decoration:none">TT @{h}</a>')
    if handles.get("youtube"):
        handle_parts.append(f'<a href="{handles["youtube"]}" target="_blank" style="font-size:12px;color:var(--muted);text-decoration:none">YouTube</a>')
    handles_html = ' <span style="color:var(--border)">·</span> '.join(handle_parts)

    loc_span     = f'<span style="font-size:12px;color:var(--muted)">{loc}</span>' if loc else ""
    handles_span = f'<span style="font-size:11.5px;color:var(--muted)">{handles_html}</span>' if handles_html else ""
    bio_div      = f'<div style="font-size:12px;color:var(--muted);line-height:1.55;max-width:640px;margin-top:5px">{bio[:160]}{"…" if len(bio) > 160 else ""}</div>' if bio else ""
    niche_div    = f'<div style="margin-bottom:5px">{niche_pills}</div>' if niche_pills else ""
    reason_div   = (
        f'<div style="background:var(--blue-50);border-left:3px solid var(--blue-400);'
        f'border-radius:0 6px 6px 0;padding:6px 12px;margin-top:8px;'
        f'font-size:12px;color:var(--muted);line-height:1.5">'
        f'<strong style="color:var(--navy)">Why:</strong> {reason}</div>'
    ) if reason else ""

    # ── assemble — NO blank lines anywhere ─────────────────────────────────────
    html = (
        '<div style="background:#fff;border:1px solid var(--border);border-radius:10px;'
        'padding:14px 18px 12px;margin-bottom:8px;">'
        '<div style="display:grid;grid-template-columns:1fr auto;gap:16px;align-items:start">'
        '<div>'
        f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:4px">'
        f'<span style="font-family:var(--fd);font-weight:700;font-size:14px;color:var(--navy)">{name}</span>'
        f'{loc_span}'
        f'{handles_span}'
        '</div>'
        f'{niche_div}'
        f'{bio_div}'
        '</div>'
        f'<div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;flex-shrink:0">'
        f'<div style="background:{sc_bg};color:{sc_text};border-radius:7px;'
        f'font-family:var(--fd);font-weight:800;font-size:13px;padding:4px 11px;white-space:nowrap">'
        f'{score:.2f} match</div>'
        f'<div style="text-align:right">'
        f'<div style="font-family:var(--fd);font-weight:700;font-size:13px;color:var(--navy)">{_fmt_num(followers)}</div>'
        f'<div style="font-size:11px;color:var(--muted)">followers</div>'
        '</div>'
        f'<div style="text-align:right">'
        f'<div style="font-family:var(--fd);font-weight:700;font-size:13px;color:var(--navy)">{engagement:.2f}%</div>'
        f'<div style="font-size:11px;color:var(--muted)">engagement</div>'
        '</div>'
        '</div>'
        '</div>'
        f'{reason_div}'
        '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)

    # Action buttons — st.switch_page for same-tab navigation
    a1, a2, _ = st.columns([1, 1, 4])
    if a1.button("View contact", key=f"view_{cid}"):
        st.session_state["selected_creator_id"] = cid
        st.switch_page("pages/5_📊_Campaigns.py")
    if a2.button("Draft outreach", key=f"out_{cid}"):
        st.session_state["outreach_creator_id"]   = cid
        st.session_state["outreach_creator_name"] = name
        st.switch_page("pages/4_✉️_AI_Outreach.py")
