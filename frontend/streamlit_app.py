"""Skout — entry point / role-based router."""
from __future__ import annotations
import streamlit as st
from frontend.utils.session import restore_session
from frontend.utils.styles import (
    inject_css,
    _P_HOME, _P_BUSINESS_DASHBOARD, _P_CREATOR_DASHBOARD,
    _P_CREATOR, _P_BUSINESS,
    _P_DISCOVER, _P_FILTER, _P_OUTREACH, _P_CAMPAIGNS,
    _P_MAP, _P_AI_AGENT, _P_CREATOR_MATCH, _P_LOCAL_MARKET,
    _P_LOGIN, _P_SIGNUP, _P_UPDATE_PROFILE,
)

st.set_page_config(page_title="Skout", page_icon="🦉",
                   layout="wide", initial_sidebar_state="collapsed")
inject_css()
restore_session()

user = st.session_state.get("user")
role = user.get("role") if user else None

_TOOL_PAGES = [
    st.Page(_P_DISCOVER,      title="Discover Creators",  icon="🔍"),
    st.Page(_P_FILTER,        title="Filter & Refine",     icon="🎯"),
    st.Page(_P_OUTREACH,      title="AI Outreach",         icon="✉️"),
    st.Page(_P_CAMPAIGNS,     title="Campaigns",           icon="📊"),
    st.Page(_P_MAP,           title="Creator Map",         icon="🗺️"),
    st.Page(_P_AI_AGENT,      title="AI Agent",            icon="🤖"),
    st.Page(_P_CREATOR_MATCH, title="Creator Match",       icon="🎯"),
    st.Page(_P_LOCAL_MARKET,  title="Local Market",        icon="📍"),
]
_AUTH_PAGES = [
    st.Page(_P_HOME,     title="Home",            icon="🏠"),
    st.Page(_P_LOGIN,    title="Login",            icon="🔐"),
    st.Page(_P_SIGNUP,   title="Sign Up",          icon="📝"),
    st.Page(_P_CREATOR,  title="Creator Profile",  icon="🎤"),
    st.Page(_P_BUSINESS, title="Business Profile", icon="💼"),
]

if role == "creator":
    pg = st.navigation({
        "Creator Hub": [
            st.Page(_P_CREATOR_DASHBOARD, title="My Dashboard",      icon="🏠", default=True),
            st.Page(_P_UPDATE_PROFILE,    title="Update Profile",     icon="✏️"),
        ],
        "Explore":  _TOOL_PAGES,
        "Account":  _AUTH_PAGES + [st.Page(_P_BUSINESS_DASHBOARD, title="Business Dashboard", icon="💼")],
    }, position="hidden")

elif role == "business":
    pg = st.navigation({
        "Dashboard": [
            st.Page(_P_BUSINESS_DASHBOARD, title="Business Dashboard",  icon="💼", default=True),
        ],
        "Tools":   _TOOL_PAGES,
        "Account": _AUTH_PAGES + [st.Page(_P_CREATOR_DASHBOARD, title="Creator Dashboard", icon="🏠")],
    }, position="hidden")

else:
    pg = st.navigation([
        st.Page(_P_HOME,              title="Home",               icon="🦉", default=True),
        st.Page(_P_BUSINESS_DASHBOARD, title="Business Dashboard", icon="💼"),
        st.Page(_P_CREATOR_DASHBOARD,  title="Creator Dashboard",  icon="🏠"),
        *_TOOL_PAGES,
        *_AUTH_PAGES[1:],  # skip duplicate Home
    ], position="hidden")

pg.run()
