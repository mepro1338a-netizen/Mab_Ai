import streamlit as st

from ui_core import require_login


require_login()


def render_home():

    st.markdown(
        """
<div style="
padding:40px;
border-radius:30px;
background:linear-gradient(145deg,#071427,#0f2747);
border:1px solid rgba(125,211,252,.15);
box-shadow:0 0 40px rgba(56,189,248,.15);
">

<h1 style="
font-size:58px;
font-weight:1000;
color:white;
margin-bottom:10px;
">
🚀 Willkommen bei MaByte
</h1>

<p style="
font-size:22px;
color:#cbd5e1;
line-height:1.7;
max-width:900px;
">
Dein AI Workspace für Chat, Coding, Content,
Automationen, Ideen und moderne Tools.
</p>

</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.info("💬 Memory Chat")

    with c2:
        st.info("💻 Coding AI")

    with c3:
        st.info("🎬 Reels & Media")

    st.markdown("<br>", unsafe_allow_html=True)

    st.success(
        f"Angemeldet als: {st.session_state.get('user')}"
    )


render_home()