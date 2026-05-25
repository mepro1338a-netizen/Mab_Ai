from pathlib import Path

import streamlit as st

from database import (
    recent_activity,
    successful_jobs_count,
    workspace_activity_score,
)

from config import PLANS, FOOTBALL_PLANS, APP_TAGLINE
from ui.premium_foundation import inject_beta_global_css
from ui.styles import inject_css, page_layout_css


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
    inject_beta_global_css()
    inject_css(page_layout_css(1360, 90, 90) + """
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

.mb-pricing-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
}
@media(max-width: 900px) {
    .mb-pricing-grid { grid-template-columns: 1fr; }
    .mb-title { font-size: 42px; }
}
.mb-price-card {
    border-radius: 20px;
    padding: 18px;
    border: 1px solid rgba(168,85,247,.2);
    background: rgba(12,16,32,.75);
}
.mb-price-card h4 { color: #ffe7a3 !important; margin: 0 0 6px 0; }
.mb-faq-item {
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 8px;
    background: rgba(15,23,42,.55);
    border: 1px solid rgba(255,255,255,.06);
}
.mb-footer {
    margin-top: 32px;
    padding: 24px 0 8px 0;
    border-top: 1px solid rgba(255,255,255,.08);
    color: #64748b !important;
    font-size: 12px;
}
"""
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
        {APP_TAGLINE}<br>
        Willkommen zurück, <strong>{user}</strong> — ein OS für AI, Reels, Football Intelligence, Automation & Teams.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    hc1, hc2, hc3 = st.columns(3)
    with hc1:
        if st.button("Upgrade Premium", width="stretch", type="primary"):
            open_page("premium")
    with hc2:
        if st.button("Football AI", width="stretch"):
            open_page("football")
    with hc3:
        if st.button("Support", width="stretch"):
            open_page("support")

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

    st.markdown('<div class="mb-section-title">Pricing Preview</div>', unsafe_allow_html=True)
    cards = []
    for key in ("pro", "grand", "elite"):
        p = PLANS.get(key, {})
        cards.append(
            f'<div class="mb-price-card"><h4>{p.get("label", key)}</h4>'
            f'<p style="color:#94a3b8;font-size:13px;">{p.get("price", "")} · {p.get("tokens", 0)} Tokens</p></div>'
        )
    st.markdown(f'<div class="mb-pricing-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
    st.caption("Football Premium: Starter / Pro / Elite — separates Abo.")
    if st.button("Alle Pläne vergleichen", width="stretch"):
        open_page("premium")

    st.markdown('<div class="mb-section-title">Warum MaByte?</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        with st.container(border=True):
            st.markdown("**AI Operating System**")
            st.caption("Chat, Code, Bild, Video, Music, Reels — ein Account.")
    with f2:
        with st.container(border=True):
            st.markdown("**Football Intelligence**")
            st.caption("Match Center, AI Engine, Odds Lab (Elite).")
    with f3:
        with st.container(border=True):
            st.markdown("**Production Beta**")
            st.caption("Stripe, OAuth, Admin OS, Support-Tickets.")

    st.markdown('<div class="mb-section-title">FAQ</div>', unsafe_allow_html=True)
    faqs = [
        ("Was ist MaByte?", "Ein Premium-SaaS AI OS für Creator und Teams — nicht nur ein Chatbot."),
        ("Wie funktionieren Tokens?", "1€ ≈ 100 Tokens. Jeder Workspace verbraucht unterschiedlich viele Tokens."),
        ("Football Premium?", f"Separate Pläne: {', '.join(FOOTBALL_PLANS.keys())} — Features je Tier."),
        ("Ist Odds Lab Wettberatung?", "Nein — nur mathematische Analyse und Bildung."),
    ]
    for q, a in faqs:
        st.markdown(
            f'<div class="mb-faq-item"><strong style="color:#f8fafc;">{q}</strong><br><span style="color:#94a3b8;font-size:13px;">{a}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="mb-section-title">Stimmen aus der Beta</div>', unsafe_allow_html=True)
    t1, t2, t3 = st.columns(3)
    for col, quote, who in (
        (t1, "Endlich Reels und Video getrennt — fühlt sich wie ein echtes Studio an.", "Creator · DE"),
        (t2, "Football Match Center spart uns Stunden Recherche pro Spieltag.", "Football Editor"),
        (t3, "Admin Panel + Support machen den Launch beherrschbar.", "Operator"),
    ):
        with col:
            with st.container(border=True):
                st.markdown(f"*{quote}*")
                st.caption(who)

    st.markdown(
        """
<div class="mb-footer">
    MaByte · Mab AI · Production Beta<br>
    <span style="opacity:.8;">Impressum · Datenschutz · AGB über Legal Center</span>
</div>
        """,
        unsafe_allow_html=True,
    )
    lc1, lc2, lc3, lc4 = st.columns(4)
    for col, (label, page) in zip(
        (lc1, lc2, lc3, lc4),
        [("Impressum", "impressum"), ("Datenschutz", "privacy"), ("AGB", "terms"), ("Legal Center", "legal")],
    ):
        with col:
            if st.button(label, key=f"home_legal_{page}", width="stretch"):
                open_page(page)