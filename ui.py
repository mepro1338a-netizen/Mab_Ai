import streamlit as st
from PIL import Image

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="MABYTE",
    page_icon="🚀",
    layout="wide",
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>

/* GLOBAL */

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: radial-gradient(circle at top, #101a3a 0%, #050816 55%);
    color: white;
}

/* MAIN */

.main .block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1600px;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: rgba(8,12,28,0.95);
    border-right: 1px solid rgba(80,140,255,0.15);
}

.sidebar-logo {
    text-align:center;
    margin-bottom:20px;
}

.sidebar-title {
    color:white;
    font-size:15px;
    font-weight:700;
    margin-top:10px;
    margin-bottom:20px;
    opacity:0.8;
}

/* HERO */

.hero-badge {
    display:inline-block;
    padding:10px 24px;
    border-radius:30px;
    background:rgba(70,120,255,0.15);
    border:1px solid rgba(100,160,255,0.35);
    color:#6eb6ff;
    font-weight:700;
    font-size:14px;
    letter-spacing:1px;
    margin-bottom:30px;
    box-shadow:0 0 20px rgba(80,140,255,0.25);
}

.hero-title {
    font-size:78px;
    font-weight:900;
    line-height:1;
    margin-bottom:10px;
    color:white;
    text-shadow:0 0 30px rgba(120,170,255,0.35);
}

.hero-sub {
    font-size:34px;
    color:#8bb8ff;
    font-weight:700;
    margin-bottom:25px;
}

.hero-text {
    font-size:22px;
    line-height:1.7;
    color:#d8e3ff;
    max-width:900px;
}

.claim {
    font-size:54px;
    font-weight:900;
    margin-top:40px;
    color:white;
    text-shadow:0 0 30px rgba(120,170,255,0.25);
}

/* FEATURE CARDS */

.card {
    background:linear-gradient(180deg, rgba(15,25,55,0.95), rgba(8,12,28,0.98));
    border:1px solid rgba(100,160,255,0.15);
    border-radius:30px;
    padding:35px;
    min-height:320px;
    transition:0.3s;
    box-shadow:0 0 35px rgba(0,0,0,0.45);
}

.card:hover {
    transform:translateY(-8px);
    border:1px solid rgba(120,180,255,0.45);
    box-shadow:0 0 40px rgba(70,120,255,0.25);
}

.card-icon {
    font-size:54px;
    margin-bottom:20px;
}

.card-title {
    font-size:42px;
    font-weight:800;
    margin-bottom:20px;
}

.card-text {
    font-size:24px;
    line-height:1.6;
    color:#dce7ff;
}

/* BUTTONS */

.stButton > button {
    width:100%;
    background:linear-gradient(90deg,#4f8cff,#67b8ff);
    border:none;
    border-radius:18px;
    color:white;
    font-weight:700;
    font-size:18px;
    padding:16px;
    transition:0.3s;
    box-shadow:0 0 25px rgba(70,120,255,0.3);
}

.stButton > button:hover {
    transform:translateY(-2px);
    box-shadow:0 0 35px rgba(70,120,255,0.5);
}

/* REMOVE STREAMLIT */

#MainMenu {
    visibility:hidden;
}

footer {
    visibility:hidden;
}

header {
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    try:
        logo = Image.open("logoMAIN.png")
        st.image(logo, use_container_width=True)
    except:
        st.warning("logoMAIN.png fehlt")

    st.markdown("""
    <div class='sidebar-title'>
        Next Generation AI Platform
    </div>
    """, unsafe_allow_html=True)

    st.button("🏠 Home")
    st.button("💬 Memory Chat")
    st.button("💻 Coding AI")
    st.button("🎨 Image Generator")
    st.button("🎵 Music Generator")
    st.button("🎬 Reels Creator")
    st.button("📹 Video Generator")

# =========================
# HERO SECTION
# =========================

col_left, col_right = st.columns([1.5, 1])

with col_left:

    st.markdown("""
    <div class='hero-badge'>
        NEXT GENERATION AI PLATFORM
    </div>
    """, unsafe_allow_html=True)

    try:
        header = Image.open("Header.png")
        st.image(header, width=700)
    except:
        st.warning("Header.png fehlt")

    st.markdown("""
    <div class='hero-sub'>
        Die neue Generation von AI Plattformen.
    </div>

    <div class='hero-text'>
        Dein persönlicher Begleiter für Ideen, Projekte und Visionen.
        MABYTE denkt mit, inspiriert dich und hilft dir,
        Gedanken in echte Ergebnisse zu verwandeln.
    </div>

    <div class='claim'>
        MABYTE — BEYOND LIMITS.
    </div>
    """, unsafe_allow_html=True)

with col_right:

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.success("24/7 AI Tools")
    st.success("PRO Creator Workflow")
    st.success("Ideas to Reality")

# =========================
# FEATURE CARDS
# =========================

st.markdown("<br><br>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class='card'>
        <div class='card-icon'>💬</div>

        <div class='card-title'>
            Smart Chat
        </div>

        <div class='card-text'>
            Chatte mit deiner AI und speichere deinen Verlauf.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class='card'>
        <div class='card-icon'>🎬</div>

        <div class='card-title'>
            AI Media
        </div>

        <div class='card-text'>
            Bilder, Videos, Musik und kreative Assets erstellen.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class='card'>
        <div class='card-icon'>🚀</div>

        <div class='card-title'>
            Creator Tools
        </div>

        <div class='card-text'>
            Reels Creator, Scheduler und Automation Tools.
        </div>
    </div>
    """, unsafe_allow_html=True)