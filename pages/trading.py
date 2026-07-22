"""Trading Workspace — Marktübersicht & Watchlist (Starter)."""
from __future__ import annotations

import html

import streamlit as st

from ui.styles import inject_css, page_layout_css

_CSS = """
.tr-page { max-width: 980px; margin: 0 auto; padding-bottom: 48px; }
.tr-h1 { margin: 0; font-size: 26px; font-weight: 800; color: #fafafa; letter-spacing: -.02em; }
.tr-tagline { margin: 6px 0 0; font-size: 14px; color: #a78bfa; font-weight: 600; }
.tr-sub { margin: 8px 0 20px; font-size: 14px; color: #94a3b8; line-height: 1.5; }
.tr-note {
  margin: 0 0 24px; font-size: 12px; color: #a78bfa;
  padding: 8px 12px; border-radius: 8px;
  background: rgba(139,92,246,.08); border: 1px solid rgba(139,92,246,.2);
}
.tr-section {
  font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
  color: #71717a; margin: 8px 0 14px;
}
.tr-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
@media (max-width: 900px) { .tr-grid { grid-template-columns: 1fr; } }
.tr-card {
  padding: 18px 16px; border-radius: 14px;
  background: linear-gradient(145deg, rgba(24,24,27,.92), rgba(15,15,20,.88));
  border: 1px solid rgba(255,255,255,.08);
  box-shadow: 0 12px 40px rgba(0,0,0,.35); min-height: 140px;
}
.tr-card h3 { margin: 0 0 8px; font-size: 16px; color: #f8fafc; font-weight: 700; }
.tr-card p { margin: 0; font-size: 13px; color: #94a3b8; line-height: 1.45; }
"""


def render_trading() -> None:
    inject_css(page_layout_css(980, 20, 48) + _CSS)

    user = html.escape(str(st.session_state.get("user") or "User"))
    st.markdown(
        f"""
<div class="tr-page">
  <h1 class="tr-h1">Trading</h1>
  <p class="tr-tagline">Marktübersicht &amp; Watchlist</p>
  <p class="tr-sub">
    Workspace für Charts, Signale und Watchlists — angemeldet als <strong>{user}</strong>.
  </p>
  <p class="tr-note">Beta: Erste Version. Live-Daten und Order-Flow folgen schrittweise.</p>
  <p class="tr-section">Bereiche</p>
  <div class="tr-grid">
    <div class="tr-card">
      <h3>Marktübersicht</h3>
      <p>Indizes, FX und ausgewählte Assets auf einen Blick.</p>
    </div>
    <div class="tr-card">
      <h3>Watchlist</h3>
      <p>Favoriten speichern und Kursbewegungen verfolgen.</p>
    </div>
    <div class="tr-card">
      <h3>Signale</h3>
      <p>KI-gestützte Hinweise — bald verfügbar.</p>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="tr-section" style="margin-top:28px">Schnellstart</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input(
            "Symbol",
            value="EURUSD",
            placeholder="z. B. EURUSD, BTCUSD, AAPL",
            key="tr_symbol",
        )
    with col2:
        timeframe = st.selectbox(
            "Zeitrahmen",
            options=["1H", "4H", "1D", "1W"],
            index=2,
            key="tr_timeframe",
        )

    if st.button("Analyse vorbereiten", key="tr_prepare", use_container_width=True, type="primary"):
        sym = (symbol or "").strip().upper() or "EURUSD"
        st.session_state["tr_last_query"] = {"symbol": sym, "timeframe": timeframe}
        st.info(
            f"Analyse für **{sym}** ({timeframe}) ist vorgemerkt. "
            "Live-Charts und Signale werden als Nächstes angebunden."
        )

    last = st.session_state.get("tr_last_query")
    if isinstance(last, dict) and last.get("symbol"):
        st.caption(
            f"Zuletzt: {last.get('symbol')} · {last.get('timeframe', '—')}"
        )
