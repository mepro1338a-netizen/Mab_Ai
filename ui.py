import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="MAB.AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "logo.png"

components.html("""
<script>
setTimeout(() => {
  const btn = window.parent.document.querySelector('[data-testid="collapsedControl"]');
  if (btn) btn.click();
}, 300);
</script>
""", height=0)

st.markdown("""
<style>
html, body, .stApp {
    background:#000 !important;
    color:#fff !important;
}

header {
    display:block !important;
    visibility:visible !important;
}

[data-testid="stSidebar"] {
    background:#07070b !important;
    border-right:1px solid rgba(255,215,0,.25) !important;
}

[data-testid="stSidebar"] * {
    color:#fff !important;
}

[data-testid="collapsedControl"] {
    display:flex !important;
    visibility:visible !important;
    opacity:1 !important;
    pointer-events:auto !important;
    z-index:999999 !important;
}

.block-container {
    max-width:1200px !important;
    padding-top:2rem !important;
}

.sidebar-logo {
    text-align:center;
    margin-bottom:20px;
}

.hero {
    background:linear-gradient(135deg,#06364d,#3b0b55);
    border:1px solid rgba(255,255,255,.12);
    border-radius:34px;
    padding:55px;
    margin-top:30px;
}

.hero h1 {
    font-size:64px;
    line-height:1;
    font-weight:900;
    color:white !important;
}

.hero p {
    font-size:20px;
    color:#e5e7eb !important;
}

.card {
    background:#11111a;
    border:1px solid rgba(255,255,255,.1);
    border-radius:22px;
    padding:24px;
    min-height:130px;
}

.stButton button {
    width:100%;
    background:#000 !important;
    color:#ffd700 !important;
    border:1px solid rgba(255,215,0,.55) !important;
    border-radius:14px !important;
    min-height:46px;
    font-weight:800;
}

.stButton button:hover {
    border-color:#ffd700 !important;
}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "home"

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    else:
        st.title("MAB.AI")

    st.markdown("---")
    st.markdown("### Account")

    if st.button("Memory Chat"):
        st.session_state.page = "home"
    if st.button("User Dashboard"):
        st.session_state.page = "dashboard"
    if st.button("Support"):
        st.session_state.page = "support"
    if st.button("Buy Premium"):
        st.session_state.page = "premium"
    if st.button("Connect with"):
        st.session_state.page = "connect"

    st.markdown("---")
    st.markdown("### Team")

    if st.button("Admin Panel"):
        st.session_state.page = "admin"

page = st.session_state.page

if page == "home":
    st.markdown("""
    <section class="hero">
        <h1>Was kann ich für dich tun?</h1>
        <p>Starte mit Memory Chat. Erstelle Texte, plane Projekte, sammle Ideen oder lass dir direkt helfen.</p>
    </section>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown('<div class="card"><h3>Free</h3><p>Memory Chat inklusive.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><h3>Pro</h3><p>Coding, Bilder, Musik und Video-Reels.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card"><h3>Grand</h3><p>AI Video Generator.</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="card"><h3>Elite</h3><p>Alles freigeschaltet.</p></div>', unsafe_allow_html=True)

elif page == "dashboard":
    st.title("📊 User Dashboard")
    st.info("Dashboard kommt hier rein.")

elif page == "support":
    st.title("🆘 Support")
    st.text_input("Betreff")
    st.text_area("Nachricht")
    st.button("Senden")

elif page == "premium":
    st.title("💳 Buy Premium")
    st.info("Premium-Pläne kommen hier rein.")

elif page == "connect":
    st.title("🔗 Connect with")
    st.info("API-Verbindungen kommen hier rein.")

elif page == "admin":
    st.title("🛡️ Admin Panel")
    st.info("Admin Bereich kommt hier rein.")