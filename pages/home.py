import textwrap
import streamlit as st


def render_home():
    html = """
<section class="hero-box">
  <div class="hero-title">Hallo willkommen auf MAB.AI</div>
  <div class="hero-subtitle">
    Die neue AI für Social Media, Business, Coding und Content Creation.
  </div>
  <div class="hero-subtitle">
    Starte mit Memory Chat, erstelle Bilder, generiere Videos,
    plane Projekte und baue digitale Workflows mit künstlicher Intelligenz.
  </div>
</section>

<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:22px;margin-top:34px;">
  <div class="page-card">
    <h2>Free</h2>
    <p>Memory Chat inklusive. Perfekt zum Starten, Planen und Schreiben.</p>
  </div>

  <div class="page-card">
    <h2>Pro</h2>
    <p>1200 Tokens<br>Coding, Images, Musik & Reels.</p>
  </div>

  <div class="page-card">
    <h2>Grand</h2>
    <p>4000 Tokens<br>AI Video Generator und stärkere Workflows.</p>
  </div>

  <div class="page-card">
    <h2>Elite</h2>
    <p>Alles freigeschaltet.<br>Höchste API-Leistung.</p>
  </div>
</div>
"""
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)