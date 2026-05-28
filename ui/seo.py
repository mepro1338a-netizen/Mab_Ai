"""SEO / OpenGraph meta injection for Streamlit."""
from __future__ import annotations

import html

import streamlit as st

from config import APP_BASE_URL, APP_NAME, APP_TAGLINE


def inject_seo_meta() -> None:
    title = f"{APP_NAME} — AI Operating System"
    desc = APP_TAGLINE or "One AI system. Infinite workflows."
    url = APP_BASE_URL or "https://mabyte.de"
    image = f"{url.rstrip('/')}/static/og-preview.png"

    st.markdown(
        f"""
<meta name="description" content="{html.escape(desc)}" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{html.escape(title)}" />
<meta property="og:description" content="{html.escape(desc)}" />
<meta property="og:url" content="{html.escape(url)}" />
<meta property="og:site_name" content="{html.escape(APP_NAME)}" />
<meta property="og:image" content="{html.escape(image)}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{html.escape(title)}" />
<meta name="twitter:description" content="{html.escape(desc)}" />
<meta name="theme-color" content="#09090b" />
        """,
        unsafe_allow_html=True,
    )
