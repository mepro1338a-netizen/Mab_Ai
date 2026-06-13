"""Content Automation — Instagram, TikTok, YouTube Shorts."""
from __future__ import annotations

import html

import streamlit as st

from database import create_automation, list_automations, get_user
from ui_core import require_plan_feature
from ui.styles import MB_THEME_VARS, inject_css, page_layout_css

_PLATFORMS = (
    ("instagram", "Instagram", "Instagram Reels"),
    ("tiktok", "TikTok", "TikTok"),
    ("youtube", "YouTube", "YouTube Shorts"),
)

_CONTENT_TYPES = (
    ("ai", "AI"),
    ("news", "News"),
    ("business", "Business"),
    ("marketing", "Marketing"),
    ("custom", "Custom"),
)

_FREQUENCIES = (
    ("daily", "Daily"),
    ("weekly", "Weekly"),
    ("manual", "Manual"),
)

_VALID_PLATFORMS = frozenset({"instagram", "tiktok", "youtube"})
_LEGACY_SKIP = frozenset({
    "football", "football_content_agent", "content_repurpose_agent",
    "developer_report_agent", "creative_asset_agent", "social_posting_agent",
})

_PLATFORM_LABEL = {k: label for k, label, _ in _PLATFORMS}
_FREQ_LABEL = {k: label for k, label in _FREQUENCIES}


_CSS = """
.ca-page { max-width: 1080px; margin: 0 auto; padding-bottom: 48px; }
.ca-h1 { margin: 0; font-size: 26px; font-weight: 800; color: #fafafa; letter-spacing: -.02em; }
.ca-tagline { margin: 6px 0 0; font-size: 14px; color: #a78bfa; font-weight: 600; }
.ca-sub { margin: 8px 0 8px; font-size: 14px; color: #94a3b8; line-height: 1.5; }
.ca-beta-note {
  margin: 0 0 28px; font-size: 12px; color: #a78bfa;
  padding: 8px 12px; border-radius: 8px;
  background: rgba(139,92,246,.08); border: 1px solid rgba(139,92,246,.2);
}
.ca-section {
  font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
  color: #71717a; margin: 32px 0 14px;
}
.ca-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
@media (max-width: 900px) { .ca-grid { grid-template-columns: 1fr; } }
.ca-card {
  padding: 22px 20px; border-radius: 16px;
  background: linear-gradient(145deg, rgba(24,24,27,.92), rgba(15,15,20,.88));
  border: 1px solid rgba(255,255,255,.08);
  box-shadow: 0 12px 40px rgba(0,0,0,.35);
  min-height: 220px;
}
.ca-card:hover { border-color: rgba(139,92,246,.35); }
.ca-card-icon {
  width: 40px; height: 40px; border-radius: 12px;
  background: rgba(124,58,237,.18); border: 1px solid rgba(139,92,246,.3);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; margin-bottom: 14px;
}
.ca-card h3 { margin: 0 0 8px; font-size: 17px; color: #f8fafc; font-weight: 700; }
.ca-feat { list-style: none; padding: 0; margin: 0 0 16px; }
.ca-feat li {
  font-size: 13px; color: #94a3b8; padding: 4px 0 4px 18px; position: relative;
}
.ca-feat li::before {
  content: ""; position: absolute; left: 0; top: 11px; width: 6px; height: 6px;
  border-radius: 50%; background: #8b5cf6;
}
.ca-table-wrap {
  border-radius: 14px; overflow: hidden;
  border: 1px solid rgba(255,255,255,.08);
  background: rgba(15,23,42,.55);
}
.ca-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.ca-table th {
  text-align: left; padding: 12px 16px; color: #71717a; font-weight: 600;
  font-size: 11px; text-transform: uppercase; letter-spacing: .06em;
  background: rgba(0,0,0,.25); border-bottom: 1px solid rgba(255,255,255,.06);
}
.ca-table td {
  padding: 14px 16px; color: #e2e8f0; border-bottom: 1px solid rgba(255,255,255,.05);
}
.ca-table tr:last-child td { border-bottom: none; }
.ca-status {
  display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 600;
}
.ca-status.active { background: rgba(34,197,94,.15); color: #4ade80; }
.ca-status.paused { background: rgba(113,113,122,.2); color: #a1a1aa; }
.ca-empty {
  padding: 28px 20px; text-align: center; color: #64748b; font-size: 14px;
  border: 1px dashed rgba(255,255,255,.1); border-radius: 14px;
}

/* ---- Form controls (scoped via .mb-auto page marker) ---- */
.stApp:has(.mb-auto) section.main .block-container {
  max-width: 1080px !important;
}
.stApp:has(.mb-auto) .st-key-ca_form_wrap div[data-testid="stVerticalBlockBorderWrapper"] {
  padding: 24px 22px !important;
  border-radius: 16px !important;
  background: linear-gradient(145deg, rgba(24,24,27,.72), rgba(15,15,20,.55)) !important;
  border: 1px solid rgba(139,92,246,.22) !important;
  backdrop-filter: blur(16px) !important;
  -webkit-backdrop-filter: blur(16px) !important;
  box-shadow: 0 16px 48px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.04) !important;
}
.stApp:has(.mb-auto) .st-key-ca_form_wrap [data-testid="column"] { min-width: 0; }
.stApp:has(.mb-auto) .st-key-ca_form_wrap [data-testid="stSelectbox"] { margin-bottom: 0 !important; }
.stApp:has(.mb-auto) .st-key-ca_form_wrap [data-testid="stSelectbox"] label[data-testid="stWidgetLabel"] p,
.stApp:has(.mb-auto) .st-key-ca_form_wrap [data-testid="stSelectbox"] label p,
.stApp:has(.mb-auto) .st-key-ca_form_prompt label[data-testid="stWidgetLabel"] p,
.stApp:has(.mb-auto) .st-key-ca_form_prompt label p {
  font-size: 11px !important; font-weight: 700 !important;
  letter-spacing: .06em !important; text-transform: uppercase !important;
  color: #a1a1aa !important; margin-bottom: 6px !important;
}
.stApp:has(.mb-auto) .st-key-ca_form_wrap [data-testid="stSelectbox"] [data-baseweb="select"] > div,
.stApp:has(.mb-auto) .st-key-ca_form_wrap div[data-baseweb="select"] > div {
  min-height: 42px !important; border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,.1) !important;
  background: rgba(24,24,27,.65) !important;
  backdrop-filter: blur(12px) !important; -webkit-backdrop-filter: blur(12px) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.04) !important;
  transition: border-color .15s ease, box-shadow .15s ease, background .15s ease !important;
}
.stApp:has(.mb-auto) .st-key-ca_form_wrap [data-baseweb="select"]:hover > div {
  border-color: rgba(139,92,246,.35) !important;
  background: rgba(30,27,46,.72) !important;
}
.stApp:has(.mb-auto) .st-key-ca_form_wrap [data-baseweb="select"]:focus-within > div {
  border-color: rgba(139,92,246,.65) !important;
  box-shadow: 0 0 0 1px rgba(139,92,246,.25), inset 0 1px 0 rgba(255,255,255,.04) !important;
}
.stApp:has(.mb-auto) .st-key-ca_form_wrap [data-baseweb="select"] span {
  color: #f4f4f5 !important; font-size: 13px !important; font-weight: 500 !important;
}
.stApp:has(.mb-auto) .st-key-ca_form_wrap [data-baseweb="select"] svg { fill: #a78bfa !important; }
.stApp:has(.mb-auto) .st-key-ca_form_prompt [data-testid="stTextArea"] > div,
.stApp:has(.mb-auto) .st-key-ca_form_prompt div[data-baseweb="textarea"] {
  border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,.1) !important;
  background: rgba(24,24,27,.65) !important;
  backdrop-filter: blur(12px) !important; -webkit-backdrop-filter: blur(12px) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.04) !important;
  transition: border-color .15s ease, box-shadow .15s ease !important;
}
.stApp:has(.mb-auto) .st-key-ca_form_prompt div[data-baseweb="textarea"]:hover {
  border-color: rgba(139,92,246,.35) !important;
}
.stApp:has(.mb-auto) .st-key-ca_form_prompt div[data-baseweb="textarea"]:focus-within {
  border-color: rgba(139,92,246,.65) !important;
  box-shadow: 0 0 0 1px rgba(139,92,246,.25), inset 0 1px 0 rgba(255,255,255,.04) !important;
}
.stApp:has(.mb-auto) .st-key-ca_form_prompt textarea {
  background: transparent !important; color: #f4f4f5 !important;
  -webkit-text-fill-color: #f4f4f5 !important; font-size: 14px !important; line-height: 1.5 !important;
}
.stApp:has(.mb-auto) .st-key-ca_form_prompt textarea::placeholder {
  color: rgba(161,161,170,.75) !important; -webkit-text-fill-color: rgba(161,161,170,.75) !important;
}
.stApp:has(.mb-auto) [class*="st-key-ca_card_"] .stButton > button,
.stApp:has(.mb-auto) [class*="st-key-ca_card_"] button[data-testid="stBaseButton-primary"] {
  min-height: 42px !important; border-radius: 12px !important;
  border: 1px solid rgba(139,92,246,.35) !important;
  background: rgba(124,58,237,.14) !important;
  background-color: rgba(124,58,237,.14) !important;
  color: #e9d5ff !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.06), 0 4px 16px rgba(0,0,0,.2) !important;
  font-weight: 600 !important; font-size: 13px !important;
  backdrop-filter: blur(10px) !important; -webkit-backdrop-filter: blur(10px) !important;
}
.stApp:has(.mb-auto) [class*="st-key-ca_card_"] .stButton > button:hover,
.stApp:has(.mb-auto) [class*="st-key-ca_card_"] button[data-testid="stBaseButton-primary"]:hover {
  border-color: rgba(167,139,250,.55) !important;
  background: rgba(124,58,237,.28) !important;
  background-color: rgba(124,58,237,.28) !important;
  color: #faf5ff !important;
  box-shadow: 0 0 20px rgba(139,92,246,.2), inset 0 1px 0 rgba(255,255,255,.08) !important;
  transform: translateY(-1px) !important;
}
.stApp:has(.mb-auto) [class*="st-key-ca_card_"] .stButton > button p,
.stApp:has(.mb-auto) [class*="st-key-ca_card_"] button[data-testid="stBaseButton-primary"] p {
  color: inherit !important; font-weight: 600 !important;
}
.stApp:has(.mb-auto) .st-key-ca_start .stButton > button,
.stApp:has(.mb-auto) .st-key-ca_start button[data-testid="stBaseButton-primary"] {
  min-height: 46px !important; border-radius: 12px !important;
  border: 1px solid rgba(139,92,246,.45) !important;
  background: linear-gradient(135deg, rgba(124,58,237,.95), rgba(99,102,241,.88)) !important;
  background-color: #7c3aed !important;
  color: #ffffff !important;
  box-shadow: 0 8px 24px rgba(124,58,237,.35), inset 0 1px 0 rgba(255,255,255,.12) !important;
  font-weight: 700 !important;
}
.stApp:has(.mb-auto) .st-key-ca_start .stButton > button:hover,
.stApp:has(.mb-auto) .st-key-ca_start button[data-testid="stBaseButton-primary"]:hover {
  border-color: rgba(167,139,250,.65) !important;
  background: linear-gradient(135deg, rgba(109,40,217,.98), rgba(91,33,182,.92)) !important;
  background-color: #6d28d9 !important;
  box-shadow: 0 10px 28px rgba(124,58,237,.45), inset 0 1px 0 rgba(255,255,255,.14) !important;
  transform: translateY(-1px) !important;
}
.stApp:has(.mb-auto) .st-key-ca_start .stButton > button p,
.stApp:has(.mb-auto) .st-key-ca_start button[data-testid="stBaseButton-primary"] p {
  color: #ffffff !important; font-weight: 700 !important;
}
"""


def _css() -> None:
    inject_css(MB_THEME_VARS + page_layout_css(1080, 20, 36) + _CSS)


def _is_content_automation(item: dict) -> bool:
    atype = str(item.get("automation_type") or "").lower()
    src = str(item.get("source_workspace") or "").lower()
    if atype in _LEGACY_SKIP or src in _LEGACY_SKIP:
        return False
    return atype in _VALID_PLATFORMS


def _row_platform(item: dict) -> str:
    return _platform_label(item.get("automation_type"))


def _platform_label(key: str) -> str:
    return _PLATFORM_LABEL.get(str(key or "").lower(), str(key or "—"))


def _freq_label(key: str) -> str:
    return _FREQ_LABEL.get(str(key or "").lower(), str(key or "—"))


def _row_frequency(item: dict) -> str:
    key = str(item.get("target_workspace") or "").lower()
    if key in _FREQ_LABEL:
        return _freq_label(key)
    return "Manual"


def _automation_name(platform: str, content_type: str) -> str:
    pl = _platform_label(platform)
    ct = next((lbl for k, lbl in _CONTENT_TYPES if k == content_type), content_type.title())
    return f"{pl} · {ct}"


def _render_header() -> None:
    st.markdown(
        """
<div class="ca-page mb-auto">
  <h1 class="ca-h1">Content Automation</h1>
  <p class="ca-sub">Plattformen und Prompts speichern — automatisches Veröffentlichen folgt in der Beta.</p>
  <p class="ca-beta-note">Status: Konfiguration aktiv · Ausführung (Posting) noch nicht live</p>
""",
        unsafe_allow_html=True,
    )


def _render_available_cards() -> None:
    st.markdown('<p class="ca-section">Verfügbare Plattformen</p>', unsafe_allow_html=True)

    cards = (
        (
            "instagram",
            "📸",
            "Instagram",
            ("Plattform wählen", "Prompt speichern", "Posting folgt in Beta"),
        ),
        (
            "tiktok",
            "🎵",
            "TikTok",
            ("Plattform wählen", "Prompt speichern", "Posting folgt in Beta"),
        ),
        (
            "youtube",
            "▶",
            "YouTube Shorts",
            ("Plattform wählen", "Prompt speichern", "Posting folgt in Beta"),
        ),
    )

    cols = st.columns(3)
    for col, (pid, icon, title, feats) in zip(cols, cards):
        feats_html = "".join(f"<li>{html.escape(f)}</li>" for f in feats)
        with col:
            st.markdown(
                f"""
<div class="ca-card">
  <div class="ca-card-icon">{html.escape(icon)}</div>
  <h3>{html.escape(title)}</h3>
  <ul class="ca-feat">{feats_html}</ul>
</div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "Plattform wählen",
                key=f"ca_card_{pid}",
                use_container_width=True,
                type="primary",
            ):
                st.session_state["ca_platform"] = pid
                st.session_state["ca_form_platform"] = pid
                st.rerun()


def _render_active_table(username: str) -> None:
    st.markdown('<p class="ca-section">Gespeicherte Automationen</p>', unsafe_allow_html=True)
    rows = [r for r in list_automations(username) if _is_content_automation(r)]

    if not rows:
        st.markdown(
            '<div class="ca-empty">Noch keine Automation gespeichert. '
            "Wähle eine Plattform und lege unten eine Konfiguration an — "
            "die Ausführung startet in der Beta noch nicht automatisch.</div>",
            unsafe_allow_html=True,
        )
        return

    body = []
    for item in rows[:20]:
        platform = _row_platform(item)
        freq = _row_frequency(item)
        status = str(item.get("status") or "active").lower()
        status_cls = "active" if status == "active" else "paused"
        status_lbl = "Gespeichert" if status == "active" else status.title()
        body.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('name') or 'Automation'))}</td>"
            f"<td>{html.escape(platform)}</td>"
            f"<td>{html.escape(freq)}</td>"
            f'<td><span class="ca-status {status_cls}">{html.escape(status_lbl)}</span></td>'
            "</tr>"
        )

    st.markdown(
        f"""
<div class="ca-table-wrap">
  <table class="ca-table">
    <thead><tr>
      <th>Name</th><th>Platform</th><th>Frequency</th><th>Status</th>
    </tr></thead>
    <tbody>{"".join(body)}</tbody>
  </table>
</div>
        """,
        unsafe_allow_html=True,
    )


def _render_create_form(username: str) -> None:
    st.markdown('<p class="ca-section">Neue Automation</p>', unsafe_allow_html=True)
    st.caption(
        "Speichert Plattform, Rhythmus und Prompt in deinem Account. "
        "Automatisches Posten ist in dieser Beta-Version noch nicht aktiv."
    )

    st.session_state.setdefault("ca_platform", "instagram")
    st.session_state.setdefault("ca_form_platform", st.session_state.get("ca_platform", "instagram"))

    platform_keys = [p[0] for p in _PLATFORMS]
    content_keys = [c[0] for c in _CONTENT_TYPES]
    freq_keys = [f[0] for f in _FREQUENCIES]

    if st.session_state.get("ca_form_platform") not in platform_keys:
        st.session_state["ca_form_platform"] = "instagram"

    with st.container(key="ca_form_wrap", border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            platform = st.selectbox(
                "Platform",
                platform_keys,
                format_func=lambda x: _platform_label(x),
                key="ca_form_platform",
            )
        with c2:
            content_type = st.selectbox(
                "Content Type",
                content_keys,
                format_func=lambda x: next(l for k, l in _CONTENT_TYPES if k == x),
                key="ca_form_content",
            )
        with c3:
            frequency = st.selectbox(
                "Frequency",
                freq_keys,
                format_func=lambda x: _freq_label(x),
                key="ca_form_frequency",
            )

        prompt = st.text_area(
            "Prompt",
            placeholder="Create one motivational AI reel every day.",
            height=120,
            key="ca_form_prompt",
        )

        if st.button("Automation speichern", type="primary", use_container_width=True, key="ca_start"):
            text = (prompt or "").strip()
            if not text:
                st.warning("Bitte einen Prompt eingeben.")
            else:
                name = _automation_name(platform, content_type)
                create_automation(
                    username=username,
                    project_id=0,
                    name=name,
                    automation_type=platform,
                    source_workspace=content_type,
                    target_workspace=frequency,
                    trigger_text=text,
                )
                st.session_state.pop("ca_form_prompt", None)
                st.success(
                    f"Konfiguration gespeichert: {name}. "
                    "Automatische Ausführung folgt in einem späteren Beta-Update."
                )
                st.rerun()


def render_automation_lab() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    username = str(st.session_state.get("user") or "")
    if not username:
        st.session_state.page = "auth"
        st.rerun()
        return

    _css()
    _render_header()

    user = get_user(username) or {"username": username, "plan": st.session_state.get("plan", "free")}
    if not require_plan_feature(
        "automation",
        user=user,
        message="Content Automation ist ab **Grand** verfügbar.",
        button_key="ca_plan_upgrade",
    ):
        st.markdown("</div>", unsafe_allow_html=True)
        return

    _render_available_cards()
    _render_active_table(username)
    _render_create_form(username)
    st.markdown("</div>", unsafe_allow_html=True)
