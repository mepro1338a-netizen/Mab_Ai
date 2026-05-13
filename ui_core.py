import streamlit as st


# =========================================================
# GLOBAL CSS
# =========================================================

def load_css():

    st.markdown(
        """
<style>

html,
body,
[class*="css"]{
    font-family: Inter, sans-serif;
}

#MainMenu,
header,
footer{
    display:none;
}

.stApp{
    background:
        radial-gradient(
            circle at top,
            rgba(37,99,235,.12),
            transparent 30%
        ),
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
    max-width:1450px;
}

/* ===================================================== */
/* SIDEBAR */
/* ===================================================== */

section[data-testid="stSidebar"]{

    background:
        linear-gradient(
            180deg,
            #071120 0%,
            #050b16 100%
        );

    border-right:
        1px solid rgba(96,165,250,.10);
}

section[data-testid="stSidebar"] *{
    color:white!important;
}

section[data-testid="stSidebar"] .block-container{
    padding-top:1rem;
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

    transition:.2s ease;
}

.stButton > button:hover{
    transform:translateY(-2px);
    box-shadow:0 0 25px rgba(56,189,248,.25);
}

</style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# NAV BUTTON
# =========================================================

def nav_button(label, page, icon="•"):

    active = st.session_state.get("page") == page

    if active:

        st.markdown(
            f"""
<div style="
background:
linear-gradient(
135deg,
#2563eb,
#38bdf8
);

padding:14px 18px;

border-radius:16px;

margin-bottom:10px;

font-weight:800;

color:white;

box-shadow:
0 0 25px rgba(56,189,248,.25);
">

{icon} {label}

</div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            f"""
<div style="
background:
rgba(15,23,42,.55);

padding:14px 18px;

border-radius:16px;

margin-bottom:10px;

font-weight:700;

color:#cbd5e1;

border:
1px solid rgba(96,165,250,.08);
">

{icon} {label}

</div>
            """,
            unsafe_allow_html=True,
        )

    if st.button(
        label,
        key=f"nav_{page}",
        use_container_width=True,
    ):

        st.session_state.page = page
        st.rerun()


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar():

    with st.sidebar:

        # =================================================
        # LOGO
        # =================================================

        st.markdown(
            """
<div style="
font-size:36px;
font-weight:900;
color:white;
margin-bottom:28px;
letter-spacing:-1px;
">
🚀 MaByte
</div>
            """,
            unsafe_allow_html=True,
        )

        # =================================================
        # MAIN
        # =================================================

        nav_button(
            "Mission Control",
            "home",
            "🏠",
        )

        nav_button(
            "AI Assistant",
            "chat",
            "💬",
        )

        nav_button(
            "Projects",
            "projects",
            "📁",
        )

        nav_button(
            "Automations",
            "automation_lab",
            "⚡",
        )

        nav_button(
            "Football AI",
            "football",
            "⚽",
        )

        # =================================================
        # MEDIA TOOLS
        # =================================================

        st.write("")
        st.caption("MEDIA TOOLS")

        nav_button(
            "Image Generation",
            "image",
            "🎨",
        )

        nav_button(
            "Video Generation",
            "video",
            "🎬",
        )

        nav_button(
            "Reels Maker",
            "reels",
            "📣",
        )

        nav_button(
            "Music Creator",
            "music",
            "🎵",
        )

        nav_button(
            "Coding Assistant",
            "coding",
            "💻",
        )

        # =================================================
        # ACCOUNT
        # =================================================

        st.write("")
        st.caption("ACCOUNT")

        nav_button(
            "Dashboard",
            "dashboard",
            "👤",
        )

        nav_button(
            "Premium",
            "premium",
            "💎",
        )

        nav_button(
            "Redeem Code",
            "redeem",
            "🎁",
        )

        nav_button(
            "Support",
            "support",
            "🛟",
        )

        # =================================================
        # ADMIN
        # =================================================

        if st.session_state.get("role") == "admin":

            st.write("")
            st.caption("SYSTEM")

            nav_button(
                "Admin Panel",
                "admin",
                "🛠️",
            )

        # =================================================
        # USER CARD
        # =================================================

        st.write("")
        st.write("")

        tokens = st.session_state.get(
            "tokens",
            0,
        )

        user = st.session_state.get(
            "user",
            "User",
        )

        plan = st.session_state.get(
            "plan",
            "Free",
        )

        st.markdown(
            f"""
<div style="
background:
linear-gradient(
135deg,
rgba(15,23,42,.95),
rgba(30,41,59,.85)
);

border:
1px solid rgba(96,165,250,.10);

border-radius:24px;

padding:22px;

margin-top:10px;
">

<div style="
display:flex;
align-items:center;
gap:14px;
">

<div style="
width:54px;
height:54px;
border-radius:18px;

background:
linear-gradient(
135deg,
#2563eb,
#7c3aed
);

display:flex;
align-items:center;
justify-content:center;

font-size:22px;
font-weight:900;
color:white;
">

{user[:1].upper()}

</div>

<div>

<div style="
font-size:21px;
font-weight:900;
color:white;
">
{user}
</div>

<div style="
display:inline-block;
margin-top:8px;
padding:5px 12px;
border-radius:999px;

background:
linear-gradient(
135deg,
#7c3aed,
#a855f7
);

font-size:12px;
font-weight:800;
color:white;
">
{plan}
</div>

</div>

</div>

<div style="
margin-top:20px;
">

<div style="
color:#38bdf8;
font-size:30px;
font-weight:900;
">
{tokens:,}
</div>

<div style="
color:#94a3b8;
font-size:13px;
margin-top:2px;
">
Tokens verfügbar
</div>

</div>

</div>
            """,
            unsafe_allow_html=True,
        )