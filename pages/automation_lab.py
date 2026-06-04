"""Content Automation — Instagram, TikTok, YouTube Shorts."""
from __future__ import annotations

import html

import streamlit as st

from database import create_automation, list_automations
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
.ca-sub { margin: 8px 0 28px; font-size: 14px; color: #94a3b8; line-height: 1.5; }
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
.ca-form {
  padding: 24px 22px; border-radius: 16px;
  background: linear-gradient(145deg, rgba(24,24,27,.94), rgba(15,15,20,.9));
  border: 1px solid rgba(139,92,246,.2);
  box-shadow: 0 16px 48px rgba(0,0,0,.4);
}
.ca-empty {
  padding: 28px 20px; text-align: center; color: #64748b; font-size: 14px;
  border: 1px dashed rgba(255,255,255,.1); border-radius: 14px;
}
"""


def _css() -> None:
    inject_css(MB_THEME_VARS + page_layout_css(1080, 0, 36) + _CSS)


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
<div class="ca-page">
  <h1 class="ca-h1">Content Automation</h1>
  <p class="ca-sub">Create, schedule and publish content automatically.</p>
""",
        unsafe_allow_html=True,
    )


def _render_available_cards() -> None:
    st.markdown('<p class="ca-section">Available Platforms</p>', unsafe_allow_html=True)

    cards = (
        (
            "instagram",
            "📸",
            "Instagram",
            ("Generate Content", "Schedule Post", "Auto Publish"),
        ),
        (
            "tiktok",
            "🎵",
            "TikTok",
            ("Generate Content", "Schedule Post", "Auto Publish"),
        ),
        (
            "youtube",
            "▶",
            "YouTube Shorts",
            ("Generate Content", "Schedule Post", "Auto Publish"),
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
                "Create Automation",
                key=f"ca_card_{pid}",
                use_container_width=True,
                type="primary",
            ):
                st.session_state["ca_platform"] = pid
                st.session_state["ca_form_platform"] = pid
                st.rerun()


def _render_active_table(username: str) -> None:
    st.markdown('<p class="ca-section">Active Automations</p>', unsafe_allow_html=True)
    rows = [r for r in list_automations(username) if _is_content_automation(r)]

    if not rows:
        st.markdown(
            '<div class="ca-empty">Noch keine aktiven Automationen. '
            "Wähle eine Vorlage oder erstelle eine neue Automation unten.</div>",
            unsafe_allow_html=True,
        )
        return

    body = []
    for item in rows[:20]:
        platform = _row_platform(item)
        freq = _row_frequency(item)
        status = str(item.get("status") or "active").lower()
        status_cls = "active" if status == "active" else "paused"
        status_lbl = "Active" if status == "active" else status.title()
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
    st.markdown('<p class="ca-section">New Automation</p>', unsafe_allow_html=True)

    st.session_state.setdefault("ca_platform", "instagram")
    st.session_state.setdefault("ca_form_platform", st.session_state.get("ca_platform", "instagram"))

    platform_keys = [p[0] for p in _PLATFORMS]
    content_keys = [c[0] for c in _CONTENT_TYPES]
    freq_keys = [f[0] for f in _FREQUENCIES]

    if st.session_state.get("ca_form_platform") not in platform_keys:
        st.session_state["ca_form_platform"] = "instagram"

    with st.container():
        st.markdown('<div class="ca-form">', unsafe_allow_html=True)

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

        if st.button("Start Automation", type="primary", use_container_width=True, key="ca_start"):
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
                st.success(f"Automation gestartet: {name}")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


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
    _render_available_cards()
    _render_active_table(username)
    _render_create_form(username)
    st.markdown("</div>", unsafe_allow_html=True)
