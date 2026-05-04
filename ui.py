import streamlit as st

# =============================
# SAFE IMPORTS (kein Crash mehr)
# =============================
try:
    from database import *
except:
    pass

try:
    from auth import login_user, register_user
except:
    pass

try:
    from backend import *
except:
    pass

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="MAB AI",
    layout="wide"
)

# =============================
# SIDEBAR FIX (WICHTIG)
# =============================
st.markdown("""
<style>

/* Sidebar immer anzeigen */
section[data-testid="stSidebar"] {
    display: block !important;
}

/* Toggle Button sichtbar */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    z-index: 999999 !important;
}

/* Header sichtbar */
header {
    display: block !important;
}

/* KEIN VERSTECKEN */
.st-emotion-cache-1cypcdb {
    display: block !important;
}

</style>
""", unsafe_allow_html=True)

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.title("⚡ MAB AI")

    st.markdown("---")

    st.subheader("Account")

    if st.button("User Dashboard"):
        st.session_state["page"] = "dashboard"

    if st.button("Support"):
        st.session_state["page"] = "support"

    if st.button("Buy Premium"):
        st.session_state["page"] = "premium"

    if st.button("Connect"):
        st.session_state["page"] = "connect"

    st.markdown("---")

    st.subheader("Team")

    if st.button("Admin Panel"):
        st.session_state["page"] = "admin"

# =============================
# DEFAULT PAGE
# =============================
if "page" not in st.session_state:
    st.session_state["page"] = "home"

page = st.session_state["page"]

# =============================
# HOME
# =============================
if page == "home":
    st.markdown("""
    <div style="text-align:center; padding-top:60px;">
        <h1>Was kann ich für dich tun?</h1>
        <p>Starte mit Memory Chat. Erstelle Texte, plane Projekte oder lass dir helfen.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.info("Free\n\nMemory Chat inklusive.")

    with col2:
        st.info("Pro\n\nCoding, Bilder, Musik & Video.")

    with col3:
        st.info("Grand\n\nAI Video Generator.")

    with col4:
        st.info("Elite\n\nAlles freigeschaltet.")

# =============================
# DASHBOARD
# =============================
elif page == "dashboard":
    st.title("User Dashboard")
    st.write("Hier kommt dein Dashboard rein.")

# =============================
# SUPPORT
# =============================
elif page == "support":
    st.title("Support")

    username = st.text_input("Username")
    message = st.text_area("Nachricht")

    if st.button("Senden"):
        try:
            add_support_message(username, "general", "Support", message)
            st.success("Nachricht gesendet!")
        except:
            st.error("Support DB noch nicht ready.")

# =============================
# PREMIUM
# =============================
elif page == "premium":
    st.title("Premium Upgrade")
    st.write("Upgrade kommt hier rein.")

# =============================
# CONNECT
# =============================
elif page == "connect":
    st.title("Connect APIs")
    st.write("Hier API Keys später.")

# =============================
# ADMIN
# =============================
elif page == "admin":
    st.title("Admin Panel")

    try:
        users = list_users()
        st.write(users)
    except:
        st.warning("User DB noch nicht vorhanden.")