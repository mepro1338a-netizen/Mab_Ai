"""MaByte Home — clean standard dashboard."""
from __future__ import annotations

import html
from datetime import datetime

import streamlit as st

from config import PLANS
from database import recent_activity
from ui.components import format_num
from ui.sidebar import navigate_to
from ui.styles import inject_css

_TOOLS: list[tuple[str, str, str]] = [
    ("chat", "AI Chat", "Fragen & Assistenz"),
    ("image", "Image", "Bilder erstellen"),
    ("video", "Video", "Shorts & Clips"),
    ("football", "Football", "Analysen & Tipps"),
    ("automation_lab", "Automation", "Content planen"),
    ("coding", "Code", "Entwickeln & fixen"),
]

# Same Material icon set as the sidebar (ui/sidebar.py _NAV_ICONS).
_TILE_ICONS: dict[str, str] = {
    "chat": ":material/chat_bubble:",
    "image": ":material/image:",
    "video": ":material/movie:",
    "football": ":material/sports_soccer:",
    "automation_lab": ":material/account_tree:",
    "coding": ":material/code:",
    "dashboard": ":material/person:",
    "premium": ":material/workspace_premium:",
}


def _tool_btn_css() -> str:
    tile = ".stApp:has(.mb-home) section.main [class*='st-key-home_tile_']"
    link = ".stApp:has(.mb-home) section.main [class*='st-key-home_link_']"
    return f"""
.stApp:has(.mb-home) section.main .block-container {{
    max-width: 820px !important;
    margin: 0 auto !important;
    padding: 20px 1.25rem 40px !important;
}}
.stApp:has(.mb-home) section.main [data-testid="stVerticalBlock"] {{ gap: 12px !important; }}
.stApp:has(.mb-home) .st-key-home_grid [data-testid="column"] > [data-testid="stVerticalBlock"] {{
    gap: 8px !important;
}}
.stApp:has(.mb-home) section.main [data-testid="stVerticalBlockBorderWrapper"] {{
    background: transparent !important; border: none !important; box-shadow: none !important;
}}
{tile}, {link} {{
    margin: 0 !important; padding: 0 !important; width: 100% !important;
    background: transparent !important; border: none !important; box-shadow: none !important;
}}
{tile} .stButton, {link} .stButton {{
    margin: 0 !important; padding: 0 !important; width: 100% !important;
    background: transparent !important; border: none !important; box-shadow: none !important;
}}
{tile} .stButton > button, {tile} button {{
    width: 100% !important; min-height: 56px !important;
    padding: 10px 14px !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    background: rgba(24,24,27,0.85) !important;
    display: flex !important; align-items: center !important;
    justify-content: flex-start !important; gap: 12px !important;
    text-align: left !important; box-shadow: none !important;
}}
{tile} .stButton > button:hover, {tile} button:hover {{
    border-color: rgba(139,92,246,0.35) !important;
    background: rgba(30,30,35,0.95) !important;
}}
{tile} [data-testid="stIconMaterial"] {{
    font-size: 18px !important; color: #a78bfa !important;
    line-height: 1 !important; flex-shrink: 0 !important;
}}
{tile} .stButton > button p, {tile} button p {{
    white-space: pre-line !important; text-align: left !important;
    font-size: 11px !important; line-height: 1.35 !important; color: #71717a !important;
    margin: 0 !important;
}}
{tile} .stButton > button p::first-line, {tile} button p::first-line {{
    font-size: 14px !important; font-weight: 600 !important; color: #fafafa !important;
}}
{link} .stButton > button, {link} button {{
    width: 100% !important; min-height: 36px !important;
    padding: 6px 12px !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    background: rgba(24,24,27,0.85) !important;
    display: flex !important; align-items: center !important;
    justify-content: flex-start !important; gap: 10px !important;
    text-align: left !important; box-shadow: none !important;
}}
{link} .stButton > button:hover, {link} button:hover {{
    border-color: rgba(139,92,246,0.35) !important;
    background: rgba(30,30,35,0.95) !important;
}}
{link} [data-testid="stIconMaterial"] {{
    font-size: 16px !important; color: #a78bfa !important;
    line-height: 1 !important; flex-shrink: 0 !important;
}}
{link} .stButton > button p, {link} button p {{
    font-size: 13px !important; color: #e4e4e7 !important;
    white-space: nowrap !important; margin: 0 !important;
}}
"""


_HOME_CSS = """
.mb-home-head {
    display: flex; align-items: flex-end; justify-content: space-between;
    gap: 16px; flex-wrap: wrap; margin-bottom: 4px;
}
.mb-home-head h1 {
    margin: 0; font-size: 26px; font-weight: 700; color: #fafafa !important;
    letter-spacing: -0.02em; line-height: 1.2;
}
.mb-home-head p { margin: 4px 0 0; font-size: 13px; color: #71717a !important; }
.mb-home-stats { display: flex; gap: 8px; flex-wrap: wrap; }
.mb-home-stat {
    padding: 8px 12px; border-radius: 8px;
    background: rgba(39,39,42,0.8); border: 1px solid rgba(255,255,255,0.08);
    font-size: 12px; color: #e4e4e7 !important; white-space: nowrap;
}
.mb-home-stat b { color: #fafafa !important; font-weight: 700; }
.mb-home-sec {
    font-size: 11px; font-weight: 600; letter-spacing: 0.06em;
    text-transform: uppercase; color: #71717a !important; margin: 8px 0 4px;
}
.mb-home-panel {
    padding: 12px 14px; border-radius: 10px;
    background: rgba(24,24,27,0.6); border: 1px solid rgba(255,255,255,0.07);
}
.mb-home-row {
    display: flex; justify-content: space-between; align-items: center; gap: 10px;
    padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 13px;
}
.mb-home-row:last-child { border-bottom: none; }
.mb-home-row .t { color: #e4e4e7 !important; font-weight: 500; }
.mb-home-row .d { color: #52525b !important; font-size: 11px; }
.mb-home-empty { color: #52525b !important; font-size: 13px; margin: 0; }
.stApp:has(.mb-home) .st-key-home_links > [data-testid="stHorizontalBlock"] { gap: 8px !important; }
""" + _tool_btn_css()


def _greeting(user: str) -> str:
    hour = datetime.now().hour
    salut = "Guten Morgen" if hour < 12 else "Guten Tag" if hour < 18 else "Guten Abend"
    return f"{salut}, {html.escape(user)}"


def _head_html(*, user: str, tokens: str, plan_label: str) -> str:
    return f"""
<div class="mb-home-head">
  <div>
    <h1>{_greeting(user)}</h1>
    <p>Wähle ein Tool und starte deinen Workflow.</p>
  </div>
  <div class="mb-home-stats">
    <span class="mb-home-stat"><b>{html.escape(tokens)}</b> Tokens</span>
    <span class="mb-home-stat">Plan <b>{html.escape(plan_label)}</b></span>
  </div>
</div>
"""


def _activity_html(username: str, *, limit: int = 5) -> str:
    items = recent_activity(username=username, limit=limit) or []
    if not items:
        body = '<p class="mb-home-empty">Noch keine Aktivität.</p>'
    else:
        body = "".join(
            f'<div class="mb-home-row"><span class="t">'
            f'{html.escape(str(r.get("tool", "system")).replace("_", " ").title())}</span>'
            f'<span class="d">{html.escape(str(r.get("created_at", ""))[:16].replace("T", " · "))}</span></div>'
            for r in items
        )
    return f'<div class="mb-home-panel"><div class="mb-home-sec">Letzte Aktivität</div>{body}</div>'


def _tile_label(title: str, desc: str) -> str:
    return f"{title}\n{desc}"


def _render_tools() -> None:
    st.markdown('<div class="mb-home-sec">Tools</div>', unsafe_allow_html=True)
    with st.container(key="home_grid"):
        for row_start in range(0, len(_TOOLS), 2):
            cols = st.columns(2, gap="small")
            for col, (page, title, desc) in zip(cols, _TOOLS[row_start : row_start + 2]):
                with col:
                    if st.button(
                        _tile_label(title, desc),
                        key=f"home_tile_{page}",
                        icon=_TILE_ICONS.get(page),
                        use_container_width=True,
                        type="tertiary",
                    ):
                        navigate_to(page)


def _render_quick_links() -> None:
    with st.container(key="home_links"):
        c1, c2 = st.columns(2, gap="small")
        with c1:
            if st.button(
                "Profil & Limits",
                key="home_link_dashboard",
                icon=_TILE_ICONS["dashboard"],
                use_container_width=True,
                type="tertiary",
            ):
                navigate_to("dashboard")
        with c2:
            if st.button(
                "Premium",
                key="home_link_premium",
                icon=_TILE_ICONS["premium"],
                use_container_width=True,
                type="tertiary",
            ):
                navigate_to("premium")


def render_home() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    user = str(st.session_state.get("user") or "User")
    plan_key = str(st.session_state.get("plan") or "free")
    plan = PLANS.get(plan_key, PLANS["free"])
    plan_label = str(plan.get("label", plan_key))
    tokens = int(st.session_state.get("tokens", 0) or 0)

    inject_css(_HOME_CSS)
    st.markdown('<div class="mb-home" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown(
        _head_html(user=user, tokens=format_num(tokens), plan_label=plan_label),
        unsafe_allow_html=True,
    )
    _render_tools()
    st.markdown(_activity_html(user), unsafe_allow_html=True)
    _render_quick_links()
