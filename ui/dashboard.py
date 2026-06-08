"""MaByte Home — slogan header + news feed."""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from ui.styles import inject_css
from ui_core import img_base64

_ROOT = Path(__file__).resolve().parent.parent
_HEADER_CANDIDATES = (
    _ROOT / "assets" / "headerslogan.png",
    _ROOT / "assets" / "sloganheader.png",
    _ROOT / "sloganheader.png",
)

NEWS_ITEMS: list[tuple[str, str, str]] = [
    ("02. Jun 2026", "Dashboard neu", "Home mit Slogan-Header und News — alles Wichtige auf einen Blick."),
    ("30. Mai 2026", "Elite Plan", "Höhere Limits, Premium-Features und Football AI im Workspace."),
    ("28. Mai 2026", "Workspace Update", "Image, Video und Automation laufen jetzt über eine einheitliche Oberfläche."),
]

_DASH_CSS = """
.stApp:has(.mb-dash) section.main .block-container {
    max-width: 100% !important;
    padding: 0 !important;
}
.mb-dash {
    display: flex;
    flex-direction: column;
    gap: var(--mb-gap-section, 20px);
}
.mb-dash-hero {
    width: 100%;
    line-height: 0;
    overflow: hidden;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.mb-dash-hero img {
    width: 100%;
    height: auto;
    max-height: 140px;
    object-fit: contain;
    object-position: center;
    display: block;
    background: #050816;
}
.mb-dash-body {
    max-width: var(--mb-content-max, 1100px);
    margin: 0 auto;
    padding: 0 var(--mb-content-pad-x, 1.5rem) 48px;
    width: 100%;
    box-sizing: border-box;
}
.mb-dash-label {
    font-size: var(--mb-label-size, 10px);
    font-weight: var(--mb-label-weight, 700);
    letter-spacing: var(--mb-label-spacing, 0.12em);
    text-transform: uppercase;
    color: var(--mb-label-color, #a78bfa) !important;
    margin: 0 0 var(--mb-gap-card, 12px);
}
.mb-news {
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.mb-news-item {
    padding: 14px 16px;
    border-radius: 12px;
    background: rgba(24, 24, 27, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: border-color 0.12s ease, background 0.12s ease;
}
.mb-news-item:hover {
    border-color: rgba(139, 92, 246, 0.28);
    background: rgba(124, 58, 237, 0.06);
}
.mb-news-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}
.mb-news-date {
    font-size: 11px;
    font-weight: 600;
    color: #71717a !important;
}
.mb-news-tag {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #e9d5ff !important;
    padding: 2px 8px;
    border-radius: 999px;
    background: rgba(124, 58, 237, 0.14);
    border: 1px solid rgba(139, 92, 246, 0.22);
}
.mb-news-title {
    margin: 0;
    font-size: 15px;
    font-weight: 700;
    color: #fafafa !important;
    line-height: 1.3;
}
.mb-news-text {
    margin: 6px 0 0;
    font-size: 13px;
    line-height: 1.55;
    color: #94a3b8 !important;
}
@media (max-width: 768px) {
    .mb-dash-hero img { max-height: 96px; }
    .mb-dash-body { padding-bottom: 32px; }
}
"""


def _header_path() -> Path | None:
    for path in _HEADER_CANDIDATES:
        if path.is_file():
            return path
    return None


def _header_html() -> str:
    path = _header_path()
    if not path:
        return ""
    b64 = img_base64(path)
    if not b64:
        return ""
    return (
        f'<div class="mb-dash-hero">'
        f'<img src="data:image/png;base64,{b64}" alt="MaByte — One system. Infinite intelligence." />'
        f"</div>"
    )


def _news_html() -> str:
    rows: list[str] = []
    for date, title, text in NEWS_ITEMS:
        rows.append(
            f'<article class="mb-news-item">'
            f'<div class="mb-news-meta">'
            f'<span class="mb-news-date">{html.escape(date)}</span>'
            f'<span class="mb-news-tag">News</span>'
            f"</div>"
            f'<h3 class="mb-news-title">{html.escape(title)}</h3>'
            f'<p class="mb-news-text">{html.escape(text)}</p>'
            f"</article>"
        )
    return "".join(rows)


def render_home() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    inject_css(_DASH_CSS)

    st.markdown(
        f"""
<div class="mb-dash">
  {_header_html()}
  <div class="mb-dash-body">
    <p class="mb-dash-label">News</p>
    <div class="mb-news">{_news_html()}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
