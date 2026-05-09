import base64
import os
import streamlit as st


def img_base64(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_home():
    header = img_base64("Header.png")

    if header:
        bg = f"""
        background:
            linear-gradient(90deg, rgba(2,6,23,.92), rgba(2,6,23,.55)),
            url("data:image/png;base64,{header}");
        background-size: cover;
        background-position: center;
        """
    else:
        bg = """
        background:
            radial-gradient(circle at top left, rgba(59,130,246,.35), transparent 35%),
            radial-gradient(circle at bottom right, rgba(14,165,233,.22), transparent 35%),
            linear-gradient(135deg, #020617, #07152f);
        """

    st.markdown(f"""
<div class="mabyte-hero" style='{bg}'>
  <div class="mabyte-hero-content">
    <span class="badge">MABYTE</span>
    <h1>Willkommen bei MABYTE</h1>
    <h2>MABYTE ist mehr als nur eine AI.</h2>

    <p>
      Es ist dein persönlicher Begleiter für Ideen, Projekte und Visionen.
      Eine Unterstützung, die mitdenkt, dich inspiriert und dir hilft,
      deine Gedanken zu realisieren.
    </p>

    <p>
      Egal ob du programmierst, ein Business aufbaust, Content erschaffst
      oder neue Möglichkeiten entdecken willst: MABYTE begleitet dich auf deinem Weg.
    </p>

    <h3>Schneller. Kreativer. Grenzenloser.</h3>

    <p>
      Denn die Zukunft entsteht nicht irgendwann.<br>
      Sie entsteht genau jetzt — mit dir.
    </p>

    <div class="mabyte-claim">MABYTE — BEYOND LIMITS.</div>
  </div>
</div>
""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
<div class="feature-card">
  <h3>💬 Smart Chat</h3>
  <p>Chatte mit deiner AI und speichere deinen Verlauf.</p>
</div>
""", unsafe_allow_html=True)

    with c2:
        st.markdown("""
<div class="feature-card">
  <h3>🎬 AI Media</h3>
  <p>Bilder, Videos, Musik und kreative Assets erstellen.</p>
</div>
""", unsafe_allow_html=True)

    with c3:
        st.markdown("""
<div class="feature-card">
  <h3>🚀 Creator Tools</h3>
  <p>Reels Creator, Scheduler und Automation Tools.</p>
</div>
""", unsafe_allow_html=True)