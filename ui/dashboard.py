"""MaByte Home — bento workspace hub."""
from __future__ import annotations

import html
from datetime import datetime
from urllib.parse import quote

import streamlit as st

from config import APP_NAME, PLANS
from database import recent_activity
from ui.components import format_num
from ui.sidebar import navigate_to
from ui.styles import inject_css

_TOOLS: list[tuple[str, str, str, str]] = [
    ("chat", "AI Chat", "Assistenz & Ideen", "violet"),
    ("image", "Image", "Bilder erstellen", "blue"),
    ("video", "Video", "Shorts & Clips", "rose"),
    ("football", "Football", "Analysen", "emerald"),
    ("automation_lab", "Automation", "Content", "amber"),
    ("coding", "Code", "Entwickeln", "cyan"),
]

_ACCENT: dict[str, str] = {
    "violet": "#8b5cf6",
    "blue": "#60a5fa",
    "rose": "#f472b6",
    "emerald": "#34d399",
    "amber": "#fbbf24",
    "cyan": "#22d3ee",
}

_ICON = (
    'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
    'stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
)
_SVG: dict[str, str] = {
    "chat": f"<svg {_ICON.format(c='%23fafafa')}><path d=\"M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z\"/></svg>",
    "image": f"<svg {_ICON.format(c='%23fafafa')}><rect width=\"18\" height=\"18\" x=\"3\" y=\"3\" rx=\"2\"/><circle cx=\"9\" cy=\"9\" r=\"2\"/><path d=\"m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21\"/></svg>",
    "video": f"<svg {_ICON.format(c='%23fafafa')}><path d=\"m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5\"/><rect x=\"2\" y=\"6\" width=\"14\" height=\"12\" rx=\"2\"/></svg>",
    "football": f"<svg {_ICON.format(c='%23fafafa')}><circle cx=\"12\" cy=\"12\" r=\"10\"/><path d=\"M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20\"/><path d=\"M2 12h20\"/></svg>",
    "automation_lab": f"<svg {_ICON.format(c='%23fafafa')}><rect width=\"8\" height=\"8\" x=\"3\" y=\"3\" rx=\"2\"/><path d=\"M7 11v4a2 2 0 0 0 2 2h4\"/><rect width=\"8\" height=\"8\" x=\"13\" y=\"13\" rx=\"2\"/></svg>",
    "coding": f"<svg {_ICON.format(c='%23fafafa')}><polyline points=\"16 18 22 12 16 6\"/><polyline points=\"8 6 2 12 8 18\"/></svg>",
    "dashboard": f"<svg {_ICON.format(c='%23fafafa')}><path d=\"M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2\"/><circle cx=\"12\" cy=\"7\" r=\"4\"/></svg>",
    "premium": f"<svg {_ICON.format(c='%23fafafa')}><path d=\"M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.734H5.81a1 1 0 0 1-.957-.734L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z\"/></svg>",
}


def _icon_uri(page: str) -> str:
    return f'url("data:image/svg+xml,{quote(_SVG.get(page, _SVG["chat"]))}")'


def _btn_css() -> str:
    base = ".stApp:has(.mb-hub) [class*='st-key-hub_']"
    parts = [
        f"""
.stApp:has(.mb-hub) section.main .block-container {{
    max-width: 900px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding: 14px 1.25rem 36px !important;
}}
.stApp:has(.mb-hub) section.main [data-testid="stVerticalBlock"] {{ gap: 10px !important; }}
.stApp:has(.mb-hub) .st-key-hub_layout > [data-testid="stHorizontalBlock"] {{
    gap: 12px !important;
    align-items: start !important;
}}
{base} .stButton, {base} [data-testid="stVerticalBlockBorderWrapper"],
{base} [data-testid="stElementContainer"] {{
    margin: 0 !important; padding: 0 !important;
    background: transparent !important; border: none !important;
    box-shadow: none !important; width: 100% !important;
}}
.stApp:has(.mb-hub) .st-key-hub_grid [data-testid="column"] > [data-testid="stVerticalBlock"] {{
    gap: 8px !important;
}}
.stApp:has(.mb-hub) .st-key-hub_side > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {{
    gap: 8px !important;
}}
.stApp:has(.mb-hub) .st-key-hub_account {{
    padding: 12px; border-radius: 12px;
    background: rgba(18, 18, 20, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.06);
}}
.stApp:has(.mb-hub) .st-key-hub_account > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {{
    gap: 8px !important;
}}
"""
    ]
    tile = f"{base}[class*='st-key-hub_tile_']"
    parts.append(
        f"""
{tile} .stButton > button, {tile} button {{
    width: 100% !important; min-height: 86px !important;
    padding: 14px 10px 12px !important; border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    background: rgba(24,24,27,0.9) !important;
    display: flex !important; flex-direction: column !important;
    align-items: center !important; justify-content: flex-start !important;
    text-align: center !important; box-shadow: none !important;
    transition: transform .12s, border-color .15s, box-shadow .15s !important;
}}
{tile} .stButton > button:hover, {tile} button:hover {{
    transform: translateY(-1px) !important;
    border-color: rgba(139,92,246,0.35) !important;
    box-shadow: 0 6px 18px rgba(124,58,237,0.1) !important;
}}
{tile} .stButton > button::before, {tile} button::before {{
    content: "" !important; display: block !important;
    width: 24px !important; height: 24px !important;
    margin: 0 auto 8px !important; border-radius: 8px !important;
    background-color: rgba(124,58,237,0.15) !important;
    background-size: 16px !important; background-position: center !important;
    background-repeat: no-repeat !important; position: static !important;
}}
{tile} .stButton > button p, {tile} button p {{
    white-space: pre-line !important; text-align: center !important;
    font-size: 11px !important; line-height: 1.35 !important; color: #71717a !important;
}}
{tile} .stButton > button p::first-line, {tile} button p::first-line {{
    font-size: 14px !important; font-weight: 700 !important; color: #fafafa !important;
}}
"""
    )
    for page, _, _, accent in _TOOLS:
        color = _ACCENT.get(accent, "#8b5cf6")
        sel = f".stApp:has(.mb-hub) .st-key-hub_tile_{page}"
        parts.append(
            f"{sel} .stButton > button, {sel} button {{ border-top: 2px solid {color} !important; }}"
            f"{sel} .stButton > button::before, {sel} button::before {{"
            f"background-image: {_icon_uri(page)} !important;"
            f"background-color: {color}22 !important; }}"
        )
    for page in ("dashboard", "premium"):
        sel = f".stApp:has(.mb-hub) .st-key-hub_link_{page}"
        parts.append(
            f"{sel} .stButton > button, {sel} button {{"
            f"min-height: 36px !important; padding: 8px 12px !important;"
            f"border-radius: 10px !important; border: 1px solid rgba(255,255,255,0.07) !important;"
            f"background: rgba(255,255,255,0.03) !important; text-align: left !important;"
            f"justify-content: flex-start !important; }}"
            f"{sel} .stButton > button::before, {sel} button::before {{"
            f"content: '' !important; display: inline-block !important; width: 16px !important;"
            f"height: 16px !important; margin: 0 8px 0 0 !important; border-radius: 0 !important;"
            f"background-color: transparent !important; background-image: {_icon_uri(page)} !important;"
            f"background-size: 16px !important; vertical-align: middle !important; }}"
            f"{sel} .stButton > button p, {sel} button p {{"
            f"font-size: 13px !important; color: #e4e4e7 !important; white-space: nowrap !important; }}"
        )
    return "".join(parts)


_HUB_CSS = """
.mb-hub-hero {
    position: relative; overflow: hidden; border-radius: 14px;
    padding: 20px 20px 18px; margin-bottom: 2px;
    border: 1px solid rgba(139, 92, 246, 0.16);
    background: linear-gradient(145deg, rgba(30, 20, 50, 0.95), rgba(15, 15, 18, 0.98));
    text-align: center;
}
.mb-hub-glow {
    position: absolute; top: -40%; right: -10%; width: 55%; height: 140%;
    background: radial-gradient(ellipse, rgba(124, 58, 237, 0.28), transparent 70%);
    pointer-events: none;
}
.mb-hub-hero-inner { position: relative; z-index: 1; }
.mb-hub-kicker {
    font-size: 10px; font-weight: 800; letter-spacing: 0.16em;
    text-transform: uppercase; color: #a78bfa !important; margin: 0 0 8px;
}
.mb-hub-hero h1 {
    margin: 0; font-size: clamp(24px, 3vw, 32px); font-weight: 800;
    color: #fafafa !important; letter-spacing: -0.03em; line-height: 1.15;
}
.mb-hub-metrics {
    display: flex; gap: 24px; margin-top: 14px; flex-wrap: wrap;
    justify-content: center; align-items: center;
}
.mb-hub-metrics .item { display: flex; flex-direction: column; gap: 2px; align-items: center; }
.mb-hub-metrics .n {
    font-size: 18px; font-weight: 800; color: #fafafa !important; line-height: 1;
}
.mb-hub-metrics .l {
    font-size: 10px; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #71717a !important;
}
.mb-hub-label {
    font-size: 9px; font-weight: 800; letter-spacing: 0.12em;
    text-transform: uppercase; color: #52525b !important;
    margin: 0 0 6px; text-align: center;
}
.mb-hub-card {
    padding: 12px; border-radius: 12px;
    background: rgba(18, 18, 20, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.06);
}
.mb-hub-card .lbl,
.stApp:has(.mb-hub) .st-key-hub_account .lbl {
    font-size: 10px; font-weight: 800; letter-spacing: 0.12em;
    text-transform: uppercase; color: #52525b !important;     margin-bottom: 8px;
}
.mb-hub-act {
    display: flex; justify-content: space-between; align-items: center; gap: 8px;
    padding: 6px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    font-size: 12px;
}
.mb-hub-act:last-child { border-bottom: none; padding-bottom: 0; }
.mb-hub-act .t { color: #e4e4e7 !important; font-weight: 600; }
.mb-hub-act .d { color: #52525b !important; font-size: 11px; }
.mb-hub-empty { color: #52525b !important; font-size: 13px; margin: 0; line-height: 1.5; }
""" + _btn_css()


def _greeting(user: str) -> str:
    hour = datetime.now().hour
    salut = "Guten Morgen" if hour < 12 else "Guten Tag" if hour < 18 else "Guten Abend"
    return f"{salut}, {html.escape(user)}"


def _hero_html(*, user: str, tokens: str, plan_label: str, tier: str) -> str:
    return f"""
<div class="mb-hub-hero">
  <div class="mb-hub-glow"></div>
  <div class="mb-hub-hero-inner">
    <p class="mb-hub-kicker">{html.escape(APP_NAME)}</p>
    <h1>{_greeting(user)}</h1>
    <div class="mb-hub-metrics">
      <div class="item"><span class="n">{html.escape(tokens)}</span><span class="l">Tokens</span></div>
      <div class="item"><span class="n">{html.escape(plan_label)}</span><span class="l">Plan</span></div>
      <div class="item"><span class="n">{html.escape(tier)}</span><span class="l">Stufe</span></div>
    </div>
  </div>
</div>
"""


def _activity_card(username: str, *, limit: int = 4) -> str:
    items = recent_activity(username=username, limit=limit) or []
    if not items:
        body = '<p class="mb-hub-empty">Noch keine Aktivität.</p>'
    else:
        body = "".join(
            f'<div class="mb-hub-act"><span class="t">'
            f'{html.escape(str(r.get("tool", "system")).replace("_", " ").title())}</span>'
            f'<span class="d">{html.escape(str(r.get("created_at", ""))[:16].replace("T", " · "))}</span></div>'
            for r in items
        )
    return f'<div class="mb-hub-card"><div class="lbl">Aktivität</div>{body}</div>'


def _tile_label(title: str, desc: str) -> str:
    return f"{title}\n{desc}"


def _render_tool_grid() -> None:
    st.markdown('<p class="mb-hub-label">Tools</p>', unsafe_allow_html=True)
    with st.container(key="hub_grid"):
        for row_start in range(0, len(_TOOLS), 3):
            cols = st.columns(3, gap="small")
            for col, item in zip(cols, _TOOLS[row_start : row_start + 3]):
                page, title, desc, _ = item
                with col:
                    with st.container(key=f"hub_tile_{page}"):
                        if st.button(
                            _tile_label(title, desc),
                            key=f"hub_btn_{page}",
                            use_container_width=True,
                            type="tertiary",
                        ):
                            navigate_to(page)


def _render_side_panel(username: str) -> None:
    with st.container(key="hub_side"):
        st.markdown(_activity_card(username), unsafe_allow_html=True)
        with st.container(key="hub_account"):
            st.markdown('<div class="lbl">Account</div>', unsafe_allow_html=True)
            with st.container(key="hub_link_dashboard"):
                if st.button("Profil & Limits", key="hub_btn_profile", use_container_width=True, type="tertiary"):
                    navigate_to("dashboard")
            with st.container(key="hub_link_premium"):
                if st.button("Premium upgraden", key="hub_btn_premium", use_container_width=True, type="tertiary"):
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

    inject_css(_HUB_CSS)
    st.markdown('<div class="mb-hub" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown(
        _hero_html(user=user, tokens=format_num(tokens), plan_label=plan_label, tier=tier),
        unsafe_allow_html=True,
    )

    with st.container(key="hub_layout"):
        col_tools, col_side = st.columns([1.45, 1], gap="small")
        with col_tools:
            _render_tool_grid()
        with col_side:
            _render_side_panel(user)
