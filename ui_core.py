import streamlit as st


def nav_button(label, page, icon="•"):

    active = st.session_state.get("page") == page

    if active:
        st.markdown(
            f"""
<div style="
background:linear-gradient(135deg,#2563eb,#38bdf8);
padding:14px 18px;
border-radius:16px;
margin-bottom:10px;
font-weight:800;
color:white;
box-shadow:0 0 25px rgba(56,189,248,.25);
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
background:rgba(15,23,42,.55);
padding:14px 18px;
border-radius:16px;
margin-bottom:10px;
font-weight:700;
color:#cbd5e1;
border:1px solid rgba(96,165,250,.08);
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


def render_sidebar():

    with st.sidebar:

        st.markdown(
            """
<div style="
font-size:34px;
font-weight:900;
color:white;
margin-bottom:30px;
">
🚀 MaByte
</div>
            """,
            unsafe_allow_html=True,
        )

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

        if st.session_state.get("role") == "admin":

            st.write("")
            st.caption("SYSTEM")

            nav_button(
                "Admin Panel",
                "admin",
                "🛠️",
            )

        st.write("")
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
background:linear-gradient(
135deg,
rgba(15,23,42,.95),
rgba(30,41,59,.85)
);
border:1px solid rgba(96,165,250,.10);
border-radius:24px;
padding:22px;
margin-top:20px;
">

<div style="
font-size:22px;
font-weight:900;
color:white;
">
{user}
</div>

<div style="
display:inline-block;
margin-top:10px;
padding:6px 12px;
border-radius:999px;
background:linear-gradient(
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

<div style="
margin-top:18px;
color:#38bdf8;
font-size:24px;
font-weight:900;
">
{tokens:,}
</div>

<div style="
color:#94a3b8;
font-size:13px;
">
Tokens verfügbar
</div>

</div>
            """,
            unsafe_allow_html=True,
        )