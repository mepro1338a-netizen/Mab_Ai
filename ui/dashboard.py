"""MaByte Home — clean standard dashboard."""
from __future__ import annotations

import base64
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

_SVG_PATHS: dict[str, str] = {
    "chat": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "image": '<rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
    "video": '<path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5"/><rect x="2" y="6" width="14" height="12" rx="2"/>',
    "football": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "automation_lab": '<rect width="8" height="8" x="3" y="3" rx="2"/><path d="M7 11v4a2 2 0 0 0 2 2h4"/><rect width="8" height="8" x="13" y="13" rx="2"/>',
    "coding": '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
    "dashboard": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "premium": '<path d="M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.734H5.81a1 1 0 0 1-.957-.734L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z"/>',
}


def _icon_html(page: str) -> str:
    inner = _SVG_PATHS.get(page, _SVG_PATHS["chat"])
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="#a78bfa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f"{inner}</svg>"
    )
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f'<img src="data:image/svg+xml;base64,{b64}" width="18" height="18" alt="" class="home-ico" />'


def _tool_btn_css() -> str:
    base = ".stApp:has(.mb-home) [class*='st-key-home_tile_']"
    rules = [
        f"""
.stApp:has(.mb-home) section.main .block-container {{
    max-width: 820px !important;
    margin: 0 auto !important;
    padding: 20px 1.25rem 40px !important;
}}
.stApp:has(.mb-home) section.main [data-testid="stVerticalBlock"] {{ gap: 12px !important; }}
.stApp:has(.mb-home) .st-key-home_grid [data-testid="column"] > [data-testid="stVerticalBlock"] {{
    gap: 8px !important;
}}
{base} .stButton, {base} [data-testid="stVerticalBlockBorderWrapper"],
{base} [data-testid="stElementContainer"] {{
    margin: 0 !important; padding: 0 !important;
    background: transparent !important; border: none !important; box-shadow: none !important;
}}
.stApp:has(.mb-home) [class*="st-key-home_tile_"] > [data-testid="stHorizontalBlock"] {{
    align-items: center !important;
}}
.stApp:has(.mb-home) [class*="st-key-home_tile_"] [data-testid="column"]:first-child {{
    flex: 0 0 36px !important; min-width: 36px !important; max-width: 36px !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
}}
.home-ico-wrap {{ display:flex; align-items:center; justify-content:center; width:36px; }}
.home-ico {{ display:block; width:18px; height:18px; }}
{base} .stButton > button, {base} button {{
    width: 100% !important; min-height: 48px !important;
    padding: 8px 12px !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    background: rgba(24,24,27,0.85) !important;
    color: #71717a !important;
    display: flex !important; align-items: center !important;
    justify-content: flex-start !important; text-align: left !important;
    box-shadow: none !important;
    white-space: pre-line !important; line-height: 1.3 !important;
    font-size: 11px !important;
}}
{base} .stButton > button:hover, {base} button:hover {{
    border-color: rgba(139,92,246,0.35) !important;
    background: rgba(30,30,35,0.95) !important;
}}
{base} .stButton > button p, {base} button p {{
    white-space: pre-line !important; text-align: left !important;
    font-size: 11px !important; line-height: 1.3 !important; color: #71717a !important;
    margin: 0 !important; display: flex !important; align-items: center !important;
}}
{base} .stButton > button p::first-line, {base} button p::first-line {{
    font-size: 14px !important; font-weight: 600 !important; color: #fafafa !important;
}}
.stApp:has(.mb-home) [class*="st-key-home_link_"] > [data-testid="stHorizontalBlock"] {{
    align-items: center !important;
}}
.stApp:has(.mb-home) [class*="st-key-home_link_"] [data-testid="column"]:first-child {{
    flex: 0 0 32px !important; min-width: 32px !important; max-width: 32px !important;
}}
"""
    ]
    for page in ("dashboard", "premium"):
        sel = f".stApp:has(.mb-home) .st-key-home_link_{page}"
        rules.append(
            f"{sel} .stButton > button, {sel} button {{"
            f"min-height: 36px !important; font-size: 13px !important; }}"
            f"{sel} .stButton > button p, {sel} button p {{"
            f"font-size: 13px !important; color: #e4e4e7 !important; white-space: nowrap !important; }}"
        )
    return "".join(rules)


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
            for col, item in zip(cols, _TOOLS[row_start : row_start + 2]):
                page, title, desc = item
                with col:
                    with st.container(key=f"home_tile_{page}"):
                        ic, bt = st.columns([0.14, 0.86], gap="small")
                        with ic:
                            st.markdown(
                                f'<div class="home-ico-wrap">{_icon_html(page)}</div>',
                                unsafe_allow_html=True,
                            )
                        with bt:
                            if st.button(
                                _tile_label(title, desc),
                                key=f"home_btn_{page}",
                                use_container_width=True,
                                type="tertiary",
                            ):
                                navigate_to(page)


def _render_quick_links() -> None:
    with st.container(key="home_links"):
        c1, c2 = st.columns(2, gap="small")
        with c1:
            with st.container(key="home_link_dashboard"):
                ic, bt = st.columns([0.14, 0.86], gap="small")
                with ic:
                    st.markdown(f'<div class="home-ico-wrap">{_icon_html("dashboard")}</div>', unsafe_allow_html=True)
                with bt:
                    if st.button("Profil & Limits", key="home_btn_profile", use_container_width=True, type="tertiary"):
                        navigate_to("dashboard")
        with c2:
            with st.container(key="home_link_premium"):
                ic, bt = st.columns([0.14, 0.86], gap="small")
                with ic:
                    st.markdown(f'<div class="home-ico-wrap">{_icon_html("premium")}</div>', unsafe_allow_html=True)
                with bt:
                    if st.button("Premium", key="home_btn_premium", use_container_width=True, type="tertiary"):
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
