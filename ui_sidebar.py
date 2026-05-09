import streamlit as st


# =========================================================
# NAVIGATION BUTTON
# =========================================================

def nav_button(label, page, icon=""):
    active = st.session_state.get("page") == page

    button_class = "nav-btn-active" if active else "nav-btn"

    if st.markdown(
        f"""
        <style>
        div.stButton > button[kind="secondary"] {{
            width: 100%;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    ):
        pass

    if st.button(
        f"{icon} {label}",
        use_container_width=True,
        key=f"nav_{page}",
    ):
        st.session_state.page = page
        st.rerun()


# =========================================================
# LOGIN CHECK
# =========================================================

def is_logged_in():
    return bool(st.session_state.get("user"))


def is_admin():
    return (
        st.session_state.get("role") in
        ["supporter", "moderator", "admin", "owner"]
        or int(st.session_state.get("admin_level", 0)) > 0
    )


# =========================================================
# LOGOUT
# =========================================================

def logout():
    st.session_state.user = None
    st.session_state.email = ""
    st.session_state.plan = "free"
    st.session_state.tokens = 0
    st.session_state.role = "user"
    st.session_state.admin_level = 0
    st.session_state.page = "home"

    st.rerun()


# =========================================================
# SIDEBAR UI
# =========================================================

def render_sidebar():

    with st.sidebar:

        # =====================================================
        # CSS
        # =====================================================

        st.markdown("""
        <style>

        section[data-testid="stSidebar"]{
            background:
                linear-gradient(
                    180deg,
                    #050816 0%,
                    #091124 45%,
                    #0c1730 100%
                );
            border-right: 1px solid rgba(0,140,255,0.15);
        }

        .sidebar-logo{
            text-align:center;
            margin-top:10px;
            margin-bottom:25px;
        }

        .sidebar-title{
            text-align:center;
            color:white;
            font-size:28px;
            font-weight:800;
            letter-spacing:2px;
            margin-top:10px;
            margin-bottom:5px;
        }

        .sidebar-sub{
            text-align:center;
            color:#6ea8ff;
            font-size:13px;
            margin-bottom:30px;
        }

        div.stButton > button{
            background:
                linear-gradient(
                    90deg,
                    #0f1729,
                    #12213d
                );

            border:1px solid rgba(80,150,255,0.25);

            color:white;

            border-radius:16px;

            padding:14px 12px;

            font-weight:700;

            transition:0.25s;

            margin-bottom:10px;

            box-shadow:
                0 0 15px rgba(0,140,255,0.08);
        }

        div.stButton > button:hover{
            border:1px solid #4ea1ff;

            transform:translateY(-2px);

            background:
                linear-gradient(
                    90deg,
                    #12213d,
                    #18345c
                );

            box-shadow:
                0 0 25px rgba(0,140,255,0.35);
        }

        .user-card{
            background:
                linear-gradient(
                    180deg,
                    rgba(15,25,45,0.95),
                    rgba(10,16,32,0.95)
                );

            border:1px solid rgba(80,150,255,0.2);

            border-radius:18px;

            padding:18px;

            margin-top:25px;

            color:white;

            box-shadow:
                0 0 25px rgba(0,100,255,0.08);
        }

        .user-name{
            font-size:18px;
            font-weight:800;
            color:white;
        }

        .user-plan{
            color:#73b4ff;
            font-size:14px;
            margin-top:4px;
        }

        .token-box{
            margin-top:12px;

            background:
                rgba(0,120,255,0.08);

            border:
                1px solid rgba(0,120,255,0.15);

            border-radius:12px;

            padding:10px;

            text-align:center;

            color:white;

            font-weight:700;
        }

        .sidebar-divider{
            height:1px;
            width:100%;
            background:
                linear-gradient(
                    90deg,
                    transparent,
                    rgba(0,120,255,0.4),
                    transparent
                );
            margin-top:20px;
            margin-bottom:20px;
        }

        </style>
        """, unsafe_allow_html=True)

        # =====================================================
        # LOGO
        # =====================================================

        st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)

        try:
            st.image("LogoMAIN.png", width=180)
        except:
            st.markdown("""
            <div class="sidebar-title">
                MAB.AI
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="sidebar-sub">
            Next Generation AI Platform
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # =====================================================
        # NAVIGATION
        # =====================================================

        nav_button("Home", "home", "🏠")

        if not is_logged_in():

            nav_button("Login / Register", "login", "🔐")
            nav_button("Premium", "premium", "💎")

        else:

            st.markdown("""
            <div class="sidebar-divider"></div>
            """, unsafe_allow_html=True)

            # =============================================
            # AI TOOLS
            # =============================================

            nav_button("Memory Chat", "chat", "💬")
            nav_button("Coding AI", "coding", "💻")
            nav_button("Image Generator", "image", "🎨")
            nav_button("Music Generator", "music", "🎵")
            nav_button("Video Generator", "video", "🎬")
            nav_button("Reels Creator", "reels", "📱")

            st.markdown("""
            <div class="sidebar-divider"></div>
            """, unsafe_allow_html=True)

            # =============================================
            # ACCOUNT
            # =============================================

            nav_button("Dashboard", "dashboard", "📊")
            nav_button("Support Tickets", "support", "🎫")
            nav_button("Redeem Code", "redeem", "🎁")
            nav_button("Premium", "premium", "💎")

            # =============================================
            # ADMIN
            # =============================================

            if is_admin():

                st.markdown("""
                <div class="sidebar-divider"></div>
                """, unsafe_allow_html=True)

                nav_button("Admin Panel", "admin", "🛡️")

            # =============================================
            # USER CARD
            # =============================================

            st.markdown(f"""
            <div class="user-card">

                <div class="user-name">
                    👤 {st.session_state.get("user")}
                </div>

                <div class="user-plan">
                    Plan:
                    {st.session_state.get("plan", "free").upper()}
                </div>

                <div class="token-box">
                    ⚡ Tokens:
                    {st.session_state.get("tokens", 0)}
                </div>

            </div>
            """, unsafe_allow_html=True)

            # =============================================
            # LOGOUT
            # =============================================

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button(
                "🚪 Logout",
                use_container_width=True,
                key="logout_btn"
            ):
                logout()