from pathlib import Path

import streamlit as st

from database import (
    recent_activity,
    successful_jobs_count,
    workspace_activity_score,
)

from config import PLANS


ASSET_DIR = Path("assets")


def open_page(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def format_number(value) -> str:
    try:
        return f"{int(value):,}".replace(",", ".")
    except Exception:
        return str(value)


def asset_path(name: str) -> Path:
    return ASSET_DIR / f"{name}.png"


def home_css() -> None:
    st.markdown(
        """
<style>
.main .block-container {
    max-width: 1360px !important;
    padding-top: 90px !important;
    padding-bottom: 90px !important;
}

.mb-hero {
    background:
        radial-gradient(circle at top right, rgba(168,85,247,.24), transparent 34%),
        radial-gradient(circle at top left, rgba(96,165,250,.16), transparent 34%),
        linear-gradient(135deg, rgba(12,18,42,.96), rgba(7,8,20,.98));
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 34px;
    padding: 38px;
    margin-bottom: 26px;
    box-shadow: 0 28px 70px rgba(0,0,0,.34);
}

.mb-kicker {
    color: #c084fc !important;
    font-size: 12px;
    font-weight: 1000;
    letter-spacing: .22em;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.mb-title {
    color: #ffe7a3 !important;
    font-size: 58px;
    line-height: .94;
    font-weight: 1000;
    letter-spacing: -2.8px;
}

.mb-sub {
    margin-top: 14px;
    max-width: 760px;
    color: #cbd5e1 !important;
    font-size: 16px;
    line-height: 1.55;
    font-weight: 700;
}

.mb-badge {
    display: inline-flex;
    padding: 8px 15px;
    border-radius: 999px;
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: #ffffff !important;
    font-size: 13px;
    font-weight: 1000;
    box-shadow: 0 0 28px rgba(168,85,247,.30);
    margin-left: 12px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.10), transparent 32%),
        linear-gradient(145deg, rgba(12,13,32,.92), rgba(6,7,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.16) !important;
    border-radius: 26px !important;
    box-shadow: 0 18px 45px rgba(0,0,0,.24) !important;
}

.stButton > button {
    min-height: 46px !important;
    border-radius: 16px !important;
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.22), transparent 34%),
        linear-gradient(145deg, rgba(36,8,56,.98), rgba(12,3,25,.98)) !important;
    border: 1px solid rgba(168,85,247,.34) !important;
    color: #ffe7a3 !important;
    font-size: 15px !important;
    font-weight: 1000 !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(255,231,163,.36) !important;
    box-shadow: 0 0 26px rgba(168,85,247,.26) !important;
}

[data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(18,14,34,.88), rgba(8,7,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.18) !important;
    border-radius: 22px !important;
    padding: 18px !important;
}

[data-testid="metric-container"] label {
    color: #c084fc !important;
    font-size: 11px !important;
    font-weight: 1000 !important;
    text-transform: uppercase !important;
}

[data-testid="metric-container"] div {
    color: #ffe7a3 !important;
    font-weight: 1000 !important;
}

.mb-card-title {
    color: #ffffff !important;
    font-size: 20px;
    font-weight: 1000;
    margin-top: 10px;
    margin-bottom: 5px;
}

.mb-card-sub {
    color: #94a3b8 !important;
    font-size: 13px;
    line-height: 1.45;
}

.mb-section-title {
    color: #ffe7a3 !important;
    font-size: 24px;
    font-weight: 1000;
    margin-bottom: 14px;
}

.mb-small {
    color: #94a3b8 !important;
    font-size: 13px;
}

.mb-status {
    display: inline-flex;
    padding: 6px 11px;
    border-radius: 999px;
    background: rgba(34,197,94,.12);
    border: 1px solid rgba(34,197,94,.24);
    color: #86efac !important;
    font-size: 12px;
    font-weight: 1000;
}

.mb-activity-title {
    color: #ffffff !important;
    font-size: 15px;
    font-weight: 1000;
}

.mb-activity-sub {
    color: #94a3b8 !important;
    font-size: 13px;
}

@media(max-width: 1100px) {
    .mb-title {
        font-size: 42px;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_icon(name: str, width: int = 42) -> None:
    path = asset_path(name)
    if path.exists():
        st.image(str(path), width=width)
    else:
        st.write("")


def app_card(icon: str, title: str, sub: str, page: str, key: str) -> None:
    with st.container(border=True):
        render_icon(icon, 42)
        st.markdown(f'<div class="mb-card-title">{title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="mb-card-sub">{sub}</div>', unsafe_allow_html=True)
        st.write("")
        if st.button("Open", key=key, width="stretch"):
            open_page(page)


def render_activity(user: str) -> None:
    items = recent_activity(username=user, limit=5)

    if not items:
        items = [
            {"tool": "Reels Studio", "created_at": "ready"},
            {"tool": "AI Assistant", "created_at": "ready"},
            {"tool": "Automation", "created_at": "ready"},
        ]

    for item in items:
        tool = str(item.get("tool", "system")).replace("_", " ").title()
        created = str(item.get("created_at", ""))[:16]

        with st.container(border=True):
            st.markdown(f'<div class="mb-activity-title">{tool}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="mb-activity-sub">Activity · {created}</div>', unsafe_allow_html=True)


def render_home() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    home_css()

    user = st.session_state.get("user", "User")
    plan = st.session_state.get("plan", "free")
    tokens = int(st.session_state.get("tokens", 0) or 0)

    plan_data = PLANS.get(plan, PLANS["free"])
    plan_label = plan_data.get("label", "Free")

    jobs = successful_jobs_count(user)
    score = workspace_activity_score(user)

    st.markdown(
        f"""
<div class="mb-hero">
    <div class="mb-kicker">Mission Control</div>
    <div class="mb-title">
        MaByte OS
        <span class="mb-badge">{plan_label}</span>
    </div>
    <div class="mb-sub">
        Willkommen zurück, {user}. Dein Creator Operating System für AI, Reels, Automationen, Football Intelligence und Projekte.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    a1, a2, a3 = st.columns([1, 1, 1], gap="medium")

    with a1:
        if st.button("Create Reel", width="stretch"):
            open_page("reels")

    with a2:
        if st.button("Open Chat", width="stretch"):
            open_page("chat")

    with a3:
        if st.button("Automation", width="stretch"):
            open_page("automation_lab")

    st.write("")

    s1, s2, s3, s4 = st.columns(4, gap="medium")

    with s1:
        st.metric("Tokens", format_number(tokens), "Available")

    with s2:
        st.metric("Jobs", jobs, "Successful")

    with s3:
        st.metric("Activity", f"{score}/100", "Workspace")

    with s4:
        st.metric("Plan", plan_label, "Current")

    st.write("")

    st.markdown('<div class="mb-section-title">AI Workspaces</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5, gap="medium")

    with c1:
        app_card("chat", "Assistant", "Strategy, coding, support", "chat", "home_chat")

    with c2:
        app_card("video", "Reels", "Shortform creator engine", "reels", "home_reels")

    with c3:
        app_card("image", "Image AI", "Thumbnails and visuals", "image", "home_image")

    with c4:
        app_card("football", "Football", "Matchday intelligence", "football", "home_football")

    with c5:
        app_card("automations", "Automation", "Creator workflows", "automation_lab", "home_auto")

    st.write("")

    left, right = st.columns([1.45, 1], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<div class="mb-section-title">Live Activity</div>', unsafe_allow_html=True)
            render_activity(user)

    with right:
        with st.container(border=True):
            st.markdown('<div class="mb-section-title">System Status</div>', unsafe_allow_html=True)
            st.markdown('<span class="mb-status">Reels Online</span>', unsafe_allow_html=True)
            st.write("")
            st.markdown('<span class="mb-status">Image AI Ready</span>', unsafe_allow_html=True)
            st.write("")
            st.markdown('<span class="mb-status">Automation Ready</span>', unsafe_allow_html=True)
            st.write("")
            st.markdown('<div class="mb-small">TikTok / Instagram Connect kommt als nächstes.</div>', unsafe_allow_html=True)

        st.write("")

        with st.container(border=True):
            st.markdown('<div class="mb-section-title">Next Focus</div>', unsafe_allow_html=True)
            st.markdown('<div class="mb-card-sub">1. Reels Studio finalisieren<br>2. Video API anbinden<br>3. Social Connect bauen<br>4. Auto Posting aktivieren</div>', unsafe_allow_html=True)

    st.write("")

    with st.container(border=True):
        st.markdown('<div class="mb-section-title">Creator OS Layer</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="mb-card-sub">{format_number(tokens)} Tokens verfügbar. MaByte ist bereit für AI Content, Video Workflows und Automationen.</div>',
            unsafe_allow_html=True,
        )