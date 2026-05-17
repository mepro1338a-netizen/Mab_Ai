import streamlit as st

st.set_page_config(
    page_title="MaByte",
    page_icon="🧠",
    layout="wide",
)

# =========================================================
# STYLE
# =========================================================

st.markdown("""
<style>

/* =========================
GLOBAL
========================= */

html, body, [class*="css"]{
    font-family: "Inter", sans-serif;
}

.stApp{
    background:
        radial-gradient(circle at top right, rgba(168,85,247,0.30), transparent 25%),
        radial-gradient(circle at bottom left, rgba(59,130,246,0.20), transparent 30%),
        linear-gradient(180deg,#020617 0%, #031127 45%, #020617 100%);
    color:white;
}

/* REMOVE STREAMLIT STUFF */

header,
#MainMenu,
footer{
    visibility:hidden;
}

.block-container{
    padding-top:0rem;
    padding-bottom:2rem;
    max-width:100%;
}

/* =========================
TOP BAR
========================= */

.mb-top{
    height:96px;
    width:100%;
    background:linear-gradient(90deg,#051937,#0a2457,#111827);
    border-bottom:1px solid rgba(255,255,255,0.06);

    display:flex;
    align-items:center;
    justify-content:center;

    margin-bottom:22px;
}

.mb-top img{
    width:100%;
    max-width:1450px;
    object-fit:cover;
}

/* =========================
LAYOUT
========================= */

[data-testid="column"]:nth-child(1){
    background:linear-gradient(
        180deg,
        rgba(33,6,52,0.96),
        rgba(10,5,33,0.96)
    );

    border-right:1px solid rgba(168,85,247,0.12);

    padding:22px 18px 22px 18px;
    border-radius:0px 24px 24px 0px;

    min-height:92vh;
}

[data-testid="column"]:nth-child(2){
    padding-left:34px;
    padding-right:34px;
}

/* =========================
LOGO
========================= */

.mb-logo{
    width:100%;
    border-radius:24px;
    overflow:hidden;
    margin-bottom:24px;
}

.mb-logo img{
    width:100%;
    border-radius:24px;
}

/* =========================
SIDEBAR BUTTONS
========================= */

.stButton > button{
    width:100%;
    height:68px;

    border-radius:22px;

    background:
        linear-gradient(
            90deg,
            rgba(168,85,247,0.14),
            rgba(10,10,20,0.96)
        );

    border:1px solid rgba(168,85,247,0.22);

    color:#ffffff !important;
    font-size:20px;
    font-weight:700;

    transition:0.25s ease;

    box-shadow:none;
}

.stButton > button:hover{
    transform:translateY(-2px);

    border:1px solid rgba(192,132,252,0.6);

    box-shadow:
        0 0 24px rgba(168,85,247,0.22);

    color:#f5d68a !important;
}

/* =========================
HERO
========================= */

.mb-hero{
    width:100%;

    padding:42px;

    border-radius:34px;

    background:
        radial-gradient(circle at top right, rgba(168,85,247,0.14), transparent 35%),
        linear-gradient(
            180deg,
            rgba(6,15,40,0.96),
            rgba(2,6,23,0.96)
        );

    border:1px solid rgba(255,255,255,0.05);

    margin-bottom:28px;
}

.mb-kicker{
    color:#c084fc;
    font-size:14px;
    font-weight:800;
    letter-spacing:4px;

    margin-bottom:12px;
}

.mb-title{
    font-size:76px;
    line-height:1;

    font-weight:900;

    background:linear-gradient(
        90deg,
        #ffe7a3,
        #ffffff
    );

    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;

    margin-bottom:16px;
}

.mb-sub{
    color:#d6d9e7;
    font-size:28px;
    line-height:1.5;
}

/* =========================
QUICK START
========================= */

.mb-section{
    margin-top:12px;
    margin-bottom:20px;
}

.mb-section-title{
    color:#c084fc;
    font-size:20px;
    font-weight:800;
    letter-spacing:3px;

    margin-bottom:20px;
}

.mb-card{
    min-height:245px;

    padding:28px;

    border-radius:28px;

    background:
        linear-gradient(
            180deg,
            rgba(8,12,36,0.96),
            rgba(5,7,20,0.96)
        );

    border:1px solid rgba(255,255,255,0.05);

    transition:0.25s ease;
}

.mb-card:hover{
    transform:translateY(-5px);

    border:1px solid rgba(168,85,247,0.35);

    box-shadow:
        0 0 32px rgba(168,85,247,0.14);
}

.mb-icon{
    width:62px;
    height:62px;

    border-radius:20px;

    display:flex;
    align-items:center;
    justify-content:center;

    font-size:30px;

    background:
        linear-gradient(
            180deg,
            rgba(168,85,247,0.28),
            rgba(91,33,182,0.18)
        );

    margin-bottom:24px;
}

.mb-card-title{
    font-size:30px;
    font-weight:800;

    color:#ffffff;

    margin-bottom:14px;
}

.mb-card-text{
    font-size:19px;
    line-height:1.6;

    color:#d1d5db;
}

/* =========================
PROMPT
========================= */

.mb-prompt-wrap{
    position:fixed;

    left:50%;
    transform:translateX(-50%);

    bottom:22px;

    width:62%;
    z-index:999;
}

.mb-prompt{
    width:100%;
    height:92px;

    border-radius:32px;

    display:flex;
    align-items:center;
    justify-content:space-between;

    padding:0px 18px 0px 28px;

    background:
        linear-gradient(
            90deg,
            rgba(49,8,82,0.98),
            rgba(20,5,40,0.98)
        );

    border:1px solid rgba(192,132,252,0.34);

    box-shadow:
        0 0 34px rgba(168,85,247,0.26);
}

.mb-prompt-text{
    color:#d8b4fe;
    font-size:26px;
    font-weight:700;
}

.mb-send{
    width:64px;
    height:64px;

    border-radius:22px;

    background:linear-gradient(
        180deg,
        #a855f7,
        #7c3aed
    );

    display:flex;
    align-items:center;
    justify-content:center;

    color:white;
    font-size:34px;
    font-weight:900;
}

/* =========================
RESPONSIVE
========================= */

@media(max-width:1200px){

    .mb-title{
        font-size:58px;
    }

    .mb-sub{
        font-size:22px;
    }

    .mb-prompt-wrap{
        width:90%;
    }
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TOP BAR
# =========================================================

st.markdown("""
<div class="mb-top">
    <img src="https://i.imgur.com/8iR7Y6D.png">
</div>
""", unsafe_allow_html=True)

# =========================================================
# LAYOUT
# =========================================================

left, right = st.columns([1, 3])

# =========================================================
# SIDEBAR
# =========================================================

with left:

    st.markdown("""
    <div class="mb-logo">
        <img src="https://i.imgur.com/Lk0Y6wM.png">
    </div>
    """, unsafe_allow_html=True)

    st.button("🏠  Mission Control", key="nav1")
    st.button("💬  AI Assistant", key="nav2")
    st.button("📁  Projects", key="nav3")
    st.button("⚡  Automations", key="nav4")
    st.button("⚽  Football AI", key="nav5")

    st.markdown("<br>", unsafe_allow_html=True)

    st.button("🖼️  Image Studio", key="nav6")
    st.button("🎬  Video Studio", key="nav7")
    st.button("🎵  Music Studio", key="nav8")
    st.button("💻  Code Studio", key="nav9")

# =========================================================
# MAIN
# =========================================================

with right:

    st.markdown("""
    <div class="mb-hero">
        <div class="mb-kicker">AI OPERATING SYSTEM</div>

        <div class="mb-title">
            MaByte
        </div>

        <div class="mb-sub">
            Strategie. Code. Content. Workflows.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="mb-section">
        <div class="mb-section-title">
            ✦ QUICK START
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="mb-card">
            <div class="mb-icon">📈</div>

            <div class="mb-card-title">
                Social Media
            </div>

            <div class="mb-card-text">
                Erstelle virale Strategien für Instagram,
                TikTok und YouTube.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="mb-card">
            <div class="mb-icon">🚀</div>

            <div class="mb-card-title">
                Marketing
            </div>

            <div class="mb-card-text">
                Baue Kampagnen mit Zielgruppen,
                Hooks und Funnels.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="mb-card">
            <div class="mb-icon">🧠</div>

            <div class="mb-card-title">
                Business Analyse
            </div>

            <div class="mb-card-text">
                Optimiere Prozesse, Umsatz
                und Wachstum.
            </div>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# PROMPT BAR
# =========================================================

st.markdown("""
<div class="mb-prompt-wrap">
    <div class="mb-prompt">

        <div class="mb-prompt-text">
            Frag MaByte...
        </div>

        <div class="mb-send">
            ➜
        </div>

    </div>
</div>
""", unsafe_allow_html=True)