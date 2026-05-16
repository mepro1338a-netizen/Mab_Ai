import random
import streamlit as st

from database import (
    create_user,
    verify_login,
    record_login_event,
)

from security import (
    is_valid_username,
    is_valid_email,
    check_login_rate,
)

from ui_core import sync_session_user


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

    allowed, msg = check_login_rate(username)

    if not allowed:
        st.error(msg)

        try:
            record_login_event(
                username=username,
                ip_address="rate_limited",
                user_agent="blocked",
                success=False,
            )
        except Exception:
            pass

        return

    ok, msg, user = verify_login(username, password)

    ip_address = "unknown"
    user_agent = "streamlit-client"

    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        ctx = get_script_run_ctx()

        if ctx:
            headers = getattr(ctx, "request_headers", {})

            if headers:
                ip_address = headers.get("X-Forwarded-For", "unknown")
                user_agent = headers.get("User-Agent", "streamlit-client")

    except Exception:
        pass

    try:
        record_login_event(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=ok,
        )
    except Exception:
        pass

    if ok and user:
        sync_session_user(user)
        st.session_state.page = "home"
        st.success("Login erfolgreich")
        st.rerun()

    else:
        st.error(msg)


# =========================================================
# REGISTER
# =========================================================

def do_register(username, email, password, captcha):

    result = st.session_state.captcha_a + st.session_state.captcha_b

    if not is_valid_username(username):
        st.error("UngÃ¼ltiger Username")
        return

    if not is_valid_email(email):
        st.error("UngÃ¼ltige Email")
        return

    if len(password) < 6:
        st.error("Passwort zu kurz")
        return

    if captcha != result:
        st.error("Captcha falsch")
        refresh_captcha()
        return

    ok, msg = create_user(
        username=username,
        email=email,
        password=password,
    )

    if ok:
        st.success("Registrierung erfolgreich")
        refresh_captcha()
    else:
        st.error(msg)


# =========================================================
# CSS
# =========================================================

def auth_css():

    st.markdown(
        """
<style>

#MainMenu,
header,
footer,
[data-testid="stToolbar"]{
    display:none!important;
}

.stApp{
    background:
        radial-gradient(circle at 18% 12%, rgba(56,189,248,.20), transparent 28%),
        radial-gradient(circle at 82% 18%, rgba(168,85,247,.18), transparent 30%),
        radial-gradient(circle at 50% 100%, rgba(14,165,233,.10), transparent 34%),
        linear-gradient(135deg,#020617 0%,#061225 48%,#020617 100%)!important;
}

.main .block-container{
    max-width:1280px;
    padding-top:2.2rem;
    padding-bottom:4rem;
}

h1,h2,h3,label{
    color:white!important;
}

p,span{
    color:#cbd5e1!important;
}

.auth-nav{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:42px;
}

.auth-brand{
    display:flex;
    align-items:center;
    gap:12px;
    color:white;
    font-size:26px;
    font-weight:950;
}

.auth-logo{
    width:42px;
    height:42px;
    border-radius:14px;
    background:linear-gradient(135deg,#2563eb,#38bdf8,#a855f7);
    display:flex;
    align-items:center;
    justify-content:center;
    box-shadow:0 0 34px rgba(56,189,248,.35);
}

.auth-pill{
    padding:10px 16px;
    border-radius:999px;
    border:1px solid rgba(125,211,252,.20);
    background:rgba(15,23,42,.55);
    color:#dbeafe;
    font-weight:800;
    font-size:14px;
}

.hero-eyebrow{
    display:inline-block;
    padding:10px 16px;
    border-radius:999px;
    background:rgba(59,130,246,.14);
    border:1px solid rgba(96,165,250,.28);
    color:#93c5fd;
    font-weight:900;
    margin-bottom:18px;
}

.hero-title{
    color:white;
    font-size:66px;
    line-height:1.02;
    font-weight:1000;
    letter-spacing:-.055em;
    margin-bottom:22px;
}

.hero-gradient{
    background:linear-gradient(135deg,#38bdf8,#818cf8,#e879f9);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.hero-sub{
    color:#cbd5e1;
    font-size:20px;
    line-height:1.55;
    max-width:680px;
    font-weight:650;
    margin-bottom:26px;
}

.hero-points{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:12px;
    margin:26px 0 30px 0;
}

.point{
    border:1px solid rgba(125,211,252,.16);
    background:linear-gradient(145deg,rgba(15,23,42,.75),rgba(30,41,90,.42));
    padding:14px 16px;
    border-radius:18px;
    color:#dbeafe;
    font-weight:850;
}

.auth-box{
    background:
        linear-gradient(145deg,rgba(8,19,45,.88),rgba(10,25,55,.76));
    border:1px solid rgba(125,211,252,.18);
    border-radius:30px;
    padding:34px;
    box-shadow:
        0 24px 80px rgba(0,0,0,.32),
        inset 0 1px 0 rgba(255,255,255,.05);
}

.login-box{
    position:sticky;
    top:24px;
}

.feature-grid{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:16px;
    margin-top:40px;
}

.feature-card{
    min-height:150px;
    border:1px solid rgba(125,211,252,.16);
    background:
        linear-gradient(145deg,rgba(15,23,42,.82),rgba(7,27,58,.54));
    border-radius:24px;
    padding:22px;
    box-shadow:0 18px 45px rgba(0,0,0,.20);
}

.feature-icon{
    font-size:30px;
    margin-bottom:14px;
}

.feature-title{
    color:white;
    font-size:18px;
    font-weight:950;
    margin-bottom:8px;
}

.feature-text{
    color:#9fb3d1;
    font-size:14px;
    line-height:1.45;
    font-weight:650;
}

.pricing-grid{
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:18px;
    margin-top:22px;
}

.price-card{
    border:1px solid rgba(125,211,252,.16);
    background:
        linear-gradient(145deg,rgba(8,19,45,.90),rgba(15,23,42,.72));
    border-radius:26px;
    padding:26px;
}

.price-card.highlight{
    border-color:rgba(168,85,247,.55);
    box-shadow:0 0 40px rgba(168,85,247,.18);
}

.price-title{
    color:white;
    font-size:23px;
    font-weight:950;
}

.price{
    color:white;
    font-size:38px;
    font-weight:1000;
    margin:14px 0;
}

.price-sub{
    color:#93a4bd;
    font-size:14px;
    margin-bottom:18px;
}

.price-feature{
    color:#dbeafe;
    margin:9px 0;
    font-weight:750;
}

.section-title{
    color:white;
    font-size:36px;
    font-weight:1000;
    margin-top:54px;
    margin-bottom:10px;
}

.section-sub{
    color:#9fb3d1;
    font-size:17px;
    margin-bottom:24px;
}

.stTextInput input,
.stNumberInput input{
    background:rgba(2,6,23,.92)!important;
    border:1px solid rgba(96,165,250,.30)!important;
    color:white!important;
    -webkit-text-fill-color:white!important;
    border-radius:16px!important;
    min-height:52px!important;
    font-weight:750!important;
}

.stButton > button{
    min-height:52px!important;
    border-radius:16px!important;
    border:1px solid rgba(96,165,250,.26)!important;
    background:linear-gradient(135deg,#2563eb,#38bdf8)!important;
    color:white!important;
    font-weight:950!important;
    box-shadow:0 0 28px rgba(56,189,248,.24);
}

.stButton > button:hover{
    transform:translateY(-1px);
    box-shadow:0 0 36px rgba(56,189,248,.34);
}

[data-testid="stTabs"] button{
    color:#dbeafe!important;
    font-weight:850!important;
}

@media(max-width:900px){
    .hero-title{
        font-size:44px;
    }

    .hero-points,
    .feature-grid,
    .pricing-grid{
        grid-template-columns:1fr;
    }

    .auth-nav{
        flex-direction:column;
        align-items:flex-start;
        gap:14px;
    }
}

</style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# PAGE
# =========================================================

def render_auth():

    ensure_captcha()
    auth_css()

    st.markdown(
        """
<div class="auth-nav">
    <div class="auth-brand">
        <div class="auth-logo">M</div>
        <div>MaByte</div>
    </div>
    <div class="auth-pill">AI Creator Operating System</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.35, .85], gap="large")

    with left:

        st.markdown(
            """
<div class="hero-eyebrow">ðŸš€ Built for creators, brands, agencies and football media teams</div>

<div class="hero-title">
Create viral content with <span class="hero-gradient">AI workflows</span>.
</div>

<div class="hero-sub">
MaByte is the AI Creator Operating System for social media growth.
Generate hooks, reels, captions, thumbnails, threads, automation flows and creator-ready content packages in seconds.
</div>

<div class="hero-points">
    <div class="point">âš½ Football Intelligence</div>
    <div class="point">ðŸ“£ Multi-Platform Content</div>
    <div class="point">ðŸ”¥ Viral Score Engine</div>
    <div class="point">ðŸ§ª AI Automation Lab</div>
    <div class="point">ðŸ–¼ï¸ Thumbnail Intelligence</div>
    <div class="point">ðŸ§  Project Memory</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    with right:

        st.markdown('<div class="auth-box login-box">', unsafe_allow_html=True)

        st.markdown("### ðŸ” Access MaByte")
        st.caption("Login or create your creator workspace.")

        tab1, tab2 = st.tabs(["ðŸ‘¤ Login", "âœ¨ Start Free"])

        with tab1:

            username = st.text_input(
                "Username",
                placeholder="dein username",
                key="login_user",
            )

            password = st.text_input(
                "Passwort",
                type="password",
                placeholder="dein Passwort",
                key="login_pw",
            )

            if st.button("ðŸš€ Einloggen", width="stretch"):
                do_login(username, password)

            st.caption("Google Login wird spÃ¤ter verbunden.")

        with tab2:

            reg_user = st.text_input(
                "Username",
                key="reg_user",
            )

            reg_email = st.text_input(
                "Email",
                key="reg_email",
            )

            reg_pw = st.text_input(
                "Passwort",
                type="password",
                key="reg_pw",
            )

            captcha = st.number_input(
                f"{st.session_state.captcha_a} + {st.session_state.captcha_b}",
                min_value=0,
                max_value=20,
                step=1,
            )

            if st.button("âœ¨ Kostenlos starten", width="stretch"):
                do_register(
                    reg_user,
                    reg_email,
                    reg_pw,
                    captcha,
                )

        st.markdown("</div>", unsafe_allow_html=True)


