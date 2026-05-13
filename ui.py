import streamlit as st

from pages.auth import render_auth
from pages.home import render_home
from pages.chat import render_chat
from pages.projects import render_projects
from pages.dashboard import render_dashboard
from pages.football import render_football
from pages.automation_lab import render_automation_lab

# OPTIONAL
try:
    from pages.image import render_image
except:
    render_image = None

try:
    from pages.video import render_video
except:
    render_video = None

try:
    from pages.reels import render_reels
except:
    render_reels = None

try:
    from pages.music import render_music
except:
    render_music = None

try:
    from pages.coding import render_coding
except:
    render_coding = None

try:
    from pages.premium import render_premium
except:
    render_premium = None


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="MaByte",
    page_icon="🚀",
    layout="wide",
)


# =========================================================
# SESSION
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "auth"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# =========================================================
# GLOBAL CSS
# =========================================================

st.markdown(
    """
<style>

#MainMenu,
header,
footer{
    display:none;
}

.stApp{
    background:
        radial-gradient(circle at top,
        rgba(59,130,246,.08),
        transparent 25%),

        linear-gradient(
            135deg,
            #020617 0%,
            #071427 55%,
            #020617 100%
        );
}

.main .block-container{
    padding-top:1rem;
    padding-bottom:1rem;
    max-width:1320px;
}

section[data-testid="stSidebar"]{

    background:
        linear-gradient(
            180deg,
            #081225 0%,
            #07111f 100%
        );

    border-right:
        1px solid rgba(96,165,250,.10);
}

section[data-testid="stSidebar"] *{
    color:white!important;
}

.sidebar-logo{
    font-size:32px;
    font-weight:900;
    color:white;
    margin-bottom:25px;
}

.sidebar-section{
    color:#64748b;
    font-size:12px;
    text-transform:uppercase;
    margin-top:24px;
    margin-bottom:10px;
    font-weight:800;
    letter-spacing:1px;
}

.stButton > button{

    width:100%;

    border:none!important;

    border-radius:16px!important;

    min-height:48px!important;

    font-weight:800!important;

    background:
        linear-gradient(
            135deg,
            #2563eb,
            #38bdf8
        )!important;

    color:white!important;

    box-shadow:
        0 8px 25px rgba(56,189,248,.18);
}

.sidebar-user{

    background:
        linear-gradient(
            145deg,
            rgba(15,23,42,.92),
            rgba(15,30,60,.65)
        );

    border:
        1px solid rgba(96,165,250,.10);

    border-radius:24px;

    padding:18px;

    margin-top:30px;
}

.sidebar-user-name{
    color:white;
    font-size:18px;
    font-weight:800;
}

.sidebar-user-plan{
    color:#c084fc;
    font-size:13px;
    font-weight:700;
}

.sidebar-user-tokens{
    color:#38bdf8;
    font-size:15px;
    font-weight:800;
    margin-top:8px;
}

</style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# NAVIGATION
# =========================================================

def go(page):
    st.session_state.page = page
    st.rerun()


# =========================================================
# SIDEBAR
# =========================================================

if st.session_state.logged_in:

    with st.sidebar:

        st.markdown(
            """
<div class="sidebar-logo">
🚀 MaByte
</div>
            """,
            unsafe_allow_html=True,
        )

        # =================================================
        # CORE
        # =================================================

        st.markdown(
            '<div class="sidebar-section">Mission Control</div>',
            unsafe_allow_html=True,
        )

        if st.button("🏠 Home"):
            go("home")

        if st.button("💬 AI Assistant"):
            go("chat")

        if st.button("📁 Projects"):
            go("projects")

        if st.button("⚡ Automations"):
            go("automation_lab")

        if st.button("⚽ Football AI"):
            go("football")

        # =================================================
        # MEDIA
        # =================================================

        st.markdown(
            '<div class="sidebar-section">Media Tools</div>',
            unsafe_allow_html=True,
        )

        if render_image:
            if st.button("🎨 Image Generation"):
                go("image")

        if render_video:
            if st.button("🎬 Video Generation"):
                go("video")

        if render_reels:
            if st.button("📣 Reels Maker"):
                go("reels")

        if render_music:
            if st.button("🎵 Music Creator"):
                go("music")

        if render_coding:
            if st.button("💻 Coding Assistant"):
                go("coding")

        # =================================================
        # ACCOUNT
        # =================================================

        st.markdown(
            '<div class="sidebar-section">Account</div>',
            unsafe_allow_html=True,
        )

        if st.button("📊 Dashboard"):
            go("dashboard")

        if render_premium:
            if st.button("💎 Premium"):
                go("premium")

        # =================================================
        # USER CARD
        # =================================================

        user = st.session_state.get(
            "user",
            "User",
        )

        plan = st.session_state.get(
            "plan",
            "Free",
        )

        tokens = st.session_state.get(
            "tokens",
            0,
        )

        st.markdown(
            f"""
<div class="sidebar-user">

<div class="sidebar-user-name">
{user}
</div>

<div class="sidebar-user-plan">
{plan}
</div>

<div class="sidebar-user-tokens">
🪙 {tokens:,} Tokens
</div>

</div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# ROUTER
# =========================================================

page = st.session_state.page

if page == "auth":
    render_auth()

elif page == "home":
    render_home()

elif page == "chat":
    render_chat()

elif page == "projects":
    render_projects()

elif page == "dashboard":
    render_dashboard()

elif page == "football":
    render_football()

elif page == "automation_lab":
    render_automation_lab()

elif page == "image" and render_image:
    render_image()

elif page == "video" and render_video:
    render_video()

elif page == "reels" and render_reels:
    render_reels()

elif page == "music" and render_music:
    render_music()

elif page == "coding" and render_coding:
    render_coding()

elif page == "premium" and render_premium:
    render_premium()

else:
    render_home()