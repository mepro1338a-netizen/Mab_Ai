import streamlit as st

from database import create_user, verify_login
from ui_helpers import sync_session_user


# =========================================================
# LOGIN
# =========================================================

def do_login(username, password):

    ok, msg, user = verify_login(
        username,
        password,
    )

    if ok and user:

        st.session_state.logged_in = True

        sync_session_user(user)

        st.success("Login erfolgreich")

        st.switch_page("ui.py")

    else:
        st.error(msg)


# =========================================================
# PAGE
# =========================================================

def render_auth():

    st.markdown(
        """
<div style="max-width:1100px;margin:auto;padding-top:40px;">

<div class="glass-card">

<h1 style="
font-size:64px;
font-weight:1000;
margin-bottom:10px;
">
🔐 MaByte Access
</h1>

<p style="
font-size:22px;
color:#cbd5e1;
margin-bottom:40px;
">
Login für Chat, Coding, Media Studio und AI Tools.
</p>

</div>

<div style="height:25px"></div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1])

    with left:

        st.markdown(
            """
<div class="glass-card">

<h2 style="font-size:42px;">
AI Workspace
</h2>

<p style="
font-size:20px;
line-height:1.7;
color:#dbeafe;
">
• 💬 Memory Chat<br><br>
• 💻 Coding AI<br><br>
• 🎬 Reels & Video<br><br>
• 🎵 Music AI<br><br>
• 📊 Dashboard
</p>

</div>
            """,
            unsafe_allow_html=True,
        )

    with right:

        tabs = st.tabs(
            [
                "👤 Login",
                "🧾 Registrierung",
            ]
        )

        with tabs[0]:

            st.markdown("## Willkommen zurück")

            username = st.text_input(
                "Username",
                placeholder="dein username",
            )

            password = st.text_input(
                "Passwort",
                type="password",
                placeholder="dein Passwort",
            )

            if st.button(
                "🚀 Einloggen",
                use_container_width=True,
            ):
                do_login(username, password)

        with tabs[1]:

            st.markdown("## Account erstellen")

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

            if st.button(
                "✨ Registrieren",
                use_container_width=True,
            ):

                ok, msg = create_user(
                    reg_user,
                    reg_email,
                    reg_pw,
                )

                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    st.markdown("</div>", unsafe_allow_html=True)


render_auth()