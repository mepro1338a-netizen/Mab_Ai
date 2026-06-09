"""MaByte Home — OS-style command center."""
from __future__ import annotations

import html
from datetime import datetime
from urllib.parse import quote

import streamlit as st

from config import APP_TAGLINE, PLANS
from database import recent_activity
from ui.components import format_num
from ui.sidebar import navigate_to
from ui.styles import inject_css

_TOOLS: list[tuple[str, str, str]] = [
    ("chat", "AI Chat", "Fragen, Ideen & Assistenz"),
    ("image", "Image", "Bilder generieren"),
    ("video", "Video", "Shorts & Clips"),
    ("football", "Football", "Analysen & Tipps"),
    ("automation_lab", "Automation", "Content planen"),
    ("coding", "Code", "Entwickeln & fixen"),
]

_ICON = (
    'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
    'stroke="%23a78bfa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
)
_SVG: dict[str, str] = {
    "chat": f"<svg {_ICON}><path d=\"M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z\"/></svg>",
    "football": f"<svg {_ICON}><circle cx=\"12\" cy=\"12\" r=\"10\"/><path d=\"M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20\"/><path d=\"M2 12h20\"/></svg>",
    "image": f"<svg {_ICON}><rect width=\"18\" height=\"18\" x=\"3\" y=\"3\" rx=\"2\"/><circle cx=\"9\" cy=\"9\" r=\"2\"/><path d=\"m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21\"/></svg>",
    "video": f"<svg {_ICON}><path d=\"m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5\"/><rect x=\"2\" y=\"6\" width=\"14\" height=\"12\" rx=\"2\"/></svg>",
    "automation_lab": f"<svg {_ICON}><rect width=\"8\" height=\"8\" x=\"3\" y=\"3\" rx=\"2\"/><path d=\"M7 11v4a2 2 0 0 0 2 2h4\"/><rect width=\"8\" height=\"8\" x=\"13\" y=\"13\" rx=\"2\"/></svg>",
    "coding": f"<svg {_ICON}><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
    "dashboard": f"<svg {_ICON}><path d=\"M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2\"/><circle cx=\"12\" cy=\"7\" r=\"4\"/></svg>",
    "premium": f"<svg {_ICON}><path d=\"M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.734H5.81a1 1 0 0 1-.957-.734L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z\"/></svg>",
}


def _icon_uri(page: str) -> str:
    svg = _SVG.get(page, _SVG["chat"])
    return f'url("data:image/svg+xml,{quote(svg)}")'


def _tool_btn_css() -> str:
    rules: list[str] = []
    base = ".stApp:has(.mb-os) [class*='st-key-os_nav_']"
    reset = f"""
{base} .stButton, {base} [data-testid="stVerticalBlockBorderWrapper"],
{base} [data-testid="stElementContainer"] {{
    margin: 0 !important; padding: 0 !important;
    background: transparent !important; border: none !important;
    box-shadow: none !important; width: 100% !important;
}}
{base} .stButton > button, {base} button {{
    width: 100% !important; margin: 0 !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    background: rgba(24, 24, 27, 0.85) !important;
    color: #a1a1aa !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: flex-start !important;
    box-shadow: none !important;
    white-space: pre-line !important;
    line-height: 1.4 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    position: relative !important;
    transition: border-color 0.15s, background 0.15s, transform 0.12s !important;
}}
{base} .stButton > button:hover, {base} button:hover {{
    border-color: rgba(139, 92, 246, 0.45) !important;
    background: rgba(30, 27, 40, 0.95) !important;
    transform: translateY(-1px) !important;
}}
{base} .stButton > button p, {base} button p {{
    white-space: pre-line !important; text-align: left !important;
    font-size: 12px !important; line-height: 1.4 !important; color: #71717a !important;
}}
{base} .stButton > button p::first-line, {base} button p::first-line {{
    font-size: 15px !important; font-weight: 700 !important; color: #fafafa !important;
}}
{base} .stButton > button::before, {base} button::before {{
    content: "" !important; position: absolute !important;
    left: 16px !important; top: 16px !important;
    width: 18px !important; height: 18px !important;
    background-size: 18px !important; background-repeat: no-repeat !important;
}}
"""
    rules.append(reset)
    for page in _SVG:
        sel = f".stApp:has(.mb-os) .st-key-os_nav_{page} .stButton > button, .stApp:has(.mb-os) .st-key-os_nav_{page} button"
        uri = _icon_uri(page)
        rules.append(
            f"{sel} {{ padding: 16px 16px 16px 48px !important; min-height: 76px !important; }}"
            f"{sel}::before {{ background-image: {uri} !important; }}"
        )
    feat = ".stApp:has(.mb-os) .st-key-os_feat .stButton > button, .stApp:has(.mb-os) .st-key-os_feat button"
    rules.append(
        f"{feat} {{"
        f"min-height: 88px !important; padding: 20px 24px 20px 56px !important;"
        f"background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(24,24,27,0.92)) !important;"
        f"border-color: rgba(139,92,246,0.35) !important;"
        f"}}"
        f"{feat}::before {{ width: 22px !important; height: 22px !important;"
        f"background-size: 22px !important; left: 20px !important; top: 22px !important; }}"
        f"{feat} .stButton > button p::first-line, {feat} button p::first-line {{"
        f"font-size: 18px !important; }}"
    )
    acc = ".stApp:has(.mb-os) .st-key-os_acc .stButton > button, .stApp:has(.mb-os) .st-key-os_acc button"
    rules.append(
        f"{acc} {{ min-height: 42px !important; padding: 10px 14px !important;"
        f"text-align: center !important; justify-content: center !important; }}"
        f"{acc}::before {{ display: none !important; }}"
        f"{acc} .stButton > button p, {acc} button p {{ text-align: center !important;"
        f"white-space: nowrap !important; font-size: 13px !important; color: #e4e4e7 !important; }}"
        f"{acc} .stButton > button p::first-line, {acc} button p::first-line {{"
        f"font-size: 13px !important; font-weight: 600 !important; }}"
    )
    return "".join(rules)


_OS_CSS = """
.stApp:has(.mb-os) section.main .block-container {
    max-width: var(--mb-content-max, 960px) !important;
    padding: 24px var(--mb-content-pad-x, 1.5rem) 56px !important;
}
.stApp:has(.mb-os) section.main [data-testid="stVerticalBlock"] {
    gap: 14px !important;
}
.mb-os-wrap { display: flex; flex-direction: column; gap: 20px; }
.mb-os-bar {
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
    flex-wrap: wrap; padding: 10px 14px; border-radius: 12px;
    background: rgba(24, 24, 27, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.06);
}
.mb-os-brand {
    font-size: 10px; font-weight: 800; letter-spacing: 0.18em;
    text-transform: uppercase; color: #a78bfa !important;
}
.mb-os-pills { display: flex; gap: 8px; flex-wrap: wrap; }
.mb-os-pill {
    font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #d4d4d8 !important; background: rgba(255, 255, 255, 0.03);
}
.mb-os-pill.accent {
    border-color: rgba(139, 92, 246, 0.35);
    background: rgba(124, 58, 237, 0.12);
    color: #e9d5ff !important;
}
.mb-os-hero { margin: 4px 0 2px; }
.mb-os-hero h1 {
    margin: 0; font-size: clamp(26px, 3.2vw, 34px); font-weight: 800;
    color: #fafafa !important; letter-spacing: -0.035em; line-height: 1.1;
}
.mb-os-hero p {
    margin: 8px 0 0; font-size: 14px; color: #71717a !important; line-height: 1.5;
    max-width: 480px;
}
.mb-os-section {
    font-size: 10px; font-weight: 800; letter-spacing: 0.14em;
    text-transform: uppercase; color: #52525b !important;
    margin: 6px 0 0;
}
.stApp:has(.mb-os) .st-key-os_grid [data-testid="column"] > [data-testid="stVerticalBlock"] {
    gap: 10px !important;
}
.mb-os-feed {
    padding: 14px 16px; border-radius: 14px;
    background: rgba(18, 18, 20, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.05);
}
.mb-os-feed .lbl {
    font-size: 10px; font-weight: 800; letter-spacing: 0.12em;
    text-transform: uppercase; color: #52525b !important; margin-bottom: 10px;
}
.mb-os-timeline { list-style: none; margin: 0; padding: 0; }
.mb-os-timeline li {
    display: flex; align-items: baseline; gap: 10px;
    padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    font-size: 13px;
}
.mb-os-timeline li:last-child { border-bottom: none; padding-bottom: 0; }
.mb-os-timeline .dot {
    width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0;
    background: #7c3aed; margin-top: 5px;
}
.mb-os-timeline .t { color: #e4e4e7 !important; font-weight: 600; flex: 1; }
.mb-os-timeline .d { color: #52525b !important; font-size: 11px; white-space: nowrap; }
.mb-os-empty { color: #52525b !important; font-size: 13px; margin: 0; line-height: 1.5; }
.stApp:has(.mb-os) .st-key-os_acc_row > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {
    gap: 10px !important;
}
""" + _tool_btn_css()


def _nav_key(page: str) -> str:
    return f"os_nav_{page}"


def _tile_label(title: str, desc: str) -> str:
    return f"{title}\n{desc}"


def _greeting(user: str) -> str:
    hour = datetime.now().hour
    if hour < 12:
        salut = "Guten Morgen"
    elif hour < 18:
        salut = "Guten Tag"
    else:
        salut = "Guten Abend"
    return f"{salut}, {html.escape(user)}"


def _activity_html(username: str, *, limit: int = 5) -> str:
    items = recent_activity(username=username, limit=limit) or []
    if not items:
        return (
            '<div class="mb-os-feed">'
            '<div class="lbl">Letzte Aktivität</div>'
            '<p class="mb-os-empty">Noch keine Aktivität — starte mit AI Chat.</p>'
            "</div>"
        )
    rows = "".join(
        "<li>"
        '<span class="dot"></span>'
        f'<span class="t">{html.escape(str(r.get("tool", "system")).replace("_", " ").title())}</span>'
        f'<span class="d">{html.escape(str(r.get("created_at", ""))[:16].replace("T", " · "))}</span>'
        "</li>"
        for r in items
    )
    return (
        '<div class="mb-os-feed">'
        '<div class="lbl">Letzte Aktivität</div>'
        f'<ul class="mb-os-timeline">{rows}</ul>'
        "</div>"
    )


def _status_bar_html(*, plan_label: str, tokens: str, tier: str) -> str:
    return (
        '<div class="mb-os-bar">'
        '<span class="mb-os-brand">MaByte OS</span>'
        '<div class="mb-os-pills">'
        f'<span class="mb-os-pill accent">{html.escape(plan_label)}</span>'
        f'<span class="mb-os-pill">{html.escape(tokens)} Tokens</span>'
        f'<span class="mb-os-pill">{html.escape(tier)}</span>'
        "</div></div>"
    )


def _render_featured_chat() -> None:
    with st.container(key="os_feat"):
        if st.button(
            _tile_label("AI Chat", "Dein Einstieg — Fragen, Brainstorming, Assistenz"),
            key=_nav_key("chat"),
            use_container_width=True,
            type="tertiary",
        ):
            navigate_to("chat")


def _render_tool_grid() -> None:
    rest = [t for t in _TOOLS if t[0] != "chat"]
    with st.container(key="os_grid"):
        for row_start in range(0, len(rest), 3):
            cols = st.columns(3, gap="small")
            for col, item in zip(cols, rest[row_start : row_start + 3]):
                page, title, desc = item
                with col:
                    if st.button(
                        _tile_label(title, desc),
                        key=_nav_key(page),
                        use_container_width=True,
                        type="tertiary",
                    ):
                        navigate_to(page)


def _render_account_row() -> None:
    with st.container(key="os_acc_row"):
        c1, c2 = st.columns(2, gap="small")
        with c1:
            with st.container(key="os_acc"):
                if st.button("Profil & Limits", key=_nav_key("dashboard"), use_container_width=True, type="tertiary"):
                    navigate_to("dashboard")
        with c2:
            with st.container(key="os_acc"):
                if st.button("Premium upgraden", key=_nav_key("premium"), use_container_width=True, type="tertiary"):
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
    tier = str(plan.get("badge", "Starter"))
    tokens = int(st.session_state.get("tokens", 0) or 0)

    inject_css(_OS_CSS)

    st.markdown('<div class="mb-os" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown(
        _status_bar_html(
            plan_label=plan_label,
            tokens=format_num(tokens),
            tier=tier,
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<div class="mb-os-hero">
  <h1>{_greeting(user)}</h1>
  <p>{html.escape(APP_TAGLINE)}</p>
</div>
<div class="mb-os-section">Workspace</div>
        """,
        unsafe_allow_html=True,
    )

    _render_featured_chat()
    _render_tool_grid()
    st.markdown(_activity_html(user), unsafe_allow_html=True)
    _render_account_row()
