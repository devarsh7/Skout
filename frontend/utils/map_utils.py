"""Shared map helpers — coordinate lookup, DataFrame builder, pydeck renderer."""
from __future__ import annotations

import math

import pandas as pd
import pydeck as pdk
import streamlit as st

# ── city / country coordinates ────────────────────────────────────────────────
_CITY: dict[tuple, tuple] = {
    ("mumbai","IN"):(19.076,72.877),("delhi","IN"):(28.614,77.209),
    ("new delhi","IN"):(28.614,77.209),("bangalore","IN"):(12.972,77.594),
    ("bengaluru","IN"):(12.972,77.594),("hyderabad","IN"):(17.387,78.491),
    ("chennai","IN"):(13.083,80.270),("kolkata","IN"):(22.573,88.364),
    ("pune","IN"):(18.520,73.857),("ahmedabad","IN"):(23.023,72.571),
    ("new york","US"):(40.713,-74.006),("nyc","US"):(40.713,-74.006),
    ("los angeles","US"):(34.052,-118.244),("chicago","US"):(41.878,-87.630),
    ("houston","US"):(29.760,-95.370),("dallas","US"):(32.776,-96.797),
    ("austin","US"):(30.267,-97.743),("seattle","US"):(47.606,-122.332),
    ("miami","US"):(25.774,-80.194),("boston","US"):(42.361,-71.057),
    ("san francisco","US"):(37.774,-122.419),("sf","US"):(37.774,-122.419),
    ("atlanta","US"):(33.749,-84.388),("las vegas","US"):(36.175,-115.137),
    ("london","GB"):(51.507,-0.128),("manchester","GB"):(53.481,-2.244),
    ("edinburgh","GB"):(55.953,-3.189),("paris","FR"):(48.857,2.352),
    ("berlin","DE"):(52.520,13.405),("munich","DE"):(48.137,11.576),
    ("madrid","ES"):(40.417,-3.704),("barcelona","ES"):(41.385,2.173),
    ("rome","IT"):(41.902,12.496),("milan","IT"):(45.465,9.188),
    ("amsterdam","NL"):(52.366,4.904),("stockholm","SE"):(59.334,18.063),
    ("oslo","NO"):(59.913,10.752),("copenhagen","DK"):(55.676,12.568),
    ("zurich","CH"):(47.377,8.540),("vienna","AT"):(48.209,16.373),
    ("lisbon","PT"):(38.718,-9.140),("warsaw","PL"):(52.230,21.012),
    ("prague","CZ"):(50.076,14.438),("athens","GR"):(37.984,23.728),
    ("istanbul","TR"):(41.015,28.980),("toronto","CA"):(43.651,-79.347),
    ("vancouver","CA"):(49.247,-123.116),("montreal","CA"):(45.502,-73.569),
    ("sydney","AU"):(-33.868,151.209),("melbourne","AU"):(-37.813,144.963),
    ("brisbane","AU"):(-27.470,153.026),("perth","AU"):(-31.953,115.861),
    ("tokyo","JP"):(35.681,139.767),("osaka","JP"):(34.693,135.502),
    ("seoul","KR"):(37.566,126.978),("beijing","CN"):(39.905,116.391),
    ("shanghai","CN"):(31.224,121.469),("hong kong","HK"):(22.320,114.170),
    ("singapore","SG"):(1.352,103.820),("taipei","TW"):(25.033,121.565),
    ("bangkok","TH"):(13.757,100.502),("jakarta","ID"):(-6.208,106.846),
    ("kuala lumpur","MY"):(3.140,101.687),("manila","PH"):(14.599,120.984),
    ("dubai","AE"):(25.204,55.270),("riyadh","SA"):(24.688,46.722),
    ("doha","QA"):(25.286,51.533),("sao paulo","BR"):(-23.549,-46.638),
    ("rio de janeiro","BR"):(-22.906,-43.173),("buenos aires","AR"):(-34.603,-58.382),
    ("mexico city","MX"):(19.433,-99.133),("bogota","CO"):(4.711,-74.073),
    ("cairo","EG"):(30.033,31.233),("lagos","NG"):(6.524,3.379),
    ("nairobi","KE"):(-1.286,36.820),("johannesburg","ZA"):(-26.195,28.034),
    ("cape town","ZA"):(-33.926,18.424),("moscow","RU"):(55.756,37.617),
    ("dhaka","BD"):(23.777,90.399),("karachi","PK"):(24.861,67.010),
}
_CC: dict[str, tuple] = {
    "AU":(-25.3,133.8),"BR":(-14.2,-51.9),"CA":(56.1,-106.3),"CN":(35.9,104.2),
    "DE":(51.2,10.5),"EG":(26.8,30.8),"ES":(40.5,-3.7),"FR":(46.2,2.2),
    "GB":(55.4,-3.4),"GH":(8.0,-1.0),"ID":(-0.8,113.9),"IN":(20.6,79.0),
    "IT":(41.9,12.6),"JP":(36.2,138.3),"KE":(-0.0,37.9),"KR":(35.9,127.8),
    "MA":(31.8,-7.1),"MX":(23.6,-102.6),"MY":(4.2,108.0),"NG":(9.1,8.7),
    "NL":(52.1,5.3),"NO":(60.5,8.5),"NZ":(-40.9,174.9),"PH":(12.9,121.8),
    "PK":(30.4,69.3),"PL":(51.9,19.1),"PT":(39.4,-8.2),"RU":(61.5,105.3),
    "SA":(23.9,45.1),"SE":(60.1,18.6),"SG":(1.4,103.8),"TH":(15.9,101.0),
    "TR":(39.0,35.2),"TW":(23.7,121.0),"UA":(48.4,31.2),"US":(37.1,-95.7),
    "ZA":(-30.6,22.9),"AE":(23.4,53.8),"AR":(-38.4,-63.6),"BD":(23.7,90.4),
    "BE":(50.5,4.5),"CH":(46.8,8.2),"CL":(-35.7,-71.5),"CO":(4.6,-74.3),
    "CZ":(49.8,15.5),"DK":(56.3,9.5),"GR":(39.1,21.8),"HK":(22.4,114.2),
    "IE":(53.4,-8.2),"IL":(31.0,34.9),"QA":(25.4,51.2),"RO":(45.9,25.0),
}

_NC: dict[str, list] = {
    "beauty":[236,72,153,230],"fashion":[249,115,22,230],"fitness":[16,185,129,230],
    "food":[234,179,8,230],"travel":[14,165,233,230],"gaming":[139,92,246,230],
    "tech":[6,182,212,230],"parenting":[244,114,182,230],"education":[59,130,246,230],
    "business":[20,184,166,230],"finance":[34,197,94,230],"lifestyle":[251,146,60,230],
    "art":[192,132,252,230],"music":[248,113,113,230],"sports":[74,222,128,230],
    "sustainability":[52,211,153,230],"pets":[253,186,116,230],"books":[167,139,250,230],
}
_DC = [37, 99, 235, 200]
_NE = {
    "beauty":"💄","fashion":"👗","fitness":"💪","food":"🍳","travel":"✈️",
    "gaming":"🎮","tech":"💻","parenting":"👶","education":"📚","business":"💼",
    "finance":"📈","lifestyle":"🌟","art":"🎨","music":"🎵","sports":"⚽",
    "sustainability":"🌱","pets":"🐾","books":"📖",
}
_AVC = ["#6366F1","#8B5CF6","#EC4899","#F59E0B","#10B981","#06B6D4","#EF4444","#3B82F6"]


def _fmt(n) -> str:
    n = int(n or 0)
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}K"
    return str(n)


def _ini(s: str) -> str:
    p = (s or "?").split()
    return (p[0][0] + (p[-1][0] if len(p) > 1 else "")).upper()


def _coords(city: str, country: str):
    if city:
        r = _CITY.get((city.lower().strip(), (country or "").upper()))
        if r:
            return r
    return _CC.get((country or "").upper())


def _map_df(creators: list) -> pd.DataFrame:
    rows, seen = [], {}
    for c in creators:
        co = (c.get("country") or "").upper()
        ci = c.get("city") or ""
        base = _coords(ci, co)
        if not base:
            continue
        key = f"{base[0]:.2f},{base[1]:.2f}"
        n = seen.get(key, 0)
        seen[key] = n + 1
        lat, lon = base
        if n:
            a = (n * 137.5) % 360
            s = 0.06 + n * 0.04
            lat += s * math.cos(math.radians(a))
            lon += s * math.sin(math.radians(a))
        niches = c.get("niches") or []
        p = niches[0] if niches else ""
        f = c.get("total_followers") or 0
        name = c.get("display_name") or c.get("full_name") or "Creator"
        h = c.get("instagram_handle") or c.get("tiktok_handle") or ""
        eng = c.get("avg_engagement_rate") or 0.0
        rows.append({
            "lat": lat, "lon": lon, "name": name,
            "handle": ("@" + h) if h else name,
            "followers": _fmt(f), "niche": p or "—",
            "eng": f"{eng:.1%}",
            "loc": ", ".join(filter(None, [ci, co])),
            "color": _NC.get(p, _DC),
        })
    cols = ["lat","lon","name","handle","followers","niche","eng","loc","color"]
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=cols)


def _draw_map(df: pd.DataFrame, height: int = 440) -> None:
    st.markdown(
        f"<style>[data-testid='stDeckGlJsonChart'] iframe"
        f"{{height:{height}px!important;min-height:{height}px!important;}}</style>",
        unsafe_allow_html=True)
    if df.empty:
        st.markdown(
            f'<div style="height:{height}px;background:#F8FAFC;'
            'display:flex;align-items:center;justify-content:center;'
            'flex-direction:column;gap:10px">'
            '<span style="font-size:2.5rem;opacity:.3">🗺️</span>'
            '<span style="font-size:13px;color:#94A3B8;font-weight:500">'
            'No creators match — adjust filters</span></div>',
            unsafe_allow_html=True)
        return
    layer = pdk.Layer(
        "ScatterplotLayer", data=df,
        get_position=["lon", "lat"], get_radius=55_000,
        get_fill_color="color", get_line_color=[255, 255, 255, 200],
        radius_min_pixels=7, radius_max_pixels=26,
        line_width_min_pixels=2, pickable=True,
        auto_highlight=True, highlight_color=[255, 255, 255, 100],
        stroked=True, filled=True)
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(latitude=20, longitude=10, zoom=1.3, pitch=0),
        map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
        tooltip={
            "html": (
                "<div style='font-family:\"Open Sans\",sans-serif;line-height:1.65'>"
                "<b style='font-size:14px;color:#0F172A'>{name}</b><br>"
                "<span style='color:#64748B;font-size:12px'>{handle} &middot; {loc}</span><br>"
                "<div style='margin-top:6px;display:flex;gap:12px;font-size:12.5px'>"
                "<span>👥 <b>{followers}</b></span>"
                "<span>📊 <b>{eng}</b></span>"
                "<span style='color:#6366F1'>🎯 {niche}</span></div></div>"
            ),
            "style": {
                "backgroundColor": "#fff", "color": "#0F172A",
                "borderRadius": "12px", "padding": "14px 18px",
                "border": "1px solid #E2E8F0",
                "boxShadow": "0 8px 40px rgba(15,23,42,.14)",
            },
        })
    st.pydeck_chart(deck, use_container_width=True)
