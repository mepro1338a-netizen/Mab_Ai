"""
MaByte Sidebar — grouped SaaS navigation (Streamlit buttons, session-safe).
"""
from __future__ import annotations

import html
from urllib.parse import quote

import streamlit as st

from config import APP_NAME
from ui.styles import inject_css

_SB = 'section[data-testid="stSidebar"]'
_WIDTH = "230px"

NAV_SECTIONS: list[tuple[str, list[tuple[str, str]]]] = [
    ("Workspace", [("Dashboard", "home"), ("AI Chat", "chat")]),
    ("Football", [("Football AI", "football")]),
    (
        "Creator Studio",
        [
            ("Image", "image"),
            ("Video", "video"),
            ("Music", "music"),
            ("Code", "coding"),
        ],
    ),
    ("Content Automation", [("Content Automation", "automation_lab")]),
    ("Account", [("Profile", "dashboard"), ("Elite", "premium")]),
]

NAV_ITEMS: list[tuple[str, str]] = [
    item for _title, items in NAV_SECTIONS for item in items
]

LEGACY_PAGE_ALIASES: dict[str, str] = {
    "reels": "video",
    "creator": "video",
    "automations": "automation_lab",
    "projects": "home",
}

SIDEBAR_NAV_ITEMS = NAV_ITEMS

_LUCIDE = (
    'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
    'stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
)
_ICONS: dict[str, str] = {
    "home": f"<svg {_LUCIDE}><rect width=\"7\" height=\"9\" x=\"3\" y=\"3\" rx=\"1\"/><rect width=\"7\" height=\"5\" x=\"14\" y=\"3\" rx=\"1\"/><rect width=\"7\" height=\"9\" x=\"14\" y=\"12\" rx=\"1\"/><rect width=\"7\" height=\"5\" x=\"3\" y=\"16\" rx=\"1\"/></svg>",
    "chat": f"<svg {_LUCIDE}><path d=\"M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z\"/></svg>",
    "football": f"<svg {_LUCIDE}><circle cx=\"12\" cy=\"12\" r=\"10\"/><path d=\"M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20\"/><path d=\"M2 12h20\"/></svg>",
    "image": f"<svg {_LUCIDE}><rect width=\"18\" height=\"18\" x=\"3\" y=\"3\" rx=\"2\" ry=\"2\"/><circle cx=\"9\" cy=\"9\" r=\"2\"/><path d=\"m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21\"/></svg>",
    "video": f"<svg {_LUCIDE}><path d=\"m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5\"/><rect x=\"2\" y=\"6\" width=\"14\" height=\"12\" rx=\"2\"/></svg>",
    "music": f"<svg {_LUCIDE}><path d=\"M9 18V5l12-2v13\"/><circle cx=\"6\" cy=\"18\" r=\"3\"/><circle cx=\"18\" cy=\"16\" r=\"3\"/></svg>",
    "coding": f"<svg {_LUCIDE}><path d=\"m18 16 4-4-4-4\"/><path d=\"m6 8-4 4 4 4\"/><path d=\"M10.5 4 8 16\"/><path d=\"m14.5 4 7 16\"/></svg>",
    "automation_lab": f"<svg {_LUCIDE}><rect width=\"8\" height=\"8\" x=\"3\" y=\"3\" rx=\"2\"/><path d=\"M7 11v4a2 2 0 0 0 2 2h4\"/><rect width=\"8\" height=\"8\" x=\"13\" y=\"13\" rx=\"2\"/></svg>",
    "dashboard": f"<svg {_LUCIDE}><path d=\"M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2\"/><circle cx=\"12\" cy=\"7\" r=\"4\"/></svg>",
    "premium": f"<svg {_LUCIDE}><path d=\"M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.734H5.81a1 1 0 0 1-.957-.734L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z\"/></svg>",
    "logout": f"<svg {_LUCIDE}><path d=\"M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4\"/><polyline points=\"16 17 21 12 16 7\"/><line x1=\"21\" x2=\"9\" y1=\"12\" y2=\"12\"/></svg>",
}

_BRAND_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="24" height="24">'
    '<defs><linearGradient id="mbs" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#6366f1"/>'
    '</linearGradient></defs><rect width="40" height="40" rx="9" fill="url(#mbs)"/>'
    '<path d="M11 28V12l6.5 8.5L24 12v16" fill="none" stroke="#fff" stroke-width="2.4" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def _icon_uri(page: str) -> str:
    svg = (_ICONS.get(page) or _ICONS["home"]).format(c="%23a1a1aa")
    return f'url("data:image/svg+xml,{quote(svg)}")'


def _plan_label(plan: str) -> str:
    key = (plan or "free").strip().lower()
    if key in ("none", ""):
        return "Free"
    if key == "elite":
        return "Elite"
    return key.replace("_", " ").title()


def _user_initial(username: str) -> str:
    u = (username or "U").strip()
    return (u[0] or "U").upper()


def _nav_button_css(active: str) -> str:
    rules: list[str] = []
    for _label, page in NAV_ITEMS:
        uri = _icon_uri(page)
        rules.append(
            f"""
{_SB} .st-key-nav_go_{page} {{ margin:0 0 2px!important; flex-shrink:0!important; }}
{_SB} .st-key-nav_go_{page} .stButton {{ margin:0!important; padding:0!important; width:100%!important; }}
{_SB} .st-key-nav_go_{page} .stButton>button {{
  width:100%!important;height:40px!important;min-height:40px!important;
  padding:0 12px 0 38px!important;border-radius:10px!important;
  border:1px solid transparent!important;background:transparent!important;
  color:#a1a1aa!important;font-size:13px!important;font-weight:500!important;
  text-align:left!important;position:relative!important;
  border-left:4px solid transparent!important;box-shadow:none!important;
}}
{_SB} .st-key-nav_go_{page} .stButton>button:hover {{
  background:rgba(255,255,255,.04)!important;border-color:transparent!important;
}}
{_SB} .st-key-nav_go_{page} .stButton>button::before {{
  content:'';position:absolute;left:12px;top:50%;transform:translateY(-50%);
  width:16px;height:16px;background-image:{uri};
  background-size:16px;background-repeat:no-repeat;
}}"""
        )
        if page == active:
            rules.append(
                f"""
{_SB} .st-key-nav_go_{page} .stButton>button {{
  background:rgba(124,58,237,.18)!important;border-left-color:#8b5cf6!important;
  color:#ffffff!important;font-weight:600!important;
}}"""
            )
    return "".join(rules)


def sidebar_master_css(active_page: str) -> str:
    logout_uri = _icon_uri("logout")
    return f"""
:root{{--sb-width:{_WIDTH};}}
{_SB}{{
  width:var(--sb-width)!important;min-width:var(--sb-width)!important;max-width:var(--sb-width)!important;
  background:#09090b!important;border-right:1px solid rgba(255,255,255,.06)!important;
}}
{_SB}>div{{
  padding:0 8px 8px!important;background:#09090b!important;
  height:100dvh!important;max-height:100dvh!important;
  display:flex!important;flex-direction:column!important;overflow:hidden!important;
  box-sizing:border-box!important;
}}
{_SB} [data-testid="stSidebarContent"],
{_SB} [data-testid="stSidebarUserContent"]{{
  padding:0!important;background:#09090b!important;
  display:flex!important;flex-direction:column!important;
  flex:1!important;min-height:0!important;overflow:hidden!important;
}}
{_SB} [data-testid="stSidebarNav"]{{display:none!important;}}
{_SB} [data-testid="stVerticalBlock"],
{_SB} [data-testid="stVerticalBlockBorderWrapper"]{{
  gap:0!important;padding:0!important;margin:0!important;border:none!important;
  box-shadow:none!important;background:transparent!important;
  display:flex!important;flex-direction:column!important;
  flex:1!important;min-height:0!important;overflow:hidden!important;
}}
{_SB} .st-key-sb_brand,
{_SB} .st-key-sb_scroll,
{_SB} .st-key-sb_foot,
{_SB} .st-key-nav_logout {{
  flex-shrink:0!important;
}}
{_SB} .st-key-sb_scroll {{
  flex:1 1 auto!important;min-height:0!important;overflow-y:auto!important;
  overflow-x:hidden!important;margin:0 -2px;padding:0 2px!important;
}}
.sb-brand-wrap {{ display:flex; align-items:center; gap:8px; padding:6px 4px 12px; }}
.sb-brand-wrap svg {{ width:24px!important;height:24px!important;flex-shrink:0; }}
.sb-brand-wrap span {{ color:#fafafa!important;font-size:14px;font-weight:600;letter-spacing:-.02em; }}
.sb-section {{
  color:#52525b!important;font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
  padding:12px 8px 4px;margin:0;line-height:1.2;
}}
.sb-user {{
  display:flex;align-items:center;gap:8px;padding:8px;border-radius:10px;
  background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.05);margin-bottom:8px;
}}
.sb-av {{
  width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,#7c3aed,#6366f1);
  color:#fff;font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;
}}
.sb-un {{ color:#e4e4e7!important;font-size:12px;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap; }}
.sb-up {{ color:#71717a!important;font-size:10px;line-height:1.2;margin-top:1px; }}
.sb-foot {{ padding-top:8px;border-top:1px solid rgba(255,255,255,.06); }}
{_nav_button_css(active_page)}
{_SB} .st-key-nav_logout{{margin-top:0!important;}}
{_SB} .st-key-nav_logout .stButton{{margin:0!important;padding:0!important;width:100%!important;}}
{_SB} .st-key-nav_logout .stButton>button{{
  width:100%!important;height:40px!important;min-height:40px!important;padding:0 12px 0 38px!important;
  border-radius:10px!important;border:1px solid rgba(255,255,255,.07)!important;
  background:rgba(255,255,255,.02)!important;color:#a1a1aa!important;font-size:13px!important;
  font-weight:500!important;text-align:left!important;position:relative!important;
}}
{_SB} .st-key-nav_logout .stButton>button::before{{
  content:'';position:absolute;left:12px;top:50%;transform:translateY(-50%);
  width:16px;height:16px;background-image:{logout_uri};
  background-size:16px;background-repeat:no-repeat;
}}
"""


def _resolve_active(active_page: str | None) -> str:
    p = (active_page or st.session_state.get("page") or "home").strip()
    return LEGACY_PAGE_ALIASES.get(p, p)


def _go_page(page: str) -> None:
    target = LEGACY_PAGE_ALIASES.get(page, page)
    if st.session_state.get("page") != target:
        st.session_state.page = target
        st.rerun()


def render_sidebar(active_page: str | None = None) -> None:
    active = _resolve_active(active_page)
    inject_css(sidebar_master_css(active))
    user = str(st.session_state.get("user") or "User")
    plan = _plan_label(str(st.session_state.get("plan") or "free"))

    with st.sidebar:
        with st.container(key="sb_brand"):
            st.markdown(
                f'<div class="sb-brand-wrap">{_BRAND_SVG}<span>{html.escape(APP_NAME)}</span></div>',
                unsafe_allow_html=True,
            )

        with st.container(key="sb_scroll"):
            for section_title, items in NAV_SECTIONS:
                st.markdown(
                    f'<p class="sb-section">{html.escape(section_title)}</p>',
                    unsafe_allow_html=True,
                )
                for label, page in items:
                    if st.button(
                        label,
                        key=f"nav_go_{page}",
                        use_container_width=True,
                        type="secondary",
                    ):
                        _go_page(page)

        with st.container(key="sb_foot"):
            st.markdown(
                f"""
<div class="sb-foot">
  <div class="sb-user">
    <div class="sb-av">{html.escape(_user_initial(user))}</div>
    <div>
      <div class="sb-un">{html.escape(user)}</div>
      <div class="sb-up">{html.escape(plan)}</div>
    </div>
  </div>
</div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Abmelden", key="nav_logout", use_container_width=True, type="secondary"):
                from services.session_auth import logout_session
                logout_session()
                st.rerun()
