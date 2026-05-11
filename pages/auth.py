import random
import streamlit as st

from database import create_user, verify_login
from security import is_valid_username, is_valid_email, check_login_rate
from ui_core import sync_session_user


# =========================================================
# SETTINGS
# =========================================================

st.set_page_config(
    page_title="MaByte Access",
    page_icon="🔐",
    layout="wide",
)

st.markdown(
    """
<style>

/* SIDEBAR AUSBLENDEN */
[data-testid="stSidebar"]{
    display:none;
}

[data-testid="collapsedControl"]{
    display:none;
}

header{
    display:none;
}

/* APP */
.main .block-container{
    max-width:1200px;
    padding-top:2rem;
}

/* BACKGROUND */
.stApp{
    background:
        radial-gradient(circle at top left,
        rgba(59,130,246,.16),
        transparent 30%),

        radial-gradient(circle at top right,
        rgba(14,165,233,.12),
        transparent 25%),

        linear-gradient(
            135deg,
            #020617 0%,
            #081225 40%,
            #0f172a 100%
        );

    color:white;
}

/* HERO */
.hero-wrap{
    text-align:center;
    margin-bottom:40px;
}

.hero-icon{
    font-size:72px;
    margin-bottom:8px;
}

.hero-title{
    font-size:72px;
    font-weight:1000;
    color:white;
    margin-bottom:10px;

    text-shadow:
        0 0 35px rgba(56,189,248,.25);
}

.hero-sub{
    color:#cbd5e1;
    font-size:22px;
    font-weight:700;
}

/* GLASS */
.glass-card{
    padding:38px;
    border-radius:34px;

    background:
        linear-gradient(
            145deg,
            rgba(10,20,40,.92),
            rgba(15,23,42,.82)
        );

    border:
        1px solid rgba(96,165,250,.20);

    box-shadow:
        0 0 55px rgba(37,99,235,.12);

    backdrop-filter: blur(16px);
}

/* LEFT */
.feature-title{
    font-size:48px;
    font-weight:1000;
    line-height:1.1;
    margin-bottom:20px;
}

.feature-text{
    color:#dbeafe;
    font-size:20px;
    line-height:1.8;
    font-weight:700;
    margin-bottom:28px;
}

.feature-box{
    padding:18px;
    border-radius:18px;

    background:
        rgba(15,23,42,.75);

    border:
        1px solid rgba(96,165,250,.18);

    margin-bottom:16px;

    font-size:17px;
    font-weight:850;
}

/* TABS */
.stTabs [data-baseweb="tab-list"]{
    gap:14px;
}

.stTabs [data-baseweb="tab"]{
    flex:1;

    justify-content:center;

    min-height:58px;

    border-radius:18px;

    background:
        rgba(15,23,42,.55);

    color:white;

    font-size:17px;
    font-weight:850;
}

/* INPUTS */
.stTextInput input,
.stNumberInput input{

    min-height:60px !important;

    border-radius:18px !important;

    background:
        rgba(2,6,23,.90) !important;

    color:white !important;

    border:
        1px solid rgba(125,211,252,.28) !important;

    font-size:17px !important;
    font-weight:700 !important;
}

.stTextInput input:focus,
.stNumberInput input:focus{

    border:
        1px solid #38bdf8 !important;

    box-shadow:
        0 0 15px rgba(56,189,248,.30);
}

/* BUTTON */
.stFormSubmitButton button{

    min-height:64px !important;

    border-radius:20px !important;

    border:none !important;

    background:
        linear-gradient(
            135deg,
            #2563eb,
            #22d3ee
        ) !important;

    color:white !important;

    font-size:20px !important;
    font-weight:900 !important;

    transition:.25s ease;
}

.stFormSubmitButton button:hover{

    transform:translateY(-2px);

    box-shadow:
        0 0 25px rgba(56,189,248,.35);
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# CAPTCHA
# =========================================================

def refresh_captcha():
    st.session_state.captcha_a = random.randint(1, 5)
    st.session_state.captcha_b = random.randint(1, 5)


def ensure_captcha():
    if "captcha_a" not in st.session_state:
        refresh_captcha()


# =========================================================
# LOGIN
# =========================================================

def do_login(username, password):

    allowed, rate_msg = check_login_rate(username)

    if not allowed:
        st.error(rate_msg)
        return

    ok, msg, user = verify_login(username, password)

    if ok and user:

        st.session_state.logged_in = True

        sync_session_user(user)

        st.session_state.page = "home"

        st.success(msg)

        st.rerun()

    else:
        st.error(msg)


# =========================================================
# REGISTER
# =========================================================

def do_register(username, email, password, captcha):

    result = (
        st.session_state.captcha_a
        + st.session_state.captcha_b
    )

    if not is_valid_username(username):
        st.error("Username ungültig.")
        return

    if not is_valid_email(email):
        st.error("Ungültige Email.")
        return

    if len(password or "") < 6:
        st.error("Mindestens 6 Zeichen.")
        return

    if captcha != result:
        st.error("Captcha falsch.")
        refresh_captcha()
        st.rerun()

    ok, msg = create_user(
        username=username,
        email=email,
        password=password,
        role="user",
        plan="free",
    )

    if ok:
        st.success("Account erstellt.")
        refresh_captcha()

    else:
        st.error(msg)


# =========================================================
# LOGIN TAB
# =========================================================

def render_login_tab():

    with st.form("login_form"):

        st.subheader("👋 Willkommen zurück")

        st.caption(
            "Öffne dein MaByte Control Center."
        )

        username = st.text_input(
            "Username",
            placeholder="dein username",
        )

        password = st.text_input(
            "Passwort",
            type="password",
            placeholder="dein Passwort",
        )

        submitted = st.form_submit_button(
            "🚀 Einloggen",
            use_container_width=True,
        )

        if submitted:
            do_login(username, password)


# =========================================================
# REGISTER TAB
# =========================================================

def render_register_tab():

    with st.form("register_form"):

        st.subheader("✨ Registrierung")

        st.caption(
            "Starte kostenlos mit MaByte."
        )

        username = st.text_input(
            "Username",
            placeholder="3-40 Zeichen",
        )

        email = st.text_input(
            "Email",
            placeholder="deine@email.de",
        )

        password = st.text_input(
            "Passwort",
            type="password",
            placeholder="mindestens 6 Zeichen",
        )

        captcha = st.number_input(
            f"{st.session_state.captcha_a} + {st.session_state.captcha_b}",
            min_value=0,
            max_value=10,
            step=1,
        )

        submitted = st.form_submit_button(
            "✨ Account erstellen",
            use_container_width=True,
        )

        if submitted:
            do_register(
                username,
                email,
                password,
                captcha,
            )


# =========================================================
# MAIN
# =========================================================

def render_auth():

    ensure_captcha()

    st.markdown(
        """
<div class="hero-wrap">

    <div class="hero-icon">
        🔐
    </div>

    <div class="hero-title">
        MaByte Access
    </div>

    <div class="hero-sub">
        Dein Login für Chat, Coding,
        Media Studio und AI Automation.
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(
        [1, 1.05],
        gap="large",
    )

    # LEFT
    with left:

        st.markdown(
            """
<div class="glass-card">

<div class="feature-title">
Alles in einem<br>
AI Workspace
</div>

<div class="feature-text">
MaByte verbindet Chat,
Coding, Content,
Reels, Video-Ideen
und moderne AI Workflows
in einer Plattform.
</div>

<div class="feature-box">
💬 Memory Chat
</div>

<div class="feature-box">
💻 Coding AI
</div>

<div class="feature-box">
🎬 Reels & Video Studio
</div>

<div class="feature-box">
🎵 Music AI
</div>

<div class="feature-box">
📊 Dashboard & Premium
</div>

</div>
            """,
            unsafe_allow_html=True,
        )

    # RIGHT
    with right:

        st.markdown(
            '<div class="glass-card">',
            unsafe_allow_html=True,
        )

        tab1, tab2 = st.tabs(
            [
                "👤 Login",
                "👥 Registrierung",
            ]
        )

        with tab1:
            render_login_tab()

        with tab2:
            render_register_tab()

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


render_auth()